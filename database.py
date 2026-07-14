import sqlite3
import os

DB_PATH = "company.db"


def get_connection():
    """Returns a SQLite connection with row factory enabled (dict-like rows)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
