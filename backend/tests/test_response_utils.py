from utils.response_utils import ok_response, error_response


def test_ok_response_shape():
    payload = ok_response('done', count=2)
    assert payload['ok'] is True
    assert payload['count'] == 2


def test_error_response_shape():
    payload = error_response('bad')
    assert payload['ok'] is False
    assert payload['message'] == 'bad'
