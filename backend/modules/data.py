"""
本地数据接口模块
提供识别日志读取、风险记录写入等轻量接口
存储方式：SQLite（logs/data.db）
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

DB_PATH = Path(__file__).parent.parent / "logs" / "data.db"
DB_PATH.parent.mkdir(exist_ok=True)


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS detection_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ts        TEXT NOT NULL,
            label     TEXT,
            label_en  TEXT,
            risk      TEXT,
            distance  TEXT,
            direction TEXT,
            confidence REAL
        );
        CREATE TABLE IF NOT EXISTS risk_record (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ts       TEXT NOT NULL,
            level    TEXT,
            message  TEXT
        );
    """)
    conn.commit()
    conn.close()


init_db()


class DetectionLogEntry(BaseModel):
    label: str
    label_en: Optional[str] = ""
    risk: str
    distance: str
    direction: str
    confidence: float


class RiskRecord(BaseModel):
    level: str
    message: str


@router.post("/log/detection")
async def log_detection(entries: List[DetectionLogEntry]):
    """批量写入识别日志"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    conn.executemany(
        "INSERT INTO detection_log(ts,label,label_en,risk,distance,direction,confidence) "
        "VALUES(?,?,?,?,?,?,?)",
        [(ts, e.label, e.label_en, e.risk, e.distance, e.direction, e.confidence) for e in entries],
    )
    conn.commit()
    conn.close()
    return {"ok": True, "saved": len(entries)}


@router.get("/log/detection")
async def get_detection_log(limit: int = 50):
    """读取最近识别日志"""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM detection_log ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return {"logs": [dict(r) for r in rows]}


@router.post("/log/risk")
async def log_risk(record: RiskRecord):
    """写入风险记录"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    conn.execute(
        "INSERT INTO risk_record(ts, level, message) VALUES(?,?,?)",
        (ts, record.level, record.message),
    )
    conn.commit()
    conn.close()
    return {"ok": True}


@router.get("/log/risk")
async def get_risk_log(limit: int = 30):
    """读取风险记录"""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM risk_record ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return {"records": [dict(r) for r in rows]}


@router.delete("/log/clear")
async def clear_logs():
    """清空所有日志"""
    conn = get_db()
    conn.execute("DELETE FROM detection_log")
    conn.execute("DELETE FROM risk_record")
    conn.commit()
    conn.close()
    return {"ok": True, "message": "日志已清空"}
