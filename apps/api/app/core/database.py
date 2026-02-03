# app/core/database.py
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from ..core.setting import settings

# PostgreSQL engine
engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True,pool_size=10,
    max_overflow=20,)

SessionLocal = sessionmaker(bind=engine, class_=Session, autocommit=False, autoflush=False)

def init_db() -> None:
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    with SessionLocal() as session:
        yield session



