import json
import configparser
from pathlib import Path


def try_send_sms(contact, message: str) -> bool:
    try:
        cfg = configparser.ConfigParser()
        cfg.read(Path(__file__).resolve().parent.parent.parent / 'deploy' / 'config.ini', encoding='utf-8')
        provider = cfg.get('sms', 'provider', fallback='none')
        if provider == 'twilio':
            from twilio.rest import Client
            client = Client(cfg.get('sms', 'account_sid'), cfg.get('sms', 'auth_token'))
            client.messages.create(body=message, from_=cfg.get('sms', 'from_number'), to=contact['phone'])
            return True
        if provider == 'aliyun':
            from alibabacloud_dysmsapi20170525.client import Client as SmsClient
            from alibabacloud_tea_openapi import models as open_api_models
            from alibabacloud_dysmsapi20170525 import models as sms_models
            config = open_api_models.Config(access_key_id=cfg.get('sms', 'access_key_id'), access_key_secret=cfg.get('sms', 'access_key_secret'))
            config.endpoint = 'dysmsapi.aliyuncs.com'
            client = SmsClient(config)
            req = sms_models.SendSmsRequest(phone_numbers=contact['phone'], sign_name=cfg.get('sms', 'sign_name'), template_code=cfg.get('sms', 'template_code'), template_param=json.dumps({'content': message}, ensure_ascii=False))
            client.send_sms(req)
            return True
        return True
    except Exception:
        return False
