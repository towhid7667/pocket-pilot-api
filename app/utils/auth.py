from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt
from dotenv import load_dotenv
import os
import redis.asyncio as redis

load_dotenv()
secret_key = os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def hash_password(password : str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password : str, hashed_password : str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict , expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(datetime.timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) 
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=JWT_ALGORITHM)  

def verify_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None 
