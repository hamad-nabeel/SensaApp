from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
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
    location_id: int
    noise_level: int
    crowdedness_level: int
    lighting_level: int
    temperature_level: int
    note: str


def get_sensory_score(report: SensoryReport):
    score = report.noise_level + report.crowdedness_level + report.lighting_level + report.temperature_level
    score = score / 4
    return score

@router.post("/submit_report")
async def submit_report(request: SensoryRequest, db: db_dependency, user:user_dependency ):
    if not user.get("role") == "ambassador" and not user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Admin or ambassador role required")
    else:
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
    print(user.get("uni"))
    if not user.get("role") == "ambassador" and not user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Admin or ambassador role required")
    else:
        all_requests = db.query(UpdateRequest).join(UniversityLocation, UpdateRequest.location_id == UniversityLocation.id).filter(UniversityLocation.university_id == user.get("uni")).all()
        return all_requests