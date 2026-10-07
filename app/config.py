"""
config.py — Application configuration using pydantic-settings.
Reads from a .env file automatically; all settings can be overridden
via environment variables (takes precedence over .env).
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────
    db_host: str = Field("localhost", description="PostgreSQL host")
    db_port: int = Field(5432, description="PostgreSQL port", ge=1, le=65535)
    db_name: str = Field("sports_club_db", description="Database name")
    db_user: str = Field("postgres", description="Database user")
    db_password: str = Field("password", description="Database password")

    # Connection pool sizing
    db_pool_min: int = Field(2, ge=1, description="Minimum pool connections")
    db_pool_max: int = Field(10, ge=1, description="Maximum pool connections")
    # Seconds to wait for a connection from the pool before raising
    db_pool_timeout: float = Field(30.0, ge=1.0, description="Pool connection timeout (s)")
    # Seconds to wait for the pool to open before giving up at startup
    db_connect_timeout: float = Field(10.0, ge=1.0, description="DB connect timeout at startup (s)")

    # ── Application ───────────────────────────────────────────────────────
    app_host: str = Field("0.0.0.0", description="Bind host")
    app_port: int = Field(8000, ge=1, le=65535, description="Bind port")
    # In production set debug=false so stack traces are never sent to clients
    debug: bool = Field(True, description="Enable debug mode (never true in production)")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
