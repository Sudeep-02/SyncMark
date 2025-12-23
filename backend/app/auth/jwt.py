from datetime import datetime, timedelta, timezone  
import jwt                                       
from fastapi.security import OAuth2PasswordBearer
from app.schemas.base import TokenData          
from app.core.setting import settings
from uuid import UUID,uuid4
from typing import Tuple


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#this searching for access_token generated for first time when logged in 
#so it  is "login" endpoint same as login page or acess_token creation function 


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM               # the algorithm used to sign the token
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES   # how long a token lasts, here: 30 minutes
REFRESH_SECRET = settings.REFRESH_SECRET
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()  # e.g., {'sub': username}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "jti": str(uuid4())}) # set expiration claim
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

    
def create_refresh_token_raw(user_id: UUID, expires_days: int = REFRESH_TOKEN_EXPIRE_DAYS) -> Tuple[str, dict]:
    
    raw_token = str(uuid4()) + str(uuid4())  
    jti_val = str(uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=expires_days)
    

    payload = {
        "sub": str(user_id),
        "jti": jti_val,
        "exp": expire,
        "token_value": raw_token  
    }
    
    encoded = jwt.encode(payload, REFRESH_SECRET, algorithm=ALGORITHM)
    
    return encoded,payload


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def decode_refresh_token(token: str) -> dict:
    return jwt.decode(token, REFRESH_SECRET, algorithms=[ALGORITHM])

    
# def get_current_user(token:str = Depends(oauth2_scheme),session: Session = Depends(get_session)):
#     # (token: Annotated[str, Depends(oauth2_scheme)]):
#     #this is how annotated works
#     credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate":"Bearer"})
#     token_data = verify_access_token(token,credentials_exception)
    
#     statement = select(User.id,User.email,User.created_at).where(User.id == token_data.id)
#     result = session.exec(statement).first()
    
#     return result