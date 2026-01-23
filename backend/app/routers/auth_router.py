from fastapi import APIRouter, Depends, HTTPException, Header, status, Request, Cookie, Response
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.models.device_model import Device
from app.core.database import get_session
from app.deps.device import get_device_id
from app.deps.login_rate_limit import login_rate_limit

from app.schemas.user_schema import (
    UserCreate,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserOut,
)
from app.schemas.base import TokenResponse
from app.services.user_service import UserService
from app.models.user_model import User
from app.auth.jwt import (
    create_access_token,
    create_refresh_token_raw,
    decode_refresh_token,
    decode_access_token,
)
from app.services.token_service import TokenService
import uuid

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut)
def register(register_data: UserCreate, session: Session = Depends(get_session)):
    try:
        user = UserService.create_user(register_data, session)
        return user
    except HTTPException:
        raise


@router.post("/login",dependencies=[Depends(login_rate_limit)])
def login(
    login_data: LoginRequest,
    request: Request,
    response: Response,
    device_id: uuid.UUID = Depends(get_device_id),
    session: Session = Depends(get_session),
):
    try:
        user = UserService.authenticate_user(
            login_data.email, login_data.password, session
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        device_query = select(Device).where(
            Device.device_id == device_id,
            Device.user_id == user.id,
        )
        existing_device = session.exec(device_query).first()

        if not existing_device:
            device = Device(
                device_id=device_id,
                user_id=user.id,
                os=login_data.os,
                android_version=login_data.android_version,
                user_agent=request.headers.get("user-agent"),
                ip=request.client.host if request.client else None,
                last_known_revision=datetime.now(timezone.utc),
            )
            session.add(device)
        else:
            device = existing_device
            device.os = login_data.os
            device.android_version = login_data.android_version
            device.user_agent = request.headers.get("user-agent")
            device.ip = request.client.host if request.client else None
            device.last_known_revision = datetime.now(timezone.utc)

        session.commit()

        encoded_refresh_token, token_meta = create_refresh_token_raw(user.id, device_id)

        TokenService.store_refresh_token(
            raw_encoded_token=encoded_refresh_token,
            meta=token_meta,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
            session=session,
            expires_at=token_meta["exp"],
            device_id = device_id,
        )

        response.set_cookie(
            key="refresh_token",
            value=encoded_refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )

        access_token = create_access_token(user.id, device_id)

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
        )

        return {"message": "Logged in successfully"}

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Login failed.")


@router.post("/refresh")
def refresh_token(
    request: Request,
    response: Response,
    device_id: uuid.UUID = Depends(get_device_id),
    refresh_token: str | None = Cookie(None),
    session: Session = Depends(get_session),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    
    try:
        payload = decode_refresh_token(refresh_token)

        from uuid import UUID

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        
        refresh_token_record = TokenService.validate_refresh_token(
            refresh_token, session
        )

        if refresh_token_record.device_id != device_id:
            raise HTTPException(status_code=401, detail="Device mismatch")
        
        TokenService.revoke_refresh_token_by_jti(
            refresh_token_record.jti, session
        )


        new_refresh_token, new_meta = create_refresh_token_raw(user_id_str, device_id)

        
        TokenService.store_refresh_token(
            raw_encoded_token=new_refresh_token,
            meta=new_meta,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
            session=session,
            expires_at=new_meta.get("exp"),
            device_id=device_id
        )

        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=False, # set True in prod (HTTPS)
            samesite="lax",
            expires=new_meta["exp"],
            path="/",
        )

        new_access_token = create_access_token(user_id_str, device_id)
        
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=False,      # set True in prod
            samesite="lax",
            path="/",
        )

        return {"access_token": new_access_token}

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid refresh token.")


@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str = Cookie(None),
    session: Session = Depends(get_session),
):
    if refresh_token:
        try:
            refresh_payload = decode_refresh_token(refresh_token)
            token_jti = refresh_payload.get("jti")
            if token_jti:
                TokenService.revoke_refresh_token_by_jti(token_jti, session)
        except Exception:
            pass

    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")

    return {"message": "Logged out"}


@router.post("/forgot-password")
def forgot_password(
    reset_request: PasswordResetRequest,
    session: Session = Depends(get_session),
):
    try:
        UserService.request_password_reset(reset_request.email, session)
        return {"message": "If that account exists, a reset link was sent."}
    except HTTPException:
        raise


@router.post("/reset-password")
def reset_password(
    reset_data: PasswordResetConfirm,
    session: Session = Depends(get_session),
):
    try:
        UserService.reset_password(
            reset_data.reset_token,
            reset_data.new_password,
            session,
        )
        return {"message": "Password reset successful."}
    except HTTPException:
        raise


@router.get("/me", response_model=UserOut)
def get_me(
    access_token: str = Cookie(None),
    session: Session = Depends(get_session),
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_access_token(access_token)
        user_id = payload.get("sub")

        user = session.get(User, user_id)
        if not user or user.is_deleted:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except Exception:
        raise HTTPException(status_code=401, detail="Not authenticated")
    