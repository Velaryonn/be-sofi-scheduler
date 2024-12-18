from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from sqlalchemy.testing.config import db_url

from models import Schedule
from schemas import ScheduleCreate, Schedule as ScheduleSchema
from database import engine,Base, SessionLocal

Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def read_root():
    return {"message": "SOFI Scheduler"}

@app.post("/schedule", response_model=ScheduleSchema, status_code=201)
def create_schedule(schedule: ScheduleCreate, db: Session = Depends(get_db)):
    db_schedule = Schedule(schedule_json=schedule.schedule_json)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

@app.get("/schedule", response_model=List[ScheduleSchema], status_code=200)
def read_schedules(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    schedules = db.query(Schedule).offset(skip).limit(limit).all()
    return schedules

@app.get("/schedule/{schedule_id}", response_model=ScheduleSchema, status_code=200)
def read_schedule(schedule_id:int, db: Session= Depends(get_db)):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule