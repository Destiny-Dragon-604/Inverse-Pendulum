import smbus
import time
import matplotlib.pyplot as plt
import numpy as np

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
    degrees = ((raw_angle / 16383.0) * 360)/8 - 152.750
    return round((degrees + 90) % 360, 2)  # Shift by 90 degrees, ensure wrap around, and round to 2 decimal places

# Initialize variables
duration = 60  # Duration of data collection in seconds
interval = 0.01  # Time interval between readings in seconds
time_data = []  # List to store time data
theta_data = []  # List to store angular position data
omega_data = []  # List to store angular velocity data
alpha_data = []  # List to store angular acceleration data

# Set up the plot
plt.ion()  # Enable interactive mode
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))

# Plot for Angular Position
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Theta (degrees)')
ax1.set_title('Position (θ) vs. Time')
ax1.grid(True)
line1, = ax1.plot([], [], 'b-', linewidth=2)

# Plot for Angular Velocity
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Angular Velocity (degrees/s)')
ax2.set_title('Angular Velocity (ω) vs. Time')
ax2.grid(True)
line2, = ax2.plot([], [], 'r-', linewidth=2)

# Plot for Angular Acceleration
ax3.set_xlabel('Time (s)')
ax3.set_ylabel('Angular Acceleration (degrees/s^2)')
ax3.set_title('Angular Acceleration (α) vs. Time')
ax3.grid(True)
line3, = ax3.plot([], [], 'g-', linewidth=2)

# Initialize the data collection
print("Starting data collection...")
start_time = time.time()
current_time = 0

# Collect data and update the plot in real-time
while current_time <= duration:
    theta = raw_to_degrees(read_raw_angle())
    current_time = time.time() - start_time

    if time_data:
        dt = current_time - time_data[-1]  # Calculate the time difference
        omega = (theta - theta_data[-1]) / dt  # Angular velocity (degrees/s)
        omega_data.append(omega)

        if len(omega_data) > 1:
            d_omega = omega_data[-1] - omega_data[-2]  # Change in angular velocity
            alpha = d_omega / dt  # Angular acceleration (degrees/s^2)
            alpha_data.append(alpha)
        else:
            alpha_data.append(0)  # No acceleration data for the first point
    else:
        omega_data.append(0)  # No velocity data for the first point
        alpha_data.append(0)  # No acceleration data for the first point

    # Append the collected data
    time_data.append(current_time)
    theta_data.append(theta)

    # Update the plots
    line1.set_xdata(time_data)
    line1.set_ydata(theta_data)
    line2.set_xdata(time_data)
    line2.set_ydata(omega_data)
    line3.set_xdata(time_data)
    line3.set_ydata(alpha_data)
    
    ax1.relim()
    ax1.autoscale_view()
    ax2.relim()
    ax2.autoscale_view()
    ax3.relim()
    ax3.autoscale_view()
    
    plt.draw()
    plt.pause(interval)

    print(f"Time: {current_time:.2f} s, Theta: {theta:.2f} degrees, Omega: {omega_data[-1]:.2f} degrees/s, Alpha: {alpha_data[-1]:.2f} degrees/s^2")
    time.sleep(interval)

print("Data collection finished.")
plt.ioff()  # Turn off interactive mode
plt.show()  # Display the final plot
