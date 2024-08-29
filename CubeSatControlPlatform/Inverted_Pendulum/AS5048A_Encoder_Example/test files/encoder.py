import smbus
import time

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
    # Adjust raw angle to make +x (right direction) as 0 degrees
    degrees = ((raw_angle / 16383.0) * 360)/8
    return round((degrees + 90) % 360, 2)  # Shift by 90 degrees, ensure wrap around, and round to 2 decimal places

# Initialize the last angle, total rotations, and rest position
last_angle_raw = read_raw_angle()
total_rotations = 0
rest_position = raw_to_degrees(last_angle_raw)
error_tolerance = 0.02  # Error tolerance considering two significant figures
stable_duration = 3  # Duration in seconds to consider the encoder at rest
stable_count = 0  # Counter for stable readings
reading_interval = 0.05  # Time interval between readings
stable_count_threshold = stable_duration / reading_interval  # Number of stable readings required for recalibration

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
        total_rotations = 1
    elif change_in_angle_raw < -8191:
        total_rotations = -1
    
    # Calculate the total angle considering the rotations
    total_angle = round((total_rotations * 180 + current_angle - rest_position) % 180, 2)  # Loop at every 360 degrees and round to 2 decimal places
    
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
    
# Main script
try:
    print("Initializing rest position...")
    time.sleep(2)  # Give some time to ensure the encoder is at rest
    rest_position = raw_to_degrees(read_raw_angle())  # Set the initial rest position
    print("Rest position initialized at {:.2f} degrees.".format(rest_position))
    
    while True:
        angle = read_angle()
        print("Angle: {:.2f} degrees".format(angle))
        time.sleep(reading_interval)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    bus.close()
