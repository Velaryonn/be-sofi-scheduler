import io
from itertools import count
from statistics import mean
from typing import Annotated, List

from fastapi import APIRouter, UploadFile, HTTPException, Depends, File
import pandas as pd
from fastapi.params import Query
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import Schedule
from backend.schemas import ResponseModel, ScheduleResponse
from rl_impelementation.thesis_defense_scheduler import ThesisDefenseScheduler
from rl_impelementation.thesis_panel_scheduler_final import ThesisPanelSchedulerFinal


router = APIRouter()

@router.get("/api/v1/schedules/{id}", response_model=ScheduleResponse)
def get_schedule_by_id(
    id: int,
    session: Session = Depends(get_session),
) -> ScheduleResponse:
    schedule = session.exec(select(Schedule).where(Schedule.id == id)).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return ScheduleResponse(
        id=schedule.id,
        schedule=schedule.schedule,
        total_schedule=schedule.total_schedule,
        total_dosen=schedule.total_dosen,
        avg_dosen=schedule.avg_dosen,
    )
@router.get("/api/v1/schedules", response_model=list[ScheduleResponse])
def read_schedules(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):

    results = session.exec(select(Schedule).offset(offset).limit(limit)).all()

    schedules = [
        ScheduleResponse(
            id=row.id,
            schedule=row.schedule,
        )
        for row in results
    ]

    return schedules

@router.post("/api/v1/schedule", response_model=ResponseModel)
def generate_schedule(dosen_file: UploadFile = File(...),
                      jadwal_file: UploadFile = File(...),
                      session: Session = Depends(get_session)):
    try:
        dosen_content = dosen_file.file.read()
        jadwal_content = jadwal_file.file.read()

        dosen_df = pd.read_excel(io.BytesIO(dosen_content))
        jadwal_df = pd.read_excel(io.BytesIO(jadwal_content))

        lecturer_expertise = {}
        for _, row in dosen_df.iterrows():
            lecturer_expertise[row['id']] = [field.strip() for field in row['keahlian'].split(',')]

        scheduler_defense = ThesisDefenseScheduler(jadwal_df, lecturer_expertise)

        best_schedule, best_reward = scheduler_defense.schedule_defenses(jadwal_df, lecturer_expertise,max_iterations=500)
        analysis = scheduler_defense.analyze_schedule(best_schedule)

        scheduler = ThesisPanelSchedulerFinal(jadwal_df, lecturer_expertise)
        final_schedule = scheduler.create_schedule()

        workload_summary = {}
        workload = final_schedule[['penguji1_id', 'penguji2_id', 'pembimbing1_id', 'pembimbing2_id']].stack()
        workload_counts = workload.value_counts()
        for lecturer_id, workload in workload_counts.items():
            workload_summary[lecturer_id] = workload

        formatted_schedule = []

        for _, row in final_schedule.iterrows():
            panel_assignment = {
                "penguji1Id": int(row["penguji1_id"]) if row["penguji1_id"] else None,
                "penguji2Id": int(row["penguji2_id"]) if row["penguji2_id"] else None,
                "pembimbing1Id": int(row["pembimbing1_id"]) if row["pembimbing1_id"] else None,
                "pembimbing2Id": int(row["pembimbing2_id"]) if row["pembimbing2_id"] else None,
            }
            formatted_schedule.append({
                "date": str(row["tanggal"]),
                "time": str(row["waktu"]),
                "room": row["ruang"],
                "studentId": int(row["mahasiswa_id"]),
                "thesisTitle": row["judul"],
                "field": row["bidang"],
                "panelAssignment": panel_assignment,
            })

        unique_fields = len(set(row["field"] for row in formatted_schedule))


        response = {
            "schedule": formatted_schedule,
            "reward": float(best_reward),
            "analysis": {
                "workload": workload_summary,
                "expertiseRatio": float(analysis["expertise_ratio"]),
                "balanceScore": float(analysis.get("balanceScore", 1.0)),
            },
            "total_schedule" : len(formatted_schedule),
            "total_dosen" : len(workload_summary),
            "avg_dosen" : mean(list(workload_summary.values())),
            "unique_fields": unique_fields  # Include unique field count

        }



        new_schedule = Schedule(schedule=response,
                                total_schedule=len(formatted_schedule),
                                total_dosen=len(workload_summary),
                                avg_dosen=mean(list(workload_summary.values())),


                                )
        session.add(new_schedule)
        session.commit()
        session.refresh(new_schedule)

        return response

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error")


