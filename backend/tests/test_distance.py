from services.distance_estimator import estimate_distance


def test_estimate_distance_near_zone():
    result = estimate_distance(400, 'person', 800)
    assert '近距离' in result


def test_estimate_distance_unknown_when_invalid():
    assert estimate_distance(0, 'person', 800) == '未知'
