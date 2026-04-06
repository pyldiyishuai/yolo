from repositories.detection_repository import select_detection_logs, count_top_targets
from repositories.risk_repository import count_all_risk, count_risk_by_level
from repositories.db.database import get_db


def get_log_stats_summary():
    conn = get_db()
    total_detection = conn.execute('SELECT COUNT(*) AS c FROM detection_log').fetchone()['c']
    conn.close()
    return {
        'total_detection': total_detection,
        'total_risk': count_all_risk(),
        'high_risk': count_risk_by_level('high'),
        'medium_risk': count_risk_by_level('medium'),
        'low_risk': count_risk_by_level('low'),
    }


def get_log_stats_payload():
    return {
        'summary': get_log_stats_summary(),
        'top_targets': count_top_targets(5),
        'recent_detections': select_detection_logs(10),
    }
