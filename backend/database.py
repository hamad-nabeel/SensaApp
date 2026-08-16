from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_PATH = Path(__file__).resolve().parent / "sensa_db.sqlite"
engine = create_engine(f"sqlite:///{DATABASE_PATH}")
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
