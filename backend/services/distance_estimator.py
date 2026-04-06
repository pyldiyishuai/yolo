from config.risk_rules import FOCAL_LENGTH, REAL_HEIGHT, DIST_RATIO_NEAR, DIST_RATIO_MEDIUM


def estimate_distance(bbox_h: float, label: str, img_h: int) -> str:
    if bbox_h <= 0 or img_h <= 0:
        return '未知'
    ratio = bbox_h / img_h
    if ratio >= DIST_RATIO_NEAR:
        zone = '近距离'
    elif ratio >= DIST_RATIO_MEDIUM:
        zone = '中距离'
    else:
        zone = '远距离'
    real_h = REAL_HEIGHT.get(label, REAL_HEIGHT['default'])
    dist_m = (real_h * FOCAL_LENGTH) / bbox_h
    ref = f'{dist_m*100:.0f}cm' if dist_m < 1 else f'{dist_m:.1f}m'
    return f'{zone}（约{ref}）'
