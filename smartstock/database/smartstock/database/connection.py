import sqlite3
from pathlib import Path

# Path to the database file (always relative to project root)
DB_PATH = Path(__file__).resolve().parents[2] / "inventory.db"

def get_connection():
    """
    Creates and returns a SQLite database connection with
    foreign key support enabled.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"[Database Error] {e}")
        return None
