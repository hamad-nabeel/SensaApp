from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Annotated

from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from .auth import get_current_user, get_db

from ..models import University, UniversityLocation, User
from passlib.context import CryptContext

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
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: str
    password: str = Field(min_length=8, max_length=50)
    university_id: int

class AmbassadorRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: str
    password: str = Field(min_length=8, max_length=50)
    university_id: int


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

@router.post("/create_admin")
async def create_admin(request: AdminRequest, db: db_dependency):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_admin = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        hashed_password = bcrypt_context.hash(request.password),
        role="admin",
        university_id=request.university_id,
    )
    db.add(new_admin)
    db.commit()

@router.post('/create_ambassador')
async def create_ambassador(request: AmbassadorRequest, db: db_dependency,user: user_dependency ):
    if not user.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Admin role required")
    else:
        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            ambassador = User(
              first_name=request.first_name,
              last_name=request.last_name,
              email=request.email,
               hashed_password=bcrypt_context.hash(request.password),
               role="ambassador",
                university_id=request.university_id,
             )
            db.add(ambassador)
            db.commit()
