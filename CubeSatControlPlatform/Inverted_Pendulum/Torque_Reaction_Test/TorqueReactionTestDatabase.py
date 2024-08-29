from sqlite3 import Error
import sqlite3

class TorqueReactionTestDatabase:

    def __init__(self, database_name):
        self.database_name = database_name
        self.conn = self.create_connection()

        self.create_table(
            '''CREATE TABLE IF NOT EXISTS trials(
            trial_id INTEGER PRIMARY KEY AUTOINCREMENT
            );'''
        )

        self.create_table(
            '''CREATE TABLE IF NOT EXISTS data(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trial_id INTEGER,
            time REAL,
            torque_setpoint REAL,
            torque_estimate REAL,
            FOREIGN KEY (trial_id) REFERENCES trials (trial_id)
            );'''
        )

    def create_connection(self):
        """ create a table from the create_table_sql statement """
        try:
            return sqlite3.connect(self.database_name)
        except Error as e:
            print(e)

    def get_connection(self):
        """
        Return a new connection to the SQLite database.
        This connection is thread-local.
        """
        try:
            return sqlite3.connect(self.database_name, check_same_thread=False)
        except Error as e:
            print(e)

    def create_table(self, create_table_sql):
        """ create table from the create_table_sql statement """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def add_trial(self):
        """
            Add a new trial to the trials table
        """
        sql = ''' INSERT INTO trials DEFAULT VALUES '''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return cur.lastrowid

    def add_data(self, trial_id, data):
        """
            Insert IMU data into data table
        """
        sql = ''' INSERT INTO data(trial_id, time, torque_setpoint, torque_estimate)
                  VALUES(?, ?, ?, ?) '''
        cur = self.conn.cursor()
        cur.execute(sql, (trial_id, *data))
        self.conn.commit()
        return cur.lastrowid

    def all_trials(self):
        """
        Returns all the trials
        """
        sql = ''' SELECT * FROM trials '''
        cur = self.conn.cursor()
        cur.execute(sql)
        return cur.fetchall()

    def all_imu_data(self, trial_id):
        """
        Returns all data for a given trial
        """
        sql = ''' SELECT * FROM data WHERE trial_id=? '''
        cur = self.conn.cursor()
        cur.execute(sql, (trial_id,))
        return cur.fetchall()

    def get_column_data(self, table_name, column_name):
        """
        Get all values from a specific column in a table.
        """
        cur = self.conn.cursor()
        cur.execute(f"SELECT {column_name} FROM {table_name}")
        results = cur.fetchall()
        return [item[0] for item in results]

    def delete_trial(self, trial_id):
        """
        Delete a trial and its associated data
        """
        # Delete associated imu_data first to maintain integrity
        cur = self.conn.cursor()
        cur.execute('''DELETE FROM data WHERE trial_id=?''', (trial_id,))
        cur.execute('''DELETE FROM trials WHERE trial_id=?''', (trial_id,))
        self.conn.commit()