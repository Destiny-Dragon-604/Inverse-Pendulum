import pyodrivecan
import asyncio
import math

async def controller(odrive, tuning_factor=0.0003):
    try:
        # Loop 10 times
        for i in range(10):
            # Calculate the adjusted delay using a logarithmic function
            # Ensure the delay does not become zero or negative
            delay = max(0.1, 0.5 - tuning_factor * math.log(i + 1))

            # Set velocity to -5000 counts per second
            odrive.set_velocity(-5000)
            await asyncio.sleep(delay)  # Wait for the dynamically calculated delay
            
            # Set velocity to 5000 counts per second
            odrive.set_velocity(5000)
            await asyncio.sleep(delay)  # Wait for the dynamically calculated delay

        # Set velocity to 0 counts per second
        odrive.set_velocity(0)
    finally:
        # Set running flag to False to stop further operations
        odrive.running = False

async def main():
    # Create ODriveCAN object with node_id = 0
    odrive = pyodrivecan.ODriveCAN(0)

    try:
        # Initialize the ODrive object
        odrive.initCanBus()

        # Set O-Drive to velocity control mode
        odrive.set_controller_mode("velocity_control")

        # Run the controller function
        await controller(odrive)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Implement any necessary cleanup here
        print("Cleanup (if necessary)")

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
