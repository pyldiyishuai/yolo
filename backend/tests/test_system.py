from services.system_service import start_system_state, stop_system_state, get_system_status


def test_system_start_and_stop_flow():
    start_system_state()
    status = get_system_status()
    assert status['running'] is True
    stop_system_state()
    status = get_system_status()
    assert status['running'] is False
