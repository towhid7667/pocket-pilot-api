from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.auth import hash_password, verify_password, create_access_token, get_redis
from app.utils.tasks import generate_otp, send_welcome_email_task, send_otp_email_task, send_reset_password_otp_email_task
from app.utils.telegram import send_telegram_message

async def register_user(email: str, password: str, name: str, profile_picture_url: str | None, db: Session, redis_client):
    try:
        password_hash = hash_password(password)
        user = User(email=email, password_hash=password_hash, name=name, profile_picture_url=profile_picture_url)
        db.add(user)
        db.commit()
        otp = generate_otp()
        await redis_client.setex(f"otp:{user.id}", 600, otp)
        send_otp_email_task.delay(email, otp)
        send_welcome_email_task.delay(email)
        return user
    except Exception as error:
        error_msg = f"Error in register_user: {str(error)}"
        print(error_msg)
        send_telegram_message(error_msg)
        raise


async def verify_user(user_id: str, otp: str, db: Session, redis_client):
    try:
        stored_otp = await redis_client.get(f"otp:{user_id}")    
        if stored_otp == otp:
            user = db.query(User).filter(User.id == user_id).first()
            user.is_verified = True
            db.commit()
            await redis_client.delete(f"otp:{user_id}")
            return True
        return False
    except Exception as error:
        error_msg = f"Error in verify_user: {str(error)}"
        print(error_msg)
        send_telegram_message(error_msg)
        raise
        
async def login_user(email: str, password: str, db: Session, redis_client):
    try:
        user = db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.password_hash) and user.is_verified:
            token = create_access_token({"sub" : user.email})        
            user.session_token = token
            db.commit()
            return {"access_token": token, "token_type": "bearer", "user": user}
        return None
    except Exception as error:
        error_msg = f"Error in login_user: {str(error)}"
        print(error_msg)
        send_telegram_message(error_msg)
        raise

async def logout_user(token: str, redis_client):
      try:
          await redis_client.setex(f"blacklist:{token}", 1800, "true")
      except Exception as error:
          error_msg = f"Error in logout_user: {str(error)}"
          print(error_msg)
          send_telegram_message(error_msg)
          raise   

async def get_user_by_id(user_id: str, db: Session):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with id {user_id} not found") 
        return user
    except Exception as error:
        error_msg = f"Error in get_user_by_id: {str(error)}"
        print(error_msg)
        send_telegram_message(error_msg)
        raise

async def get_all_users(db: Session):
    try:
        users = db.query(User).all()
        return users
    except Exception as error:
        error_msg = f"Error in get_all_users: {str(error)}"
        print(error_msg)
        send_telegram_message(error_msg)
        raise



async def update_user(user_id: str, name: str | None, profile_picture_url: str | None, password: str | None, db: Session, current_user_email: str):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with id {user_id} not found")

        if user.email != current_user_email:
            raise ValueError("You can only update your own profile")

        if name is not None:
            user.name = name

        if profile_picture_url is not None:  
            user.profile_picture_url = profile_picture_url

        if password is not None:
            user.password_hash = hash_password(password)

        db.commit()
        db.refresh(user)
        return user
    except Exception as error:
        error_msg = f"Error in update_user: {str(error)}"
        print(error_msg)
        send_telegram_message(error_msg)
        raise

async def forgot_password(email: str, db: Session, redis_client):
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError(f"User with email {email} not found")
        otp = generate_otp()
        await redis_client.setex(f"reset_otp:{user.id}", 600, otp)
        send_reset_password_otp_email_task.delay(email, otp)
        return user
    except Exception as error:
        error_msg = f"Error in forgot_password: {str(error)}"
        print(error_msg)
        send_telegram_message(error_msg)
        raise

async def reset_password(email: str, otp: str, new_password: str, db: Session, redis_client):  
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError(f"User with email {email} not found")
        stored_otp = await redis_client.get(f"reset_otp:{user.id}")
        if stored_otp != otp: 
            raise ValueError("Invalid OTP")
        user.password_hash = hash_password(new_password)
        db.commit()
        await redis_client.delete(f"reset_otp:{user.id}")
        return user
    except Exception as error:
        error_msg = f"Error in reset_password: {str(error)}"
        print(error_msg)
        send_telegram_message(error_msg)
        raise 