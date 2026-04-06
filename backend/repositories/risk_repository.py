from datetime import datetime
from repositories.db.database import get_db


def insert_risk_record(level, message):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db()
    conn.execute('INSERT INTO risk_record(ts, level, message) VALUES(?,?,?)', (ts, level, message))
    conn.commit()
    conn.close()


def select_risk_records(limit=30, level=None):
    conn = get_db()
    if level:
        rows = conn.execute('SELECT * FROM risk_record WHERE level = ? ORDER BY id DESC LIMIT ?', (level, limit)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM risk_record ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_risk_by_level(level):
    conn = get_db()
    row = conn.execute('SELECT COUNT(*) AS c FROM risk_record WHERE level = ?', (level,)).fetchone()
    conn.close()
    return row['c']


def count_all_risk():
    conn = get_db()
    row = conn.execute('SELECT COUNT(*) AS c FROM risk_record').fetchone()
    conn.close()
    return row['c']
