from services.risk_service import assess_risk


def test_high_risk_for_near_car():
    assert assess_risk('car', 500, 1000) == 'high'


def test_medium_risk_for_medium_car():
    assert assess_risk('car', 200, 1000) == 'medium'


def test_medium_risk_for_near_person():
    assert assess_risk('person', 500, 1000) == 'medium'
