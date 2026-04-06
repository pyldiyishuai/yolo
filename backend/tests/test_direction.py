from services.direction_service import get_direction


def test_direction_left():
    assert get_direction(10, 300) == '左前方'


def test_direction_center():
    assert get_direction(150, 300) == '正前方'


def test_direction_right():
    assert get_direction(290, 300) == '右前方'
