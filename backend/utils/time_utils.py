from datetime import datetime


def now_text() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def format_uptime(seconds: float) -> str:
    seconds = int(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, sec = divmod(rem, 60)
    if hours:
        return f'{hours}小时{minutes}分钟{sec}秒'
    if minutes:
        return f'{minutes}分钟{sec}秒'
    return f'{sec}秒'
