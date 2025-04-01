from pydantic import BaseModel

class UserCreate(BaseModel):
    emai : str
    password : str

class UserLogin(BaseModel):
    email : str
    password : str
    device_id : str

class OTPVerify(BaseModel):
    user_id : str
    otp: str

class Token(BaseModel):
    access_token : str
    token_type : str