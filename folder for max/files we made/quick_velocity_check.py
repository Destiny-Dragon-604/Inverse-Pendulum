import pyodrivecan
import asyncio
import math

async def controller(odrive, trial_id, tuning_factor=0.0003):
    try:
        print(f"Using trial_id: {trial_id}")

        # Enter closed loop control mode
        if not odrive.enter_closed_loop_control():
            print("ODrive 0 did not enter closed_loop_control. Exiting.")
            return

        # Set controller mode to velocity control and input mode to pass-through
        odrive.set_controller_mode("velocity_control")
        odrive.set_input_mode("pass_through")

        print("Controller mode set to velocity_control and input mode set to pass_through for ODrive 0.")

        # Continuous loop for movement
        while odrive.running:
            # Set velocity to a negative value to move in one direction
            odrive.set_velocity(-5000)
            await asyncio.sleep(1)  # Adjust delay as needed for your application

            # Set velocity to a positive value to move in the opposite direction
            odrive.set_velocity(5000)
            await asyncio.sleep(1)  # Adjust delay as needed for your application

        # Set velocity to 0 counts per second after the loop ends
        odrive.set_velocity(0)
    finally:
        # Set running flag to False to stop further operations
        odrive.running = False

async def main():
    # Define the trial ID
    trial_id = 4  # Example, replace with dynamic fetching if needed

    # Create ODriveCAN object with node_id = 0
    odrive = pyodrivecan.ODriveCAN(0)

    try:
        # Initialize the ODrive object
        odrive.initCanBus()

        # Set running flag to True to start continuous movement
        odrive.running = True

        # Run the controller function with a trial_id
        await controller(odrive, trial_id)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Implement any necessary cleanup here
        print("Cleanup (if necessary)")
        # Ensure the motor stops if an error occurs
        odrive.set_velocity(0)

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
