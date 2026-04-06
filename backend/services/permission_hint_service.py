from config.display_texts import PERMISSION_HINTS


def get_permission_hint(permission_name: str) -> str:
    return PERMISSION_HINTS.get(permission_name, '请检查浏览器权限设置')


def build_permission_summary(status_map: dict) -> list:
    summary = []
    for name, status in status_map.items():
        summary.append({
            'name': name,
            'status': status,
            'hint': '' if status == 'granted' else get_permission_hint(name),
        })
    return summary
