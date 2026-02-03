from fastapi import Depends, HTTPException, status,Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from app.core.database import get_session
from app.models.user_model import User
from app.auth.jwt import decode_access_token

http_bearer = HTTPBearer(auto_error=False)

def get_current_user(access_token : str | None = Cookie(default=None),session: Session = Depends(get_session)):
    # print("im inside get user account")
    # print(access_token)
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    token = access_token
    # print("this is from get user auth.py")
    # print(token)
    try:
        # print("before payload")
        payload = decode_access_token(token)
        # print("after payload")
        # print(payload)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")
        user = session.get(User, user_id)
        if not user or user.is_deleted or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")
        return user.id
    except HTTPException:
        raise
    except Exception as e:
        print("Error decoding token:", e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.")
