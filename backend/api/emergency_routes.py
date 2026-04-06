from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from services.emergency_service import trigger_emergency_flow, get_emergency_history

router = APIRouter()


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
    risk_info: str = '用户触发应急求助'


@router.post('/emergency')
async def trigger_emergency(req: EmergencyRequest):
    location = req.location.model_dump() if req.location else None
    contacts = [c.model_dump() for c in req.contacts]
    return trigger_emergency_flow(contacts, location, req.risk_info)


@router.get('/emergency/history')
async def get_emergency_history_api(limit: int = 50):
    return get_emergency_history(limit)
