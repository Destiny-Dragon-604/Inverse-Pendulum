import smbus
import time
import pyodrivecan
import asyncio
import math

# Initialize SMBus for I2C communication
bus = smbus.SMBus(1)

# AS5048A default I2C address and register
AS5048A_ADDR = 0x40
AS5048A_ANGLE_REG = 0xFE

# Function to read raw angle from the encoder
def read_raw_angle():
    data = bus.read_i2c_block_data(AS5048A_ADDR, AS5048A_ANGLE_REG, 2)
    return data[0] * 256 + data[1]

# Function to convert raw angle to degrees
def raw_to_degrees(raw_angle):
    degrees = ((raw_angle / 16383.0) * 360) / 8
    return round((degrees + 90) % 360, 2)

# Initialize encoder variables
last_angle_raw = read_raw_angle()
total_rotations = 0
rest_position = raw_to_degrees(last_angle_raw)
error_tolerance = 0.02
stable_duration = 3
stable_count = 0
reading_interval = 0.01
stable_count_threshold = stable_duration / reading_interval

def read_angle():
    global last_angle_raw, total_rotations, rest_position, stable_count

    # Read the current raw angle
    current_angle_raw = read_raw_angle()
    
    # Convert to degrees
    current_angle = raw_to_degrees(current_angle_raw)
    
    # Calculate change in angle
    change_in_angle_raw = current_angle_raw - last_angle_raw
    
    # Update the last angle
    last_angle_raw = current_angle_raw
    
    # Check for wrap around
    if change_in_angle_raw > 8191:
        total_rotations += 1
    elif change_in_angle_raw < -8191:
        total_rotations -= 1
    
    # Calculate the total angle considering rotations
    total_angle = round((total_rotations * 180 + current_angle - rest_position) % 360, 2)
    
    # Check for stability and recalibrate if necessary
    if abs(total_angle) < error_tolerance:
        stable_count += 1
        if stable_count >= stable_count_threshold:
            rest_position = current_angle
            stable_count = 0
            print(f"Recalibrated rest position to: {rest_position:.2f} degrees")
        total_angle = 0
    else:
        stable_count = 0
    
    return total_angle

async def initial_velocity_oscillation(odrive, trial_id, tuning_factor=0.0003):
    """
    Initial velocity oscillation to build initial motion dynamics.
    """
    try:
        print(f"Using trial_id: {trial_id}")

        # Loop 10 times
        for i in range(4):
            # Calculate the adjusted delay using a logarithmic function
            delay = max(0.1, 0.5 - tuning_factor * math.log(i + 1))

            # Set velocity to -5000 counts per second
            odrive.set_velocity(-5000)
            await asyncio.sleep(delay)  # Wait for the dynamically calculated delay

            # Set velocity to 5000 counts per second
            odrive.set_velocity(5000)
            await asyncio.sleep(delay)  # Wait for the dynamically calculated delay
        
        for i in range(1):
            # Calculate the adjusted delay using a logarithmic function
            delay = 0.653

            # Set velocity to -5000 counts per second
            odrive.set_velocity(-5000)
            await asyncio.sleep(delay)  # Wait for the dynamically calculated delay

            # Set velocity to 5000 counts per second
            odrive.set_velocity(5000)
            await asyncio.sleep(delay)  # Wait for the dynamically calculated delay

        # Set velocity to 0 counts per second after the loop ends
        odrive.set_velocity(0)

        # Immediately start PID control after initial oscillation
        await pid_control_oscillation(odrive)
        
    finally:
        # Set running flag to False to stop further operations
        odrive.running = False

async def pid_control_oscillation(odrive, max_target_position=180, kp=0.1, ki=0.02, kd=0.05, damping=0.1, max_velocity=10000):
    """
    Enhanced PID-based oscillation control with damping after initial dynamics.
    """
    integral = 0
    previous_error = 0

    try:
        # Initialize oscillation parameters
        current_amplitude = 45  # Start with a small amplitude (45 degrees)
        amplitude_step = 15     # Increase amplitude by 15 degrees on each oscillation
        max_amplitude = max_target_position  # Maximum amplitude to reach is 180 degrees
        direction = 1           # Initial direction

        while True:
            # Set the target positions based on the current amplitude
            target_position = current_amplitude if direction > 0 else (360 - current_amplitude)
            print(f"Current Target Position: {target_position:.2f} degrees")

            # Oscillate to target position and build momentum
            start_time = time.time()
            while True:
                # Read the current angle from the encoder
                angle = read_angle()
                print(f"Current Angle: {angle:.2f} degrees")

                # Calculate PID error terms
                error = target_position - angle
                integral += error * reading_interval
                derivative = (error - previous_error) / reading_interval
                previous_error = error

                # Get current velocity asynchronously
                current_velocity = await odrive.get_velocity()  # Await the coroutine

                # PID control output with damping
                velocity_command = kp * error + ki * integral + kd * derivative - damping * current_velocity
                velocity_command = max(min(velocity_command, max_velocity), -max_velocity)  # Constrain velocity
                odrive.set_velocity(velocity_command)

                # Check if the current angle is within a small range of the target position
                if abs(angle - target_position) < 2:  # Close enough to the target
                    print(f"Reached target position: {target_position:.2f} degrees")
                    break

                # Allow more time to build momentum by waiting longer in each direction
                if time.time() - start_time > 4:  # Stay in one direction for 4 seconds
                    break

                await asyncio.sleep(reading_interval)

            # Switch direction for the next oscillation
            direction *= -1

            # Increase the amplitude for the next swing
            if current_amplitude < max_amplitude:
                current_amplitude += amplitude_step
                print(f"Increasing amplitude to: {current_amplitude} degrees")
            else:
                # Once max amplitude is reached, maintain 180-degree target
                print("Reached maximum amplitude. Continuing to maintain 180 degrees.")
                current_amplitude = max_amplitude

    finally:
        # Stop the motor
        odrive.set_velocity(0)
        odrive.running = False

async def main():
    trial_id = 1

    # Create and initialize ODriveCAN object
    odrive = pyodrivecan.ODriveCAN(0)
    odrive.clear_errors()
    
    try:
        odrive.initCanBus()
        odrive.set_controller_mode("velocity_control")

        # Calibration delay for 5 seconds to set initial rest position
        print("Calibrating initial rest position. Please wait...")
        await asyncio.sleep(5)
        global rest_position
        rest_position = raw_to_degrees(read_raw_angle())  # Set the initial rest position after 5 seconds
        print(f"Initial rest position calibrated to: {rest_position:.2f} degrees.")

        # Run initial velocity oscillation to build initial dynamics
        await initial_velocity_oscillation(odrive, trial_id)

    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        print("Cleanup (if necessary)")
        bus.close()

if __name__ == "__main__":
    asyncio.run(main())
