import os
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn

from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):
    app_title: str = 'file-storage'
    database_dsn: PostgresDsn = 'postgresql+asyncpg://postgres:postgressheli@db:5432/postgres_fastapi'
    project_name: str = os.getenv('PROJECT_NAME', 'file-storage')
    project_host = os.getenv('PROJECT_HOST', '127.0.0.1')
    project_port = os.getenv('PROJECT_PORT', '8080')

    class Config:
        env_file = '.env'


app_settings = AppSettings()
