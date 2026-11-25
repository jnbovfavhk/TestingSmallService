import allure
import pytest
from playwright.sync_api import sync_playwright

from core.config import REPORTS_DIR, settings
from core.logger import get_logger

log = get_logger(__name__)


@pytest.fixture(scope="session")
def playwright_instance():
    log.info("Запуск Playwright")
    with sync_playwright() as p:
        yield p
    log.info("Остановка Playwright")


@pytest.fixture(scope="session")
def browser(playwright_instance):
    log.info(
        "Старт браузера %s (headless=%s, slow_mo=%s ms)",
        settings.browser, settings.headless, settings.slow_mo_ms,
    )
    browser_type = getattr(playwright_instance, settings.browser)
    browser = browser_type.launch(
        headless=settings.headless,
        slow_mo=settings.slow_mo_ms,
        args=["--disable-blink-features=AutomationControlled"],
    )
    yield browser
    browser.close()
    log.info("Браузер закрыт")


@pytest.fixture
def context(browser):
    """Чистая сессия на каждый тест + маскировка под обычный браузер."""
    log.debug("Создание нового контекста (сессия не наследуется)")
    ctx = browser.new_context(
        base_url=settings.base_url,
        locale="ru-RU",
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        extra_http_headers={
            "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        },
    )
    # Прячем признак автоматизации
    ctx.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    ctx.set_default_timeout(settings.timeout_ms)
    ctx.set_default_navigation_timeout(settings.nav_timeout_ms)
    yield ctx
    ctx.close()
    log.debug("Контекст закрыт")


@pytest.fixture
def page(context, request):
    page = context.new_page()
    log.info("Тест: %s", request.node.name)
    yield page

    # скриншот при падении
    failed = getattr(request.node, "rep_call", None)
    if failed is not None and failed.failed:
        safe_name = request.node.name.replace("/", "_").replace("\\", "_")
        path = REPORTS_DIR / f"{safe_name}.png"
        try:
            page.screenshot(path=str(path), full_page=True)
            allure.attach.file(
                str(path),
                name="screenshot-on-failure",
                attachment_type=allure.attachment_type.PNG,
            )
            log.error("Скриншот сбоя сохранён: %s", path)
        except Exception as exc:
            reason = f"Скриншот недоступен: {type(exc).__name__}: {exc}"
            allure.attach(reason, name="screenshot-unavailable",
                          attachment_type=allure.attachment_type.TEXT)
            log.error(reason)

    page.close()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def pytest_sessionstart(session):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "allure-results").mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "allure-results" / "environment.properties").write_text(
        "\n".join([
            f"Base.URL={settings.base_url}",
            f"Browser={settings.browser}",
            f"Headless={settings.headless}",
            f"Timeout.ms={settings.timeout_ms}",
            f"Log.Level={settings.log_level}",
        ]),
        encoding="utf-8",
    )