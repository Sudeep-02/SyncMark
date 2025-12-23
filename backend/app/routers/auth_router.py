from fastapi import APIRouter, Depends, HTTPException, status, Request,Cookie,Response
from sqlmodel import Session,select
from datetime import datetime,timezone
from app.models.device_model import Device
from app.core.database import get_session
from app.schemas.user_schema import (
    UserCreate, LoginRequest,
    PasswordResetRequest, PasswordResetConfirm,UserOut
)
from app.schemas.base import TokenResponse
from app.services.user_service import UserService
from app.auth.jwt import create_access_token, create_refresh_token_raw, decode_refresh_token
from app.services.token_service import TokenService
import uuid
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut)
def register(data: UserCreate, session: Session = Depends(get_session)):
    try:
        user = UserService.create_user(data, session)
        return user #{"id": user.id, "email": user.email, "username": user.username}
    except HTTPException:
        raise


@router.post("/login")
def login(data: LoginRequest, request: Request,response: Response, session: Session = Depends(get_session)):
    try:
        
        user = UserService.authenticate_user(data.email, data.password, session)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
        
  
        stmt = select(Device).where(Device.device_id == data.device_id, Device.user_id == user.id)
        device_result = session.exec(stmt).first()
        
        # Use a temporary UUID until frontend sends one
        device_id = getattr(data, "device_id", None)  # maybe None for now
        if device_id is None:
            device_id = uuid.uuid4()  # generate a temporary UUID

        if not device_result:
            device = Device(
                device_id=device_id,
                user_id=user.id,
                os=data.os,
                android_version=data.android_version,
                user_agent=request.headers.get("user-agent"),
                ip=request.client.host if request.client else None,
                last_sync_at=datetime.now(timezone.utc)
            )
            session.add(device)
        else:
            # Update existing device
            device = device_result
            device.os = data.os
            device.android_version = data.android_version
            device.user_agent = request.headers.get("user-agent")
            device.ip = request.client.host if request.client else None
            device.last_login = datetime.now(timezone.utc)

        session.commit()
        
        
        # print("Headers:")
        # for key, value in request.headers.items():
        #     print(f"{key}: {value}")
        # Create jti and raw refresh token (encoded)
        encoded_refresh, metadata = create_refresh_token_raw(user.id)
        # jti=metadata["jti"]
        # sub=metadata["sub"]
        # Store hashed refresh token in DB with metadata
        TokenService.store_refresh_token(
            raw_encoded_token=encoded_refresh,
            meta=metadata,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
            session=session,
            expires_at=metadata["exp"]
        )
        
        response.set_cookie(
            key="refresh_token",
            value=encoded_refresh,
            httponly=True,
            secure=False,   # Don't forget to change to True in production (HTTPS)
            samesite="lax",
            path="/"
        )
        
        
        access_token = create_access_token(data=metadata)
        
        return {"access_token": access_token}
        # return TokenResponse(access_token=access_token, refresh_token=encoded_refresh)
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Login failed.")


@router.post("/refresh")
def refresh_token(request: Request, response:Response, refresh_token: str = Cookie(...),  session: Session = Depends(get_session)):
    try:
        # validate token decode
        payload = decode_refresh_token(refresh_token)
        
        from uuid import UUID

        user_id_str = payload.get("sub")

        if not user_id_str:
            raise HTTPException(401, "Invalid refresh token")

        try:
            user_uuid = UUID(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(400, "Invalid user id in token")
        
        
        # validate against DB (hash)
        rt = TokenService.validate_refresh_token(refresh_token, session)
        
        # issue new tokens: new jti
        new_encoded_refresh, meta = create_refresh_token_raw(user_uuid)
        
        # Revoke old token (single-use refresh tokens)
        TokenService.revoke_refresh_token_by_jti(rt.jti, session)
        
        # Store new refresh token record
        TokenService.store_refresh_token(
            raw_encoded_token=new_encoded_refresh,
            meta=meta,
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
            session=session,
            expires_at=meta.get("exp")
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_encoded_refresh,
            httponly=True,
            secure=False,   
            samesite="lax",
            expires=meta["exp"]
        )

        
        access_token = create_access_token(data=meta)
        
        
        return {"access_token": access_token}
        # return TokenResponse(access_token=access_token, refresh_token=new_encoded_refresh)
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid refresh token.")


@router.post("/logout")
def logout(refresh_token: str = Cookie(...), session: Session = Depends(get_session)):
    try:
        # decode refresh token to get jti
        payload = decode_refresh_token(refresh_token)
        jti = payload.get("jti")
        if not jti:
            raise HTTPException(status_code=400, detail="Invalid refresh token.")
        TokenService.revoke_refresh_token_by_jti(jti, session)
        return {"message": "Logged out."}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid refresh token.")


@router.post("/forgot-password")
def forgot_password(data: PasswordResetRequest, session: Session = Depends(get_session)):
    try:
        UserService.request_password_reset(data.email, session)
        return {"message": "If that account exists, a reset link was sent."}
    except HTTPException:
        raise


@router.post("/reset-password")
def reset_password(data: PasswordResetConfirm, session: Session = Depends(get_session)):
    try:
        user = UserService.reset_password(data.reset_token, data.new_password, session)
        return {"message": "Password reset successful."}
    except HTTPException:
        raise
