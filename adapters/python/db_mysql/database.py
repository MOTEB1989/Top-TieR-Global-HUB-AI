import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    os.getenv("MYSQL_DSN")
    or os.getenv("DATABASE_URL")
    or "mysql+pymysql://root:root@db_mysql:3306/lexcode"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
