import os
from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from ..database import SessionLocal
from passlib.context import CryptContext

from ..models import University, User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

SECRET_KEY = os.getenv("SENSA_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SENSA_SECRET_KEY environment variable is required")
ALGORITHM = "HS256"

##---------


db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class UserRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=50)
    uni_id: int = Field(ge=1)



router=APIRouter(
    prefix="/auth",
    tags=["auth"],
)

def create_new_access_token(email: str, role: str, user_id: int, uni: int | None, expire_delta: timedelta):
    encode ={
        "email": email,
        "role": role,
        "id": user_id,
        "uni": uni,
    }
    expire = datetime.utcnow() + expire_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload["email"]
        role: str = payload["role"]
        user_id: int = payload["id"]
        uni: int | None = payload["uni"]
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return {'email': email, 'role': role, 'id': user_id, 'uni': uni}

@router.post("/new_account")
async def new_account(request: UserRequest, db: db_dependency):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    university = db.query(University).filter(University.id == request.uni_id).first()
    if university is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="University not found",
        )

    new_user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        hashed_password=bcrypt_context.hash(request.password),
        university_id=request.uni_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Account created successfully"}


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not bcrypt_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_new_access_token(user.email, user.role, user.id, user.university_id ,timedelta(hours=1))
    return {"access_token": token, "token_type": "bearer"}
