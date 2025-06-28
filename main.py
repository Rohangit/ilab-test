from typing import Union

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from database import engine, SessionLocal
import models
import auth
from auth import validate_request
import ai
import rate_limiter


app = FastAPI()
app.include_router(auth.router)

# call model and db create sqlite database and tables
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# dependancies
db_dependency = Annotated[Session, Depends(get_db)]
user_dependancey = Annotated[dict, Depends(validate_request)]

items = []

@app.get("/")
def read_root():
    return {"Project Name": "iLab Test", "Version": "1.0"}

@app.get("/users", status_code=status.HTTP_200_OK)
async def users(user:user_dependancey, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not authenticate check token lifetime")
    return {"user": user}