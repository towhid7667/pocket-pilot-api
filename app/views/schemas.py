from pydantic import BaseModel
from typing import Optional, List

class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    profile_picture_url: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class OTPVerify(BaseModel):
    user_id: str
    otp: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    profile_picture_url: Optional[str] = None
    created_at: str
    is_verified: bool

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_picture_url: Optional[str] = None

class UserListResponse(BaseModel):
    users: List[UserResponse]