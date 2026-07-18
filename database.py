from sqlmodel import create_engine, Session, SQLModel

engine = create_engine("sqlite:///./gms.db")


def create_db_and_tables():
    """

    """
    SQLModel.metadata.create_all(engine)


def get_db_session():
    """
    Fetches the current session and passes the same.
    """
    with Session(engine) as db_session:
        yield db_session


