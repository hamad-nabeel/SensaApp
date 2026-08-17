from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./sensa.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
@event.listens_for(engine, "connect")
def enable_foreign_keys(
    dbapi_connection,
    connection_record
):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


