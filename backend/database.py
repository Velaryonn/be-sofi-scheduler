from sqlmodel import create_engine, SQLModel, Session

db = "schedule2.db"
sqlite_url = f"sqlite:///{db}"

connect_args = {"check_same_thread" : False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

