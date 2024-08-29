import smbus
import time
from simple_pid import PID
import pyodrivecan
import asyncio

# ... (rest of the imports)

def read_raw_angle(bus):
    # ... (rest of the function)

def raw_to_degrees(raw_angle):
    # ... (rest of the function)

def read_angle(bus, last_angle_raw, total_rotations, rest_position):
    # ... (rest of the function)

async def velocity_controller(odrive, trial_id, tuning_factor=0.0003):
    # ... (rest of the function)

async def pid_control(odrive, angle, pid):
    control_output = pid(angle)
    print(f"PID control output: {control_output}")
    odrive.set_velocity(control_output)

async def main(bus):
    trial_id = 1  # Example, replace with dynamic fetching if needed

    odrive = pyodrivecan.ODriveCAN(0)
    odrive.clear_errors()
    odrive.initCanBus()
    odrive.set_controller_mode("velocity_control")

    pid = PID(10, 5, 0.05, setpoint=180)
    pid.output_limits = (-1000, 1000)  # Example PID limits for control

    use_pid = False

    while True:
        angle = read_angle(bus, last_angle_raw, total_rotations, rest_position)
        print(f"Angle: {angle:.2f} degrees")

        if not use_pid:
            if 135 <= angle <= 225:
                print("Switching to PID control.")
                use_pid = True
                odrive.set_velocity(0)  # Stop the controller motion
            else:
                await velocity_controller(odrive, trial_id)
        else:
            await pid_control(odrive, angle, pid)

        time.sleep(reading_interval)

if __name__ == "__main__":
    print("Initializing rest position...")
    time.sleep(2)
    rest_position = raw_to_degrees(read_raw_angle(bus))
    print("Rest position initialized at {:.2f} degrees.".format(rest_position))

    asyncio.run(main(bus))
