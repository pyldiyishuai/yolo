from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from repositories.db.database import init_db, get_db
from repositories.detection_repository import insert_detection_logs, select_detection_logs
from repositories.risk_repository import insert_risk_record, select_risk_records
from services.stats_service import get_log_stats_payload

router = APIRouter()
init_db()


class DetectionLogEntry(BaseModel):
    label: str
    label_en: Optional[str] = ''
    risk: str
    distance: str
    direction: str
    confidence: float


class RiskRecord(BaseModel):
    level: str
    message: str


@router.post('/log/detection')
async def log_detection(entries: List[DetectionLogEntry]):
    saved = insert_detection_logs([e.model_dump() for e in entries])
    return {'ok': True, 'saved': saved}


@router.get('/log/detection')
async def get_detection_log(limit: int = 50):
    return {'logs': select_detection_logs(limit)}


@router.get('/log/detection/history')
async def get_detection_history(limit: int = 100):
    return {'records': select_detection_logs(limit)}


@router.post('/log/risk')
async def log_risk(record: RiskRecord):
    insert_risk_record(record.level, record.message)
    return {'ok': True}


@router.get('/log/risk')
async def get_risk_log(limit: int = 30, level: Optional[str] = None):
    return {'records': select_risk_records(limit, level)}


@router.get('/log/stats')
async def get_log_stats():
    return get_log_stats_payload()


@router.delete('/log/clear')
async def clear_logs():
    conn = get_db()
    conn.execute('DELETE FROM detection_log')
    conn.execute('DELETE FROM risk_record')
    conn.commit()
    conn.close()
    return {'ok': True, 'message': '日志已清空'}
