from fastapi import APIRouter
from pydantic import BaseModel
from services.system_service import start_system_state, stop_system_state, get_system_status

router = APIRouter()


class StatusResponse(BaseModel):
    running: bool
    uptime_sec: float
    message: str


@router.post('/system/start')
async def start_system():
    return start_system_state()


@router.post('/system/stop')
async def stop_system():
    return stop_system_state()


@router.get('/system/status', response_model=StatusResponse)
async def system_status():
    return StatusResponse(**get_system_status())
