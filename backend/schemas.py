from typing import Dict, Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    schedule:list
    reward:float
    analysis:dict
    total_schedule:float
    total_dosen:float
    avg_dosen:float


class ScheduleResponse(BaseModel):
    id: int
    schedule: Dict[str, Any]