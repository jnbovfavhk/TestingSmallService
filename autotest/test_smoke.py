import allure

from core.config import settings
from core.logger import get_logger

log = get_logger(__name__)


@allure.title("Smoke: главная страница открывается")
@allure.description("Проверка, что сайт доступен и главная страница загружается")
def test_smoke(page):
    log.info("Открываю %s", settings.base_url)
    page.goto("/")
    log.debug("Заголовок: %s", page.title())
    assert page.title() != ""