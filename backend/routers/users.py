from fastapi import APIRouter, status, HTTPException
from typing import Annotated
from fastapi.params import Depends
from sqlalchemy.orm import Session
import models
from models import University

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