from datetime import datetime
from repositories.db.database import get_db


def insert_detection_logs(entries):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = get_db()
    conn.executemany(
        'INSERT INTO detection_log(ts,label,label_en,risk,distance,direction,confidence) VALUES(?,?,?,?,?,?,?)',
        [(ts, e['label'], e.get('label_en', ''), e['risk'], e['distance'], e['direction'], e['confidence']) for e in entries],
    )
    conn.commit()
    conn.close()
    return len(entries)


def select_detection_logs(limit=50):
    conn = get_db()
    rows = conn.execute('SELECT * FROM detection_log ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_top_targets(limit=5):
    conn = get_db()
    rows = conn.execute(
        'SELECT label, COUNT(*) AS count FROM detection_log GROUP BY label ORDER BY count DESC, label ASC LIMIT ?',
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
