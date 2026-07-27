"""Environment-backed settings, loaded once and cached."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration; values come from the environment or `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./managining.db",
        description="Async SQLAlchemy connection URL for the application database.",
    )
    session_secret: str = Field(
        default="change-me",
        description="Secret used to sign session cookies. Must be overridden in production.",
    )
    cookie_secure: bool = Field(
        default=False,
        description="Send the session cookie over HTTPS only. Enable in production.",
    )
    cookie_samesite: str = Field(
        default="none",
        description=(
            "SameSite policy for the session cookie. 'none' lets the standalone "
            "frontend (a different origin) send it; browsers require Secure with it, "
            "but exempt localhost so dev works over http."
        ),
    )
    frontend_origin: str = Field(
        default="http://localhost:5173",
        description=(
            "Comma-separated list of origins allowed to call the API with "
            "credentials (CORS). Include both the local dev origin and the "
            "deployed frontend origin (e.g. https://you.github.io)."
        ),
    )

    @property
    def frontend_origins(self) -> list[str]:
        """The CORS allow-list, split from the comma-separated setting."""
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]

    sql_echo: bool = Field(
        default=False,
        description="When true, SQLAlchemy logs every statement it emits. Debugging only.",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the single Settings instance, parsed on first call."""
    return Settings()
