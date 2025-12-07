import logging
from datetime import UTC

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

TIMEZONE = UTC
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# logger setup
LOG_FORMAT = (
    "%(levelname) -10s %(asctime)s %(name) -30s %(funcName) "
    "-35s %(lineno) -5d: %(message)s"
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Logger
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # App settings
    root_path: str = Field(default="", alias="ROOT_PATH")
    cors_origins: list[str] = Field(default=["*"], alias="CORS_ORIGINS")
    allowed_hosts: list[str] = Field(default=["*"], alias="ALLOWED_HOSTS")
    debug: bool = Field(default=False)

    # PostgreSQL settings
    postgres_host: str = Field(alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")

    @field_validator("cors_origins", "allowed_hosts", mode="before")
    @classmethod
    def parse_comma_separated(cls, v):
        """Parse comma-separated strings into lists."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",")]
        return v

    @property
    def sqlalchemy_database_url(self) -> str:
        """Build SQLAlchemy database URL from components."""
        dsn = PostgresDsn.build(
            scheme="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )
        return str(dsn)


def setup_logging(log_level: str) -> None:
    """Configure logging based on settings."""
    logging.basicConfig(format=LOG_FORMAT, level=log_level.upper())


# Initialize settings
settings = Settings()
