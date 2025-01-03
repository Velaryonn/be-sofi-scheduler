from typing import Dict, Any
from sqlalchemy import JSON
from sqlmodel import SQLModel, Field, Column


class Schedule(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    schedule: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    total_schedule: int = Field(default=None)
    total_dosen: int = Field(default=None)
    avg_dosen: float = Field(default=None)
