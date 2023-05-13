from fastapi import FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# Set up the database connection
import psycopg2

conn = psycopg2.connect(
    host="your_host",
    database="your_database",
    user="your_username",
    password="your_password"
)

# Define the User model
class User(BaseModel):
    username: str
    email: str
    password: str

# Define the UserInDB model
class UserInDB(User):
    id: int

# Define the get_user function
def get_user(username: str):
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return UserInDB(id=result[0], username=result[1], email=result[2], password=result[3])

# Define the create_user function
def create_user(user: User):
    cursor = conn.cursor()
    query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id"
    cursor.execute(query, (user.username, user.email, hash_password(user.password)))
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    return UserInDB(id=result[0], username=user.username, email=user.email, password=user.password)

# Define the hash_password function
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

# Define the verify_password function
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Define the create_access_token function
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Define the authenticate_user function
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

# Define the /token endpoint
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Define the /register endpoint
@app.post("/register", response_model=UserInDB)
async def register(user: User):
    existing_user = get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(user)

# Run the FastAPI app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
