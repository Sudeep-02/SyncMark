from uuid import uuid4,UUID
from datetime import datetime, timedelta,timezone
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.auth.security import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token_raw
# from app.utils.email_utils import send_reset_email
from app.services.token_service import TokenService


class UserService:
    @staticmethod
    def create_user(data: UserCreate, session: Session) -> User:
        try:
            existing = session.exec(select(User).where(User.email == data.email)).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered.")

            user = User(
                email=data.email,
                username=data.username,
                password_hash=hash_password(data.password_hash),
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except HTTPException:
            raise
        except Exception:
            session.rollback()
            raise HTTPException(status_code=500, detail="Failed to create user.")

    @staticmethod
    def authenticate_user(email: str, password: str, session: Session) -> User | None:
        try:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user or user.is_deleted:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            if not verify_password(password, user.password_hash):
                return None
            return user
        except HTTPException:
            raise
        except Exception as e:
            # Optional: log unexpected errors
            return None

    @staticmethod
    def update_user(user_id: UUID, data: UserUpdate, session: Session) -> User:
        try:
            user = session.get(User, user_id)
            if not user or user.is_deleted:
                raise HTTPException(status_code=404, detail="User not found.")
            if data.username:
                user.username = data.username
            user.updated_at = datetime.now(timezone.utc)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except HTTPException:
            raise
        except Exception:
            session.rollback()
            raise HTTPException(status_code=500, detail="Failed to update user.")

    @staticmethod
    def soft_delete_user(user_id: UUID, session: Session):
        try:
            user = session.get(User, user_id)
            if not user or user.is_deleted:
                raise HTTPException(status_code=404, detail="User not found.")
            user.is_deleted = True
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            session.add(user)
            session.commit()
        except HTTPException:
            raise
        except Exception:
            session.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete user.")

    @staticmethod
    def request_password_reset(email: str, session: Session):
        try:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                return  # do not reveal presence
            reset_token = str(uuid4())
            user.reset_token = reset_token
            user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
            session.add(user)
            session.commit()
            # send_reset_email(email, reset_token)
        except Exception:
            session.rollback()
            raise HTTPException(status_code=500, detail="Failed to process password reset request.")

    @staticmethod
    def reset_password(reset_token: str, new_password: str, session: Session):
        try:
            user = session.exec(select(User).where(User.reset_token == reset_token)).first()
            if not user:
                raise HTTPException(status_code=400, detail="Invalid reset token.")
            if not user.reset_token_expires_at or user.reset_token_expires_at < datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="Reset token expired.")
            user.hashed_password = hash_password(new_password)
            user.reset_token = None
            user.reset_token_expires_at = None
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except HTTPException:
            raise
        except Exception:
            session.rollback()
            raise HTTPException(status_code=500, detail="Failed to reset password.")
