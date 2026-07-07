from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://monitor:monitor@postgres:5432/monitor"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 720
    initial_admin_email: str = "admin@example.com"
    initial_admin_password: str = "ChangeMe123!"
    initial_admin_name: str = "Network Monitor Admin"
    frontend_url: str = "http://localhost:3000"
    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    return Settings()
