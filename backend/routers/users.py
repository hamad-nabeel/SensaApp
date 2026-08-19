from fastapi import APIRouter, status, HTTPException
from typing import Annotated
from fastapi.params import Depends
from sqlalchemy.orm import Session
from ..models import University, UniversityLocation, SensoryReport, UpdateRequest
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
    if university is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found",
    )
    university_locations = []
    for location in university.locations:
        university_locations.append({"id": location.id, "name": location.name})
    return university_locations


@router.get("/get_location_report")
async def get_location_report(db: db_dependency, university_id: int, location_id: int):
    university_location = db.query(UniversityLocation).filter(UniversityLocation.university_id== university_id).filter(UniversityLocation.id == location_id).first()
    if university_location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )
    else:
        report = (
            db.query(SensoryReport)
            .filter(SensoryReport.location_id == university_location.id)
            .order_by(SensoryReport.created_at.desc())
            .first()
        )
        if report is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sensory report not found",
            )
        return{
            "overall_score": get_sensory_score(report),
            "crowdedness_score": report.crowdedness_level,
            "lighting_score": report.lighting_level,
            "temperature_score": report.temperature_level,
            "noise_score": report.noise_level,
            "additional_notes": report.note,
            "updated_at": report.created_at,
        }

@router.post("/request_update")
async def request_update(db: db_dependency, user: user_dependency, id: int):
    location = db.query(UniversityLocation).filter(UniversityLocation.id == id).first()
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found",
        )

    existing = db.query(UpdateRequest).filter(UpdateRequest.location_id == id).first()
    if existing:
        return {"message": "Update already requested", "id": existing.id}

    new_update = UpdateRequest(
        location_id=id,
    )
    db.add(new_update)
    db.commit()
    db.refresh(new_update)
    return {"message": "Update requested successfully", "id": new_update.id}
