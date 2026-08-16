from datetime import timedelta, datetime
from typing import Annotated
from urllib.request import Request

from fastapi import FastAPI, Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from ..database import SessionLocal
from passlib.context import CryptContext

from ..models import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

## JWT Encoding details
SECRET_KEY = "7cd802e77c631ee8bec50293b1f29acb3ad8fa967f514334ffe8b74e7d6eb90c" ##generated using openssl rand -hex 32
ALGORITHM = "HS256"

##---------


db_dependency = Annotated[SessionLocal, Depends(get_db)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

class UserRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: str
    password: str = Field(min_length=8, max_length=50)



router=APIRouter(
    prefix="/auth",
    tags=["auth"],
)

def create_new_access_token(email: str, role: str, id: str, expire_delta: timedelta):
    encode ={
        "email": email,
        "role": role,
        "id": id,
    }
    expire = datetime.utcnow() + expire_delta
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY)
        email: str = payload["email"]
        role: str = payload["role"]
        id: str = payload["id"]
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return {'email': email, 'role': role, 'id': id}

@router.post("/new_account")
async def new_account(request: UserRequest, db: db_dependency):
    new_user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        hashed_password=bcrypt_context.hash(request.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not bcrypt_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_new_access_token(user.email, user.role, user.id, timedelta(seconds=30))
    return {"access_token": token, "token_type": "bearer"}
