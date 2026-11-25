from core.config import settings

MASK = "***"


def mask_value(value: str, keep: int = 0) -> str:
    """Для параметров отчёта: логин -> u***t, пароль -> ***."""
    if not value:
        return "<empty>"
    if len(value) <= keep * 2:
        return MASK
    return f"{value[:keep]}{MASK}{value[-keep:]}" if keep else MASK


def mask_secrets(text: str) -> str:
    for secret in settings.secrets:
        text = text.replace(secret, MASK)
    return text