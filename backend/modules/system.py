"""
系统控制模块：启动 / 停止 / 状态查询
"""
import time
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

_state = {
    "running": False,
    "start_time": None,
}


class StatusResponse(BaseModel):
    running: bool
    uptime_sec: float
    message: str


@router.post("/system/start")
async def start_system():
    _state["running"] = True
    _state["start_time"] = time.time()
    return {"ok": True, "message": "系统已启动"}


@router.post("/system/stop")
async def stop_system():
    _state["running"] = False
    _state["start_time"] = None
    return {"ok": True, "message": "系统已停止"}


@router.get("/system/status", response_model=StatusResponse)
async def system_status():
    uptime = 0.0
    if _state["running"] and _state["start_time"]:
        uptime = round(time.time() - _state["start_time"], 1)
    return StatusResponse(
        running=_state["running"],
        uptime_sec=uptime,
        message="运行中" if _state["running"] else "已停止",
    )
