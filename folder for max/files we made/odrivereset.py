import pyodrivecan
import asyncio

async def controller(odrive):
    try:
        # Start with an initial velocity of 0 counts per second
        current_velocity = 0
        
        # Define the target velocity and the step size for increasing velocity
        target_velocity = 3000  # Adjust as needed for your application
        velocity_step = 100  # Increase by 100 counts per second per step
        step_delay = 0.5  # Delay between each velocity increment in seconds
        
        # Gradually increase the velocity to the target velocity
        while current_velocity < target_velocity:
            odrive.set_velocity(current_velocity)
            print(f"Setting velocity to {current_velocity} counts per second")
            await asyncio.sleep(step_delay)  # Wait for a short period before the next increment
            current_velocity += velocity_step

        # Maintain the target velocity for a certain duration
        print(f"Maintaining target velocity of {target_velocity} counts per second")
        await asyncio.sleep(15)  # Maintain target velocity for 15 seconds

        # Gradually decrease the velocity back to 0
        while current_velocity > 0:
            current_velocity -= velocity_step
            if current_velocity < 0:
                current_velocity = 0  # Ensure velocity does not go below 0
            odrive.set_velocity(current_velocity)
            print(f"Decreasing velocity to {current_velocity} counts per second")
            await asyncio.sleep(step_delay)

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
        # Properly shutdown CAN interface if needed
        odrive.shutdown_can()  # Hypothetical method, replace with actual if available

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
