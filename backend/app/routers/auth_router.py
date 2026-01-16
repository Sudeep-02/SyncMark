from fastapi import APIRouter, Depends, HTTPException, Header, status, Request, Cookie, Response
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.models.device_model import Device
from app.core.database import get_session
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


@router.post("/login")
def login(
    login_data: LoginRequest,
    request: Request,
    response: Response,
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
            Device.device_id == login_data.device_id,
            Device.user_id == user.id,
        )
        existing_device = session.exec(device_query).first()

        device_id = getattr(login_data, "device_id", None)
        if device_id is None:
            device_id = uuid.uuid4()

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
    device_id: uuid.UUID = Header(..., alias="device-id"),
    refresh_token: str = Cookie(...),
    session: Session = Depends(get_session),
):
    try:
        refresh_payload = decode_refresh_token(refresh_token)

        from uuid import UUID

        user_id_str = refresh_payload.get("sub")
        if not user_id_str:
            raise HTTPException(401, "Invalid refresh token")

        try:
            user_uuid = UUID(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(400, "Invalid user id in token")

        refresh_token_record = TokenService.validate_refresh_token(
            refresh_token, session
        )

        new_encoded_refresh, new_token_meta = create_refresh_token_raw(user_id_str, device_id)

        TokenService.revoke_refresh_token_by_jti(
            refresh_token_record.jti, session
        )

        TokenService.store_refresh_token(
            raw_encoded_token=new_encoded_refresh,
            meta=new_token_meta,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
            session=session,
            expires_at=new_token_meta.get("exp"),
        )

        response.set_cookie(
            key="refresh_token",
            value=new_encoded_refresh,
            httponly=True,
            secure=False,
            samesite="lax",
            expires=new_token_meta["exp"],
        )

        new_access_token = create_access_token(user_id_str, device_id)

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
    refresh_token: str = Cookie(None),
    session: Session = Depends(get_session),
):
    if access_token:
        try:
            access_payload = decode_access_token(access_token)
            user_id = access_payload.get("sub")

            user = session.get(User, user_id)
            if user and not user.is_deleted:
                return user
        except Exception:
            pass

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        refresh_token_record = TokenService.validate_refresh_token(
            refresh_token, session
        )
        user = session.get(User, refresh_token_record.user_id)

        if not user or user.is_deleted:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except HTTPException:
        raise
