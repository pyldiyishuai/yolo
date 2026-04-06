from utils.location import haversine, check_route_deviation


def test_haversine_zero_distance():
    assert round(haversine(30.0, 120.0, 30.0, 120.0), 1) == 0.0


def test_route_deviation_false_when_close():
    result = check_route_deviation(30.0, 120.0, [{'lat': 30.0, 'lng': 120.0001}], threshold_m=50)
    assert result['deviated'] is False
