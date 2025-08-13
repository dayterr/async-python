import os
from logging import config as logging_config

from pydantic import BaseSettings, PostgresDsn

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_HOST = os.getenv('PROJECT_HOST', '127.0.0.1')
PROJECT_PORT = os.getenv('PROJECT_PORT', '8080')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):
    app_title: str = 'url-shortener'
    database_dsn: PostgresDsn
    project_name: str = os.getenv('PROJECT_NAME', 'url-shortener')

    class Config:
        env_file = '.env'


app_settings = AppSettings()
