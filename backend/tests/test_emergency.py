from services.emergency_service import build_location_text, build_emergency_message


def test_build_location_text_known():
    text = build_location_text({'lat': 30.12345, 'lng': 120.54321})
    assert '纬度30.12345' in text


def test_build_message_contains_risk_info():
    msg = build_emergency_message('前方存在高风险', '位置未知', '2026-04-06 12:00:00')
    assert '前方存在高风险' in msg
