from pydantic import BaseSettings


class Settings(BaseSettings):
    host: str = '127.0.0.1'
    port: int = 8080

    class Config:
        env_file = '.env'


settings = Settings()
