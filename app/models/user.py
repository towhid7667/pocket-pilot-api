from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.sqlite import VARCHAR
from app.database import Base
import uuid
from datetime import datetime
class User(Base):
    __tablename__ = "users"
    id = Column(VARCHAR(255), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False) 
    profile_picture_url = Column(String, nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False) 
    session_token = Column(String, nullable=True) 
    is_verified = Column(Boolean, default=False) 