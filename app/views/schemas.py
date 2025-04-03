from pydantic import BaseModel, ConfigDict, field_serializer
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

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime, _info):
        return created_at.isoformat()

    model_config = ConfigDict(
        from_attributes=True  # Replaces orm_mode=True
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