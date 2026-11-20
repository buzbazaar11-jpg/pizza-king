from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    # For Supabase: use the Session Pooler (port 5432) connection string.
    # Format: postgresql+asyncpg://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
    # Get this from: Supabase Dashboard → Project Settings → Database → Connection string → URI
    DATABASE_URL: str = ""  # optional — direct Postgres (SQLAlchemy)

    # ── Supabase REST client (optional) ───────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""

    # ── Auth ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "supersecret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # ── Redis (optional — only used for caching; app works without it) ────────
    REDIS_URL: str = "redis://localhost:6379"

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5173", "http://localhost:3000"]

    # ── Business ──────────────────────────────────────────────────────────────
    CENTER_LAT: float = 33.5651
    CENTER_LNG: float = 73.1486
    MAX_DELIVERY_RADIUS_KM: float = 7.0
    APP_NAME: str = "Pizza King"
    CREDIT: str = "Software Developed by AM Enterprises / 03173712950"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
