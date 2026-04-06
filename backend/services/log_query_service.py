from config.display_texts import ALERT_LEVEL_TEXT
from repositories.detection_repository import select_detection_logs
from repositories.risk_repository import select_risk_records


def get_recent_dashboard_logs(limit=10):
    detections = select_detection_logs(limit)
    risks = select_risk_records(limit)
    return {
        'detections': detections,
        'risks': [
            {
                **item,
                'level_text': ALERT_LEVEL_TEXT.get(item['level'], item['level'])
            }
            for item in risks
        ],
    }
