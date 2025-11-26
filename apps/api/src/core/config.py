import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="test_")
    dev_enviroment: bool = False
    service_name: str = "service"
    redis_host: str = ...
    redis_port: int = ...
    db_name: str = ...
    db_host: str = ...
    db_port: int = ...
    db_user: str = ...
    db_password: str = ...

    @property
    def db_full_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
