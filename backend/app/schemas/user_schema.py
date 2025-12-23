# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.schemas.base import ForbidExtraBase

class UserBase(ForbidExtraBase):
    email: EmailStr
    username: Optional[str] = None
    
class UserCreate(UserBase):
    password_hash: str
    avatar_url: Optional[str] = None

class UserRead(UserBase):
    id: UUID
    is_active: bool


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None



class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: Optional[UUID] = None  # remove optional when working with frontend and same for below
    os:Optional[str] = None
    android_version: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str


class UserOut(BaseModel):
    id: UUID
    username: Optional[str] = None
    email: EmailStr
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

model_config = {
        "from_attributes": True 
    }





