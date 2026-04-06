from repositories.emergency_repository import read_emergency_logs


def test_read_emergency_logs_returns_list():
    rows = read_emergency_logs(5)
    assert isinstance(rows, list)
