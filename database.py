import sqlite3

from config import DB_PATH


class DatabaseManager:
    """
    Handles all SQLite database operations for BMI records.

    Every database method catches sqlite3.Error internally and returns a safe
    value (False or an empty list) instead of raising an exception. This keeps
    the GUI responsive even if the database file is locked, missing, or
    otherwise unreadable.
    """

    def __init__(self):
        """Open (or create) the database and ensure the table exists."""
        self.conn = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Open a connection to the SQLite database."""
        try:
            self.conn = sqlite3.connect(DB_PATH)
        except sqlite3.Error:
            # If the connection fails, self.conn stays None and every
            # operation below degrades gracefully.
            self.conn = None

    def _create_table(self):
        """Create the bmi_records table if it does not already exist."""
        if self.conn is None:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bmi_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    weight REAL NOT NULL,
                    height REAL NOT NULL,
                    bmi REAL NOT NULL,
                    category TEXT NOT NULL,
                    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
        except sqlite3.Error:
            # Table creation failure is handled by the caller via the
            # return values of save_record/get_history.
            pass

    def save_record(self, user_name, weight, height, bmi, category):
        """
        Insert one BMI record into the database.

        Returns:
            True on success, False if the write failed.
        """
        if self.conn is None:
            return False
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO bmi_records (user_name, weight, height, bmi, category)
                VALUES (?, ?, ?, ?, ?)
            """, (user_name, weight, height, bmi, category))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_history(self, user_name):
        """
        Fetch all BMI records for one user, oldest record first.

        Returns:
            A list of tuples: (weight, height, bmi, category, record_date).
            Returns an empty list if the user has no records or a read fails.
        """
        if self.conn is None:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT weight, height, bmi, category, record_date
                FROM bmi_records
                WHERE user_name = ?
                ORDER BY record_date ASC
            """, (user_name,))
            return cursor.fetchall()
        except sqlite3.Error:
            return []

    def get_unique_users(self):
        """
        Return a sorted list of distinct user names stored in the database.

        Returns:
            A list of user name strings, or an empty list on failure.
        """
        if self.conn is None:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT DISTINCT user_name
                FROM bmi_records
                ORDER BY user_name ASC
            """)
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def close(self):
        """Close the database connection if it is open."""
        if self.conn:
            self.conn.close()
            self.conn = None
