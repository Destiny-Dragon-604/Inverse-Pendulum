import smbus
import time
import pyodrivecan
import asyncio

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
    return round((degrees + 90) % 360, 2)  # Adjust to make +x (right direction) as 0 degrees

# Initialize encoder variables
last_angle_raw = read_raw_angle()
total_rotations = 0
rest_position = raw_to_degrees(last_angle_raw)
error_tolerance = 0.02
stable_duration = 3
stable_count = 0
reading_interval = 0.01
stable_count_threshold = stable_duration / reading_interval

# PID control variables
kp = 0.1  # Proportional gain
ki = 0.01  # Integral gain
integral = 0  # Integral accumulator

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
    
    # Check for wrap around (if the encoder passes through 0)
    if change_in_angle_raw > 8191:  # more than half of 16383
        total_rotations += 1
    elif change_in_angle_raw < -8191:
        total_rotations -= 1
    
    # Calculate the total angle considering the rotations
    total_angle = round((total_rotations * 180 + current_angle - rest_position) % 360, 2)
    
    # Check if the angle is within the error tolerance
    if abs(total_angle) < error_tolerance:
        stable_count += 1
        if stable_count >= stable_count_threshold:
            rest_position = current_angle  # Recalibrate to new rest position
            stable_count = 0  # Reset stable count after recalibration
            print(f"Recalibrated rest position to: {rest_position:.2f} degrees")
        total_angle = 0  # Zero out the angle if within tolerance
    else:
        stable_count = 0  # Reset stable count if movement is detected
    
    return total_angle

def compute_pid_control(angle):
    global integral

    # Calculate error
    error = 0 - angle  # Target is 0 degrees, so error is negative of current angle
    
    # Update integral
    integral += error * reading_interval
    
    # Calculate control output
    control_output = kp * error + ki * integral
    
    return control_output

async def main():
    # Initialize ODrive
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

        while True:
            # Read the current angle
            angle = read_angle()
            print("Angle: {:.2f} degrees".format(angle))
            
            # Compute PID control output
            control_output = compute_pid_control(angle)
            
            # Set motor velocity based on PID control output
            velocity_command = max(min(control_output * 5000, 5000), -5000)  # Scale and constrain velocity
            odrive.set_velocity(velocity_command)
            
            await asyncio.sleep(reading_interval)

    except KeyboardInterrupt:
        print("Measurement stopped by user")
        bus.close()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Stop the motor
        odrive.set_velocity(0)
        print("Cleanup (if necessary)")
        bus.close()

if __name__ == "__main__":
    asyncio.run(main())


