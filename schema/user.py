from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str
    phone: Optional[str]
    password: str

class User(BaseModel):
    id: int
    username: str
    email: str

class UserInDB(UserCreate): 
    id: int
