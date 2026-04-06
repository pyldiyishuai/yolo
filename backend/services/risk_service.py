from config.object_labels import HIGH_RISK_LABELS, MEDIUM_RISK_LABELS
from config.risk_rules import DIST_RATIO_NEAR, DIST_RATIO_MEDIUM


def assess_risk(label: str, bbox_h: float, img_h: int) -> str:
    if img_h <= 0:
        return 'low'
    ratio = bbox_h / img_h
    if label in HIGH_RISK_LABELS:
        if ratio >= DIST_RATIO_NEAR:
            return 'high'
        if ratio >= DIST_RATIO_MEDIUM:
            return 'medium'
        return 'low'
    if label in MEDIUM_RISK_LABELS:
        if ratio >= DIST_RATIO_NEAR:
            return 'medium'
        return 'low'
    return 'low'
