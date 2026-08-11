from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///db.sqlite")
Base = declarative_base(engine)
SessionLocal = sessionmaker(bind=engine)