from datetime import datetime,timezone
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.Refresh_Token_model import RefreshToken
from app.auth.security import hash_refresh_token
from uuid import UUID as UUIDType


class TokenService:
    @staticmethod
    def store_refresh_token(raw_encoded_token: str, meta: dict, user_agent: str | None, ip: str | None, session: Session, expires_at: datetime | None)-> RefreshToken:
        try:
            token_hash = hash_refresh_token(raw_encoded_token)
            
            user_sub = meta.get("sub")
            jti = meta.get("jti")
            
            if not user_sub or not jti:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing token subject or jti")

            try:
                user_uuid = UUIDType(user_sub)
            except (ValueError, TypeError):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id in token")
            
            rt = RefreshToken(
                user_id=user_uuid,
                jti=jti,
                token_hash=token_hash,
                user_agent=user_agent,
                ip_address=ip,
                expires_at=expires_at,
                revoked=False,
            )
            session.add(rt)
            session.commit()
            session.refresh(rt)
            return rt
        except Exception:
            session.rollback()
            raise HTTPException(status_code=500, detail="Failed to store refresh token.")

    @staticmethod
    def revoke_refresh_token_by_jti(jti: str, session: Session):
        try:
            rt = session.exec(select(RefreshToken).where(RefreshToken.jti == jti)).first()
            if not rt:
                return
            rt.revoked = True
            session.add(rt)
            session.commit()
        except Exception:
            session.rollback()
            raise HTTPException(status_code=500, detail="Failed to revoke refresh token.")

    @staticmethod
    def validate_refresh_token(old_refresh_token: str, session: Session):
        try:
            
            token_hash = hash_refresh_token(old_refresh_token)

            rt = session.exec(select(RefreshToken).where(RefreshToken.token_hash == token_hash)).first()
    
            if not rt:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
            if rt.revoked:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked.")
            if rt.expires_at and rt.expires_at < datetime.now(timezone.utc):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired.")
            return rt
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to validate refresh token.")
