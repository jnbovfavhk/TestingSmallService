import logging
import sys

from core.config import REPORTS_DIR, settings
from core.masking import mask_secrets

_CONFIGURED = False


class _SecretFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = mask_secrets(str(record.getMessage()))
        record.args = ()
        return True


def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = logging.getLevelName(
        "WARNING" if settings.log_level == "WARN" else settings.log_level
    )
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    secret_filter = _SecretFilter()

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    console.addFilter(secret_filter)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(REPORTS_DIR / "run.log", encoding="utf-8")
    file_handler.setFormatter(fmt)
    file_handler.addFilter(secret_filter)
    file_handler.setLevel(logging.DEBUG)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(console)
    root.addHandler(file_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)