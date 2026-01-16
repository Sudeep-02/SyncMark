# app/core/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    
    SECRET_KEY: str
    REFRESH_SECRET:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 30 min
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
   

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()  # type: ignore[call-arg]
