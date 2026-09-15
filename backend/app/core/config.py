from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "JobIQ API"
    app_version: str = "0.1.0"
    environment: str = "development"
    frontend_url: str = "http://localhost:3000"

    jwt_secret_key: str = "dev-only-change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    database_url: str = "postgresql+psycopg://jobiq:jobiq_dev_password@localhost:5432/jobiq"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()