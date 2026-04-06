import sqlite3
from config.settings import DB_PATH, LOG_DIR

LOG_DIR.mkdir(exist_ok=True)


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS detection_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            label TEXT,
            label_en TEXT,
            risk TEXT,
            distance TEXT,
            direction TEXT,
            confidence REAL
        );
        CREATE TABLE IF NOT EXISTS risk_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            level TEXT,
            message TEXT
        );
    """)
    conn.commit()
    conn.close()
