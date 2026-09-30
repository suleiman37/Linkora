import os
from dataclasses import dataclass
from dataclasses import field

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    base_url: str = field(
        default_factory=lambda: os.getenv("BASE_URL", "http://localhost:8000")
    )
    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://url_shortener:password@localhost:5432/url_shortener",
        )
    )
    cors_allowed_origins: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            origin.strip()
            for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
            if origin.strip()
        )
    )


settings = Settings()