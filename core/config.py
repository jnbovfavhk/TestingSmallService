from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT_DIR / "reports"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str
    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = True
    slow_mo_ms: int = 0
    timeout_ms: int = 10000
    nav_timeout_ms: int = 30000
    log_level: Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR"] = "INFO"

    app_login: str
    app_password: SecretStr
    wrong_password: SecretStr = SecretStr("wrongpass")
    unknown_login: str = "no_such_user"
    order_search_query: str = ""

    @property
    def secrets(self) -> list:
        """Значения, которые нельзя показывать в логах/отчётах."""
        return [
            s.get_secret_value()
            for s in (self.app_password, self.wrong_password)
            if s.get_secret_value()
        ]


settings = Settings()