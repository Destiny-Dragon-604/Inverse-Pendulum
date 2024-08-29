import smbus
import time
from simple_pid import PID
import pyodrivecan
import asyncio
import math
from advanced_pid import PID
from advanced_pid.models import MassSpringDamper
from matplotlib import pyplot as plt
from numpy import diff


# Create an SMBus instance
bus = smbus.SMBus(1)

# AS5048A default address
AS5048A_ADDR = 0x40

# AS5048A Register
AS5048A_ANGLE_REG = 0xFE

# Function to read raw angle from the encoder
def read_raw_angle():
    data = bus.read_i2c_block_data(AS5048A_ADDR, AS5048A_ANGLE_REG, 2)
    return data[0] * 256 + data[1]

# Function to convert raw angle to degrees
def raw_to_degrees(raw_angle):
    degrees = ((raw_angle / 16383.0) * 360) / 8
    return round((degrees + 90) % 360, 2)

# Initialize the last angle, total rotations, and rest position
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
    
    current_angle_raw = read_raw_angle()
    current_angle = raw_to_degrees(current_angle_raw)
    change_in_angle_raw = current_angle_raw - last_angle_raw
    last_angle_raw = current_angle_raw
    
    if change_in_angle_raw > 8191:
        total_rotations += 1
    elif change_in_angle_raw < -8191:
        total_rotations -= 1
    
    total_angle = round((total_rotations * 180 + current_angle - rest_position) % 360, 2)
    
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

async def controller(odrive, trial_id, tuning_factor=0.0003):
    try:
        print(f"Using trial_id: {trial_id}")
        for i in range(4):
            delay = max(0.1, 0.5 - tuning_factor * math.log(i + 1))
            odrive.set_velocity(-5000)
            await asyncio.sleep(delay)
            odrive.set_velocity(5000)
            await asyncio.sleep(delay)
        
        for i in range(1):
            delay = 0.648
            odrive.set_velocity(-5000)
            await asyncio.sleep(delay)
            odrive.set_velocity(5000)
            await asyncio.sleep(delay)

        odrive.set_velocity(0)
    finally:
        odrive.running = False

async def main():
    # Define the trial ID
    trial_id = 1  # Example, replace with dynamic fetching if needed

    # Create ODriveCAN object with node_id = 0
    odrive = pyodrivecan.ODriveCAN(0)
    
    # Clear old errors:
    odrive.clear_errors()
    
    try:
        # Initialize the ODrive object
        odrive.initCanBus()

        # Set O-Drive to velocity control mode
        odrive.set_controller_mode("velocity_control")

        # Set up PID controller with setpoint at 180 degrees
        pid = PID(10, 5, 0.05, setpoint=180)
        pid.output_limits = (-1000, 1000)  # Example PID limits for control

        use_pid = False

        while True:
            angle = read_angle()
            print(f"Angle: {angle:.2f} degrees")

            if not use_pid:
                # Perform controller function until angle is around 180 degrees
                if 135 <= angle <= 225:
                    print("Switching to PID control.")
                    use_pid = True  # Switch to PID control
                    #odrive.set_velocity(0)  # Stop the controller motion
                else:
                    await controller(odrive, trial_id)  # Continue with controller function
            else:
                # Perform PID control to maintain the angle at 180 degrees
                control_output = pid(angle)
                print(f"PID control output: {control_output}")

                # Set the velocity of the ODrive based on the PID control output
                odrive.set_velocity(control_output)

            # Wait for the next reading
            time.sleep(reading_interval)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        print("Cleanup (if necessary)")
        bus.close()

if __name__ == "__main__":
    print("Initializing rest position...")
    time.sleep(2)
    rest_position = raw_to_degrees(read_raw_angle())
    print("Rest position initialized at {:.2f} degrees.".format(rest_position))

    asyncio.run(main())
