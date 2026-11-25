from core.config import settings
from core.logger import get_logger

log = get_logger(__name__)


def test_check_access(page):
    page.goto("/")
    content = page.content()
    log.info("Размер HTML: %d символов", len(content))
    assert "Forbidden" not in content, "Сервер вернул 403 Forbidden"