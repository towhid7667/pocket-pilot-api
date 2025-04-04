from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_redis, verify_token
from app.views.user import (register_user, verify_user, login_user, logout_user, 
                            get_user_by_id, get_all_users, update_user, forgot_password, reset_password)
from app.views.schemas import (UserCreate, UserLogin, OTPVerify, Token, UserResponse, 
                               UserUpdate, UserListResponse, ForgotPasswordRequest, ResetPasswordRequest)
from app.utils.telegram import send_telegram_message

router = APIRouter(prefix="/user", tags=["user"])

async def get_current_user(request: Request, redis_client = Depends(get_redis)):
    try:
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(401, "Not authenticated")
            
        if await redis_client.get(f"blacklist:{token}"):
            raise HTTPException(401, "Token blacklisted")
        
        payload = verify_token(token)
        if not payload:
            raise HTTPException(401, "Invalid token")
        
        return payload["sub"]  # Return email instead of token for user identification
    except Exception as e:
        error_msg = f"Error in get_current_user: {str(e)}"
        send_telegram_message(error_msg)
        raise

@router.post("/register", response_model=dict)
async def register(user: UserCreate, db: Session = Depends(get_db), redis_client = Depends(get_redis)):
    db_user = await register_user(user.email, user.password, user.name, user.profile_picture_url, db, redis_client)
    return {"message": "User registered. Verify your email.", "user_id": db_user.id}

@router.post("/verify", response_model=dict)
async def verify(otp_data: OTPVerify, db: Session = Depends(get_db), redis_client = Depends(get_redis)):
    if await verify_user(otp_data.user_id, otp_data.otp, db, redis_client):
        return {"message": "User verified"}
    raise HTTPException(400, "Invalid OTP")

@router.post("/login", response_model=Token)
async def login(user: UserLogin, response: Response, db: Session = Depends(get_db), redis_client = Depends(get_redis)):
    result = await login_user(user.email, user.password, db, redis_client)
    if result:
        response.set_cookie(key="access_token", value=result["access_token"], httponly=True, secure=True)
        return result
    raise HTTPException(401, "Invalid credentials")

@router.post("/logout", response_model=dict)
async def logout(request: Request, response: Response, redis_client = Depends(get_redis)):
    token = request.cookies.get("access_token")
    if token:
        await logout_user(token, redis_client)
    response.delete_cookie(key="access_token", httponly=True, secure=True)
    return {"message": "Logged out"}

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.get("/", response_model=UserListResponse)
async def list_users(db: Session = Depends(get_db)):
    users = await get_all_users(db)
    return {"users": users}

@router.put("/{user_id}", response_model=UserResponse)
async def edit_user(user_id: str, user_update: UserUpdate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    updated_user = await update_user(user_id, user_update.name, user_update.profile_picture_url, user_update.password, db, current_user)
    if not updated_user:
        raise HTTPException(404, "User not found")
    return updated_user

@router.post("/forgot-password", response_model=dict)
async def forgot_password_endpoint(request: ForgotPasswordRequest, db: Session = Depends(get_db), redis_client = Depends(get_redis)):
    user_id = await forgot_password(request.email, db, redis_client)
    return {"message": "Reset password OTP sent", "user_id": user_id.id}

@router.post("/reset-password", response_model=dict)
async def reset_password_endpoint(request: ResetPasswordRequest, db: Session = Depends(get_db), redis_client = Depends(get_redis)):
    if await reset_password(request.email, request.otp, request.new_password, db, redis_client):
        return {"message": "Password reset successfully"}
    raise HTTPException(400, "Invalid OTP or email")