from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 60
    COOKIE_SECURE: bool = False  # в проде на HTTPS выставить True в .env
    # Файлы заданий. Пока это папка, которую раздаёт сам бэкенд; позже — S3/MinIO
    STORAGE_DIR: str = 'storage'
    STORAGE_PUBLIC_URL: str = '/storage'  # префикс ссылок на файлы в ответах API

    @property
    def DATABASE_URL(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()