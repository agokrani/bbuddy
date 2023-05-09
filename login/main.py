from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
import jwt

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"


DATABASE_URL = "postgresql://username:password@localhost/dbname"
#DATABASE_URL = "postgres://bijmbrqw:xnnbF7f-i_X-9uPRnUreaOOJFS-d9oWt@dumbo.db.elephantsql.com/bijmbrqw"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password = Column(String)
    phone_number = Column(String, nullable=True)


class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    phone_number: str = None

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone_number: str = None

    class Config:
        orm_mode = True


app = FastAPI()

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/register")
async def register(user: UserCreate, token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=user.email, name=user.name, password=user.password, phone_number=user.phone_number)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login")
async def login(email: str, password: str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password != password:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

