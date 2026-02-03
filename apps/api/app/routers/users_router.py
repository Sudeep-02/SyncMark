from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.deps.auth import get_current_user
from app.core.database import get_session
from app.schemas.user_schema import UserRead, UserUpdate
from app.models.user_model import User
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def get_user(current_user: User = Depends(get_current_user)):
    # current_user is loaded from DB already
    return UserRead(id=current_user.id, email=current_user.email, username=current_user.username, is_active=current_user.is_active)


@router.patch("/me", response_model=UserRead)
def update_user(data: UserUpdate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        user = UserService.update_user(current_user.id, data, session)
        return UserRead(id=user.id, email=user.email, username=user.username, is_active=user.is_active)
    except HTTPException:
        raise


@router.delete("/me")
def delete_user(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    try:
        UserService.soft_delete_user(current_user.id, session)
        return {"message": "Account soft-deleted."}
    except HTTPException:
        raise
