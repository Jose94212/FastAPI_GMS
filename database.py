from sqlmodel import create_engine, SQLModel

engine = create_engine("sqlite:///./gms.db")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
