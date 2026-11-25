from playwright.sync_api import Page

from core.logger import get_logger

log = get_logger(__name__)


class BasePage:
    """Базовый класс для Page Object."""

    def __init__(self, page: Page):
        self.page = page

    def open(self, url: str = "/") -> None:
        log.info("Открытие страницы: %s", url)
        self.page.goto(url)

    @property
    def title(self) -> str:
        return self.page.title()