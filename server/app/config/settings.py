from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MYUBER API"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    
    database_url: str = "postgresql://postgres:Venkatesh431971@localhost:5433/myuber_db"

    class Config:
        env_file = ".env"

settings = Settings()