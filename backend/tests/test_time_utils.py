from utils.time_utils import format_uptime


def test_format_uptime_seconds_only():
    assert format_uptime(12) == '12秒'


def test_format_uptime_minutes_seconds():
    assert format_uptime(125) == '2分钟5秒'
