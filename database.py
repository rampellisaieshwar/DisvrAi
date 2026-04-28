import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# The user can set this in their environment variables on Render
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

def get_connection():
    """Returns a connection to the PostgreSQL database."""
    conn = psycopg2.connect(DB_URL)
    return conn

def execute_query(query: str, params: tuple = ()):
    """Executes a SQL query and returns the results as a list of dictionaries."""
    conn = get_connection()
    try:
        # Use RealDictCursor so rows behave like dictionaries
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, params)
        
        # If it's a SELECT query, fetch results
        if cursor.description:
            results = cursor.fetchall()
            conn.commit()
            return [dict(row) for row in results]
        else:
            conn.commit()
            return []
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                amount REAL,
                category VARCHAR(255),
                merchant VARCHAR(255),
                transaction_date TIMESTAMP
            )
        """)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
