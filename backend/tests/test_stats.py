from services.stats_service import get_log_stats_payload


def test_stats_payload_has_required_keys():
    payload = get_log_stats_payload()
    assert 'summary' in payload
    assert 'top_targets' in payload
    assert 'recent_detections' in payload
