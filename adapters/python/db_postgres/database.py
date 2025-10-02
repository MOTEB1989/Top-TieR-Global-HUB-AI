import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    os.getenv("POSTGRES_DSN")
    or os.getenv("DATABASE_URL")
    or "postgresql+psycopg2://postgres:postgres@db_postgres:5432/postgres"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
