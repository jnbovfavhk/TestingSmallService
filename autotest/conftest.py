import pytest

from ui.pages.login_page import LoginPage


@pytest.fixture
def login_page(page):
    """Фикстура для страницы авторизации."""
    return LoginPage(page)