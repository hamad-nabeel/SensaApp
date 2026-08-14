from fastapi import APIRouter, status, HTTPException
from typing import Annotated
from fastapi.params import Depends
from sqlalchemy.orm import Session
import models
from models import University, UniversityLocation, SensoryReport
from .ambassadors import get_sensory_score

from .auth import get_current_user, get_db
router = APIRouter(
    prefix="/users",
    tags=["users"],
)
user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/universities")
async def get_universities(db: db_dependency):
    universities = db.query(University).all()
    return universities


@router.get("/universities/{university_id}")
async def get_university(university_id: int, db: db_dependency):
    university = db.query(University).filter(University.id == university_id).first()
    university_locations =[]
    for location in university.locations:
        university_locations.append(location.name)
    return university_locations


@router.get("/get_location_report")
async def get_location_report(db: db_dependency, university_id: int, location_id: int):
    university_location = db.query(UniversityLocation).filter(UniversityLocation.university_id== university_id).filter(UniversityLocation.id == location_id).first()
    if university_location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)
    else:
        report = db.query(SensoryReport).filter(SensoryReport.location_id== university_location.id).first()
        return{
            "Overall Sensory Score": get_sensory_score(report),
            "Crowdedness: ": report.crowdedness_level,
            "Lighting: ": report.lighting_level,
            "Temperature: ": report.temperature_level,
            "Noise: ": report.noise_level,
            "Additional Notes: ": report.note,
        }
