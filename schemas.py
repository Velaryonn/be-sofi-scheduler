from datetime import datetime

from pydantic import BaseModel, json


class ScheduleCreate(BaseModel):
    schedule_json: json

class Schedule(ScheduleCreate):
    id:int
    schedule_json:json
    created_at:datetime
    updated_at:datetime

    class Config:
        orm_mode = True