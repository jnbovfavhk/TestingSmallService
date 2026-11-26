import allure
from playwright.sync_api import Locator, Page, expect

from core.logger import get_logger

log = get_logger(__name__)


class BaseElement:
    """Базовая обёртка над элементом Playwright."""

    def __init__(self, page: Page, locator: str):
        self.page = page
        self.locator = page.locator(locator)

    def click(self, description: str = "Клик") -> None:
        log.info("%s: %s", description, self.locator)
        with allure.step(f"{description}: {self.locator}"):
            self.locator.click()

    def click_first(self, description: str = "Клик по первому элементу") -> None:
        """Клик по первому найденному элементу (обход strict mode)."""
        log.info("%s: %s (first)", description, self.locator)
        with allure.step(f"{description}: {self.locator} (first)"):
            self.locator.first.click()

    def fill(self, value: str, description: str = "Ввод текста") -> None:
        log.info("%s: %s = %s", description, self.locator, "***" if "пароль" in description.lower() else value)
        with allure.step(f"{description}: {self.locator}"):
            self.locator.fill(value)

    def get_text(self) -> str:
        text = self.locator.text_content() or ""
        log.debug("Текст элемента %s: %s", self.locator, text)
        return text

    def expect_visible(self, timeout: int = 5000) -> None:
        log.debug("Ожидание видимости: %s", self.locator)
        expect(self.locator).to_be_visible(timeout=timeout)

    def expect_text(self, expected: str, timeout: int = 5000) -> None:
        log.debug("Ожидание текста '%s' в %s", expected, self.locator)
        expect(self.locator).to_have_text(expected, timeout=timeout)

    def is_visible(self) -> bool:
        try:
            self.locator.wait_for(state="visible", timeout=1000)
            return True
        except Exception:
            return False

    @property
    def first(self):
        """Возвращает первый найденный элемент (аналог .first у локатора)."""
        # Возвращаем нативный локатор Playwright для первого элемента
        return self.locator.first
