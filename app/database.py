from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./club.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # shows SQL in the terminal; you can set to False later
    connect_args={"check_same_thread": False}
)

def init_db():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Yield a database session."""
    with Session(engine) as session:
        yield session
