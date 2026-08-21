import os
import sqlite3
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self.cursor_obj = cursor

    def execute(self, query, params=None):
        # Convert MySQL placeholders (%s) to SQLite placeholders (?)
        query = query.replace("%s", "?")

        if params is None:
            return self.cursor_obj.execute(query)
        else:
            return self.cursor_obj.execute(query, params)

    def fetchone(self):
        row = self.cursor_obj.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        rows = self.cursor_obj.fetchall()
        return [dict(row) for row in rows]

    def __getattr__(self, name):
        return getattr(self.cursor_obj, name)


class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def cursor(self, dictionary=False):
        return SQLiteCursorWrapper(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def get_connection():
    """
    Try MySQL first.
    If unavailable, automatically use SQLite.
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

        db_path = os.path.join(
            os.path.dirname(__file__),
            "student_predictions.db"
        )

        conn = sqlite3.connect(
            db_path,
            check_same_thread=False
        )

        init_sqlite_tables(conn)

        return SQLiteConnectionWrapper(conn)


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