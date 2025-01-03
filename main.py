from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import create_db_and_tables
from backend.routes.schduler import router as schedule_router

# Initialize FastAPI
app = FastAPI(
    title="Sofi Scheduler API",
    description="API SOFI Scheduler",
    version="1.0.0",
)

origins = [
    "http://localhost:3000",  # Replace with your frontend's URL
    "",  # Use "" to allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Include custom headers
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(
    schedule_router,
    tags=["Schedule"],
)
