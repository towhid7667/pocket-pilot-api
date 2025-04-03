from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

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
    created_at: datetime
    is_verified: bool

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda dt: dt.isoformat()  # This ensures created_at is a string in JSON
        },
        from_attributes=True  # Replaces orm_mode=True in Pydantic v2
    )

class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    password: Optional[str] = None

class UserListResponse(BaseModel):
    users: List[UserResponse]

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str