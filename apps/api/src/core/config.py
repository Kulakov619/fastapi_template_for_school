import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


class Settings(BaseSettings):
    dev_enviroment: bool = True
    db_engine_echo: bool = False
    service_name: str = "lib_api"
    redis_host: str = ...
    redis_port: int = ...
    db_name: str = ...
    db_host: str = ...
    db_port: int = ...
    db_user: str = ...
    db_password: str = ...
    request_id_excluded_urls: list[str] = ["/api/v1/auth/health"]

    @property
    def db_full_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
