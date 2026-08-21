from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.orm import Session

from .auth import get_current_user, get_db

from ..models import SensoryReport, UpdateRequest, University, UniversityLocation, User
from passlib.context import CryptContext

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)
class NewUniversityRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)

class NewLocationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    university_id: int = Field(ge=1)
user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


class AdminRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)

class AmbassadorRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)
    university_id: int = Field(ge=1)


def require_admin(user: dict | None):
    if user is None or user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )


@router.post("/new_university")
async def new_university(request: NewUniversityRequest, db: db_dependency, user: user_dependency):
    require_admin(user)
    university = University(
        name=request.name,
    )
    db.add(university)
    db.commit()
    db.refresh(university)
    return university

@router.post("/university_location")
async def new_university_location(request: NewLocationRequest, db: db_dependency, user: user_dependency):
    require_admin(user)
    university = db.query(University).filter(University.id == request.university_id).first()
    if university is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found",
        )

    location = UniversityLocation(
        name=request.name,
        university_id=request.university_id,
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location

@router.delete("/universities/{university_id}")
async def delete_university(university_id: int, db: db_dependency, user: user_dependency):
    require_admin(user)
    university = db.query(University).filter(University.id == university_id).first()
    if university is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found",
        )

    location_ids = [
        location_id
        for (location_id,) in db.query(UniversityLocation.id)
        .filter(UniversityLocation.university_id == university_id)
        .all()
    ]

    deleted_reports = 0
    deleted_update_requests = 0
    if location_ids:
        deleted_reports = (
            db.query(SensoryReport)
            .filter(SensoryReport.location_id.in_(location_ids))
            .delete(synchronize_session=False)
        )
        deleted_update_requests = (
            db.query(UpdateRequest)
            .filter(UpdateRequest.location_id.in_(location_ids))
            .delete(synchronize_session=False)
        )

    updated_users = (
        db.query(User)
        .filter(User.university_id == university_id)
        .update({User.university_id: None}, synchronize_session=False)
    )
    deleted_locations = (
        db.query(UniversityLocation)
        .filter(UniversityLocation.university_id == university_id)
        .delete(synchronize_session=False)
    )
    db.delete(university)
    db.commit()

    return {
        "message": "University deleted successfully",
        "deleted_university_id": university_id,
        "deleted_locations": deleted_locations,
        "deleted_reports": deleted_reports,
        "deleted_update_requests": deleted_update_requests,
        "updated_users": updated_users,
    }

@router.post("/create_admin")
async def create_admin(
    request: AdminRequest,
    db: db_dependency,
    token: Annotated[str | None, Depends(optional_oauth2_scheme)],
):
    admin_exists = db.query(User).filter(User.role == "admin").first() is not None
    if admin_exists:
        user = get_current_user(token)
        require_admin(user)

    email = str(request.email).lower()
    existing = db.query(User).filter(func.lower(User.email) == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    new_admin = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=email,
        hashed_password = bcrypt_context.hash(request.password),
        role="admin",
        university_id=None
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return {"message": "Admin created successfully", "id": new_admin.id}

@router.post('/create_ambassador')
async def create_ambassador(request: AmbassadorRequest, db: db_dependency,user: user_dependency ):
    require_admin(user)
    email = str(request.email).lower()
    existing = db.query(User).filter(func.lower(User.email) == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    university = db.query(University).filter(University.id == request.university_id).first()
    if university is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found",
        )

    ambassador = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=email,
        hashed_password=bcrypt_context.hash(request.password),
        role="ambassador",
        university_id=request.university_id,
    )
    db.add(ambassador)
    db.commit()
    db.refresh(ambassador)
    return {"message": "Ambassador created successfully", "id": ambassador.id}
