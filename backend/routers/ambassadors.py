from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Annotated

from sqlalchemy.orm import Session

from ..models import SensoryReport, UpdateRequest, UniversityLocation
from .auth import get_current_user, get_db

router = APIRouter(
    prefix="/ambassadors",
    tags=["ambassadors"],
)

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

class SensoryRequest(BaseModel):
    location_id: int = Field(ge=1)
    noise_level: int = Field(ge=1, le=5)
    crowdedness_level: int = Field(ge=1, le=5)
    lighting_level: int = Field(ge=1, le=5)
    temperature_level: int = Field(ge=1, le=5)
    note: str = Field(default="", max_length=500)


def get_sensory_score(report: SensoryReport):
    score = report.noise_level + report.crowdedness_level + report.lighting_level + report.temperature_level
    score = score / 4
    return score


def format_update_requests(requests):
    return [
        {
            "id": update_request.id,
            "location_id": update_request.location_id,
            "location_name": update_request.location.name,
            "created_at": update_request.created_at,
        }
        for update_request in requests
    ]

@router.post("/submit_report")
async def submit_report(request: SensoryRequest, db: db_dependency, user:user_dependency ):
    if not user.get("role") == "ambassador" and not user.get("role") == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or ambassador role required")
    else:
        location = db.query(UniversityLocation).filter(UniversityLocation.id == request.location_id).first()
        if location is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found",
            )
        university = location.university_id
        if user.get("role") == "ambassador" and not user.get("uni") == university:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your university")
        new_report = SensoryReport(
            location_id = request.location_id
            ,noise_level = request.noise_level
            ,reporter_id= user.get("id")
            ,crowdedness_level = request.crowdedness_level
            ,lighting_level = request.lighting_level
            ,temperature_level = request.temperature_level
            ,note = request.note
        )
        existing_report = db.query(SensoryReport).filter(SensoryReport.location_id == new_report.location_id).first()
        if existing_report:
            db.delete(existing_report)
            db.commit()
        db.add(new_report)
        db.commit()
        return{
            "message": "Sensory report published successfully! Previous report was replaced.",
            "report": new_report
        }


@router.get('/update_requests')
async def all_requests(db: db_dependency, user: user_dependency):
    if not user.get("role") == "ambassador" and not user.get("role") == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin or ambassador role required")
    else:
        if user.get("role") == "ambassador":
            all_requests = db.query(UpdateRequest).join(UniversityLocation,
                                                        UpdateRequest.location_id == UniversityLocation.id).filter(
                UniversityLocation.university_id == user.get("uni")).all()
            return format_update_requests(all_requests)
        elif user.get("role") == "admin":
            all_requests = db.query(UpdateRequest).all()
            return format_update_requests(all_requests)
