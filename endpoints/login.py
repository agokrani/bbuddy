from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from jose.exceptions import JWTError
from db.user_manager import user_manager
from schema.user import UserCreate, UserInDB, User
from schema.token import Token, RefreshToken
from deps import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/access-token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "83899ed3e2c5f6504a2a86b4cf28fe6b286200e65064fad9b0866c5d64c31dbf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 48
REFRESH_TOKEN_EXPIRE_DAYS = 45

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(access_token=encoded_jwt, token_type="Bearer")

def create_refresh_token(data: dict, expires_delta: Optional[timedelta]= None): 
    to_encode = data.copy()
    if expires_delta: 
        expire = datetime.utcnow() + expires_delta
    else: 
        expire = datatime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return RefreshToken(refresh_token=encoded_jwt)

async def get_current_user(db = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = Token(access_token=token, token_type="Bearer")
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = user_manager.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    return user

@router.post("/register", response_model=User)
async def register_user(user: UserCreate, db = Depends(get_db)):
    db_user = user_manager.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = user_manager.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = user_manager.insert_user(db, user.username, user.email, hashed_password, user.firstName, user.lastName, user.phone)
    
    return db_user

@router.post("/login/access-token")
async def login_for_access_token(db = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):

    user = user_manager.get_user_by_username(db, form_data.username) 
    
    if not user:
        raise HTTPException(status_code=400, detail="The username you entered isn't connected to an account")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/login/refresh-token", response_model=Token)
async def refresh_access_token(data: dict, db = Depends(get_db)):
    try:
        if data['token'] is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        refresh_token = jwt.decode(data['token'], SECRET_KEY, algorithms=[ALGORITHM])
        username: str = refresh_token.get("sub")
        
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = user_manager.get_user_by_username(db, username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        access_token_expires = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return access_token
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        
# async def refresh_access_token(db = Depends(get_db), token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         refresh_token = payload.get("refresh_token")
#         print(refresh_token)
#         print(token)
#         import pdb;pdb.set_trace()
#         if refresh_token is None:
#             raise HTTPException(status_code=401, detail="Invalid authentication credentials")
#         try:
#             refresh_token_data = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
#         except jwt.ExpiredSignatureError:
#             raise HTTPException(status_code=401, detail="Refresh token has expired")
        
#         username: str = refresh_token_data.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid authentication credentials")
#         user = user_manager.get_user_by_username(db, username)
#         if user is None:
#             raise HTTPException(status_code=401, detail="Invalid authentication credentials")
#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token = create_access_token(
#             data={"sub": user.username}, expires_delta=access_token_expires
#         )
#         return {"access_token": access_token, "token_type": "Bearer"}
    
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
