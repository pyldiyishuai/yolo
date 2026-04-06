def ok_response(message='ok', **kwargs):
    payload = {'ok': True, 'message': message}
    payload.update(kwargs)
    return payload


def error_response(message='error', **kwargs):
    payload = {'ok': False, 'message': message}
    payload.update(kwargs)
    return payload
