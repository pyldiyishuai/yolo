def get_direction(cx: float, img_w: int) -> str:
    third = img_w / 3
    if cx < third:
        return '左前方'
    if cx > third * 2:
        return '右前方'
    return '正前方'
