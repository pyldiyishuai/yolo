"""
应急求助模块
接收前端求助请求 -> 记录日志 -> 尝试发送短信通知
"""
import json
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

LOG_PATH = Path(__file__).parent.parent / "logs" / "emergency.log"
LOG_PATH.parent.mkdir(exist_ok=True)


class Contact(BaseModel):
    id: int
    name: str
    phone: str


class LocationInfo(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    accuracy: Optional[float] = None


class EmergencyRequest(BaseModel):
    contacts: List[Contact]
    location: Optional[LocationInfo] = None
    risk_info: str = "用户触发应急求助"


def _write_log(entry: dict):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _try_send_sms(contact: Contact, message: str) -> bool:
    """尝试调用 Twilio 或阿里云短信，未配置则跳过"""
    try:
        import configparser
        cfg = configparser.ConfigParser()
        cfg.read(
            Path(__file__).parent.parent.parent / "deploy" / "config.ini",
            encoding="utf-8",
        )
        sms_provider = cfg.get("sms", "provider", fallback="none")

        if sms_provider == "twilio":
            from twilio.rest import Client
            client = Client(
                cfg.get("sms", "account_sid"),
                cfg.get("sms", "auth_token"),
            )
            client.messages.create(
                body=message,
                from_=cfg.get("sms", "from_number"),
                to=contact.phone,
            )
            return True

        elif sms_provider == "aliyun":
            from alibabacloud_dysmsapi20170525.client import Client as SmsClient
            from alibabacloud_tea_openapi import models as open_api_models
            from alibabacloud_dysmsapi20170525 import models as sms_models
            config = open_api_models.Config(
                access_key_id=cfg.get("sms", "access_key_id"),
                access_key_secret=cfg.get("sms", "access_key_secret"),
            )
            config.endpoint = "dysmsapi.aliyuncs.com"
            client = SmsClient(config)
            req = sms_models.SendSmsRequest(
                phone_numbers=contact.phone,
                sign_name=cfg.get("sms", "sign_name"),
                template_code=cfg.get("sms", "template_code"),
                template_param=json.dumps({"content": message}, ensure_ascii=False),
            )
            client.send_sms(req)
            return True
        else:
            # 未配置短信服务，本地日志记录即可
            print(f"[应急] SMS未配置，模拟发送给 {contact.name}({contact.phone}): {message}")
            return True
    except Exception as e:
        print(f"[应急] 短信发送失败: {e}")
        return False


@router.post("/emergency")
async def trigger_emergency(req: EmergencyRequest):
    """处理应急求助，通知所有紧急联系人"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    loc_str = "位置未知"
    if req.location and req.location.lat:
        loc_str = f"纬度{req.location.lat:.5f}, 经度{req.location.lng:.5f}"

    message = (
        f"【视助系统紧急求助】{now}\n"
        f"风险信息：{req.risk_info}\n"
        f"当前位置：{loc_str}\n"
        f"请立即联系并提供帮助！"
    )

    results = []
    for contact in req.contacts:
        ok = _try_send_sms(contact, message)
        results.append({"contact_id": contact.id, "name": contact.name, "ok": ok})
        _write_log({
            "time": now, "contact": contact.name,
            "phone": contact.phone, "ok": ok,
            "location": loc_str, "risk_info": req.risk_info,
        })

    return {"ok": True, "results": results, "message": message}
