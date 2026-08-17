from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String, default="viewer")
    university_id = Column(Integer, ForeignKey("universities.id"))


class University(Base):
    __tablename__ = "universities"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    locations = relationship("UniversityLocation", back_populates="university")

class SensoryReport(Base):
    __tablename__ = "sensory_reports"
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("universities_locations.id"))
    reporter_id = Column(Integer, ForeignKey("users.id"))
    noise_level = Column(Integer)
    crowdedness_level = Column(Integer)
    lighting_level = Column(Integer)
    temperature_level = Column(Integer)
    note = Column(String)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False)

class UpdateRequest(Base):
    __tablename__ = "update_requests"
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("universities_locations.id"))
    location = relationship("UniversityLocation", back_populates="requests")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UniversityLocation(Base):
    __tablename__ = "universities_locations"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    requests = relationship("UpdateRequest", back_populates="location")
    university_id = Column(Integer, ForeignKey("universities.id"))
    university = relationship("University", back_populates="locations")
