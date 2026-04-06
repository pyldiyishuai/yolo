from datetime import datetime
from repositories.emergency_repository import append_emergency_log, read_emergency_logs
from services.sms_sender import try_send_sms


def build_location_text(location):
    if location and location.get('lat') is not None and location.get('lng') is not None:
        return f"纬度{location['lat']:.5f}, 经度{location['lng']:.5f}"
    return '位置未知'


def build_emergency_message(risk_info, location_text, now):
    return (
        f'【视助系统紧急求助】{now}\n'
        f'风险信息：{risk_info}\n'
        f'当前位置：{location_text}\n'
        f'请立即联系并提供帮助！'
    )


def trigger_emergency_flow(contacts, location=None, risk_info='用户触发应急求助'):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    location_text = build_location_text(location)
    message = build_emergency_message(risk_info, location_text, now)
    results = []
    for contact in contacts:
        ok = try_send_sms(contact, message)
        results.append({'contact_id': contact['id'], 'name': contact['name'], 'ok': ok})
        append_emergency_log({
            'time': now,
            'contact': contact['name'],
            'phone': contact['phone'],
            'ok': ok,
            'location': location_text,
            'risk_info': risk_info,
        })
    return {'ok': True, 'results': results, 'message': message}


def get_emergency_history(limit=50):
    return {'records': read_emergency_logs(limit)}
