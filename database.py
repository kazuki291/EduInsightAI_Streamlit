import os
import sqlite3
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def cursor(self, dictionary=False):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def get_connection():
    """
    Attempts to connect to MySQL. If MySQL is offline,
    automatically falls back to local SQLite so the demo never crashes.
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "eduinsight"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        return conn
    except Exception:
        # Fallback to local SQLite database file
        db_path = os.path.join(os.path.dirname(__file__), "student_predictions.db")
        raw_conn = sqlite3.connect(db_path, check_same_thread=False)
        init_sqlite_tables(raw_conn)
        return SQLiteConnectionWrapper(raw_conn)

def init_sqlite_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            student_name TEXT,
            gender TEXT,
            study_hours_per_day REAL,
            attendance_percentage REAL,
            assignment_score REAL,
            midterm_score REAL,
            final_exam_score REAL,
            participation_score REAL,
            internet_access TEXT,
            extra_classes TEXT,
            parent_education TEXT,
            sleep_hours REAL,
            prediction TEXT,
            confidence_score REAL,
            recommendation TEXT,
            prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit() 