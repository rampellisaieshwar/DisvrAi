import sqlite3
import os

DB_PATH = "db.sqlite3"

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def execute_query(query: str, params: tuple = ()):
    """Executes a SQL query and returns the results."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.commit()
        return results
    finally:
        conn.close()

def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            merchant TEXT,
            transaction_date TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
