import time

_state = {
    'running': False,
    'start_time': None,
}


def start_system_state():
    _state['running'] = True
    _state['start_time'] = time.time()
    return {'ok': True, 'message': '系统已启动'}


def stop_system_state():
    _state['running'] = False
    _state['start_time'] = None
    return {'ok': True, 'message': '系统已停止'}


def get_system_status():
    uptime = 0.0
    if _state['running'] and _state['start_time']:
        uptime = round(time.time() - _state['start_time'], 1)
    return {
        'running': _state['running'],
        'uptime_sec': uptime,
        'message': '运行中' if _state['running'] else '已停止',
    }
