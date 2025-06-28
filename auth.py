from datetime import datetime, timedelta
from typing import Annotated
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.DEBUG)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

load_dotenv()

# import config keys and settings from env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/create-token")

class CreateUserRequest(BaseModel):
    username:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# create user api
@router.post("/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    try:
        existing_user = db.query(User).filter(User.username == create_user_request.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="username already registered"
            )
        
        create_user_model = User(
            username=create_user_request.username,
            hashed_password=bcrypt_context.hash(create_user_request.password),
        )
        
        db.add(create_user_model)
        db.commit()

        return { 'message': 'successfully created' }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

# generate token
# return token json format
@router.post("/create-token", response_model=Token)
async def create_token(from_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    try:
        user = authenticate_user(from_data.username, from_data.password, db)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="username or password error")
        
        token = create_access_token(user.username, user.id, timedelta(minutes=20))

        return {'access_token': token, 'token_type': 'bearer'}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in authenticating user: {str(e)}"
        )

# authenticate user
# return bool or user object
def authenticate_user(username:str, password:str, db):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# create jwt token
# return jwt
def create_access_token(username:str, user_id:str, expire_dt: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + expire_dt
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# validate user rquest by bearer token
async def validate_request(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not authenticate check token lifetime")
        
        return {'username': username, 'id': user_id};

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not authenticate check token lifetime")