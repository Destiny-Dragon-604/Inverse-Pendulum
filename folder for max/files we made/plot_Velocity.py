import sqlite3
import matplotlib.pyplot as plt

def read_odrive_data(db_file):
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Select velocity values from all trials
        cursor.execute("SELECT trial_id, velocity_estimate FROM ODriveData")
        rows = cursor.fetchall()

        # Print velocity values from all trials
        print("Velocity values from all trials:")
        for row in rows:
            print("Trial ID:", row[0], "Velocity:", row[1])

        # Select velocity values from trial ID 4
        cursor.execute("SELECT velocity_estimate FROM ODriveData WHERE trial_id = 4")
        rows_trial_4 = cursor.fetchall()

        # Multiply velocity values by 13
        velocity_values_trial_4 = [row[0] * 13 for row in rows_trial_4]

        # Plot velocity values from trial ID 4
        plt.plot(velocity_values_trial_4)
        plt.title('Velocity values from trial ID 4 (multiplied by 13)')
        plt.xlabel('Sample')
        plt.ylabel('Velocity')
        plt.grid(True)
        plt.show()

    except sqlite3.Error as e:
        print("SQLite error:", e)

    finally:
        if conn:
            # Close the database connection
            conn.close()

if __name__ == "__main__":
    db_file = "odrive_data.db"
    read_odrive_data(db_file)
