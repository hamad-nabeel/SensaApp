from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated

from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from .auth import get_current_user, get_db

from models import University, UniversityLocation

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)
class NewUniversityRequest(BaseModel):
    name: str

class NewLocationRequest(BaseModel):
    name: str
    university_id: int
user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]



@router.post("/new_university")
async def new_university(request: NewUniversityRequest, db: db_dependency, user: user_dependency):
    if not user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Admin role required")
    else:
        university = University(
            name=request.name,
        )
        db.add(university)
        db.commit()
@router.post("/university_location")
async def new_university_location(request: NewLocationRequest, db: db_dependency, user: user_dependency):
    if not user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Admin role required")
    else:
        location = UniversityLocation(
            name=request.name,
            university_id=request.university_id,
        )
        db.add(location)
        db.commit()



