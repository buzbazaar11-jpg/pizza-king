from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/youngmalang"
    SECRET_KEY: str = "supersecret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REDIS_URL: str = "redis://localhost:6379"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    CENTER_LAT: float = 33.5651
    CENTER_LNG: float = 73.1486
    MAX_DELIVERY_RADIUS_KM: float = 7.0
    APP_NAME: str = "Young Malang"
    CREDIT: str = "Software Developed by AM Enterprises / 03173712950"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
