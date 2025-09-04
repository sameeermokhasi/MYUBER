from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    app_name: str = "MYUBER API"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
