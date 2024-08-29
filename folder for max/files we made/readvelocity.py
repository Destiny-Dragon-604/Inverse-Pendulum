import pyodrivecan
import asyncio
import sqlite3
from datetime import datetime

# Function to initialize the SQLite database
def init_db():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('odrive_data.db')
    cursor = conn.cursor()

    # Create a table to store velocity data if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS velocity_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            velocity REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to insert velocity data into the database
def insert_velocity_data(velocity):
    # Connect to the SQLite database
    conn = sqlite3.connect('odrive_data.db')
    cursor = conn.cursor()

    # Insert the current timestamp and velocity into the database
    cursor.execute('''
        INSERT INTO velocity_data (timestamp, velocity)
        VALUES (?, ?)
    ''', (datetime.now().isoformat(), velocity))
    
    conn.commit()
    conn.close()

async def read_velocity(odrive):
    try:
        print("Reading velocity data from ODrive...")
        
        while odrive.running:
            # Await the coroutine to get velocity data
            velocity = await odrive.get_velocity()  # Ensure this method is correctly implemented in pyodrivecan
            print(f"Current velocity: {velocity} counts per second")

            # Insert the velocity data into the SQLite database
            insert_velocity_data(velocity)

            await asyncio.sleep(0.5)  # Read velocity data every 0.5 seconds

    except Exception as e:
        print(f"An error occurred while reading velocity: {e}")

async def main():
    # Initialize the database
    init_db()

    # Create ODriveCAN object with node_id = 0
    odrive = pyodrivecan.ODriveCAN(0)
    odrive.running = True

    try:
        # Initialize the ODrive object
        odrive.initCanBus()

        # Set O-Drive to velocity control mode
        odrive.set_controller_mode("velocity_control")

        # Call read_velocity to continuously read and store velocity data
        await read_velocity(odrive)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Implement any necessary cleanup here
        print("Cleanup (if necessary)")
        odrive.running = False  # Ensure the loop stops
        # Commented out since `shutdown_can` does not exist in the library
        # odrive.shutdown_can()  # Replace with the actual method if available

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())
