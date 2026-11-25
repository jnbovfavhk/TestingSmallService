import allure
import pytest

from core.config import settings
from core.dto import LoginData
from core.logger import get_logger

log = get_logger(__name__)

# Наборы данных для тестов авторизации
LOGIN_CASES = [
    LoginData(
        case_id="ТК-А1",
        identifier_kind="username",
        login=settings.app_login,
        password=settings.app_password.get_secret_value(),
        expected_success=True,
        error_class="success",
        description="Успешная авторизация с валидными данными"
    ),
    LoginData(
        case_id="ТК-А2.1",
        identifier_kind="username",
        login="",
        password=settings.app_password.get_secret_value(),
        expected_success=False,
        error_class="empty_login",
        description="Авторизация с пустым логином"
    ),
    LoginData(
        case_id="ТК-А2.2",
        identifier_kind="username",
        login=settings.app_login,
        password="",
        expected_success=False,
        error_class="empty_password",
        description="Авторизация с пустым паролем"
    ),
    LoginData(
        case_id="ТК-А3",
        identifier_kind="username",
        login=settings.app_login,
        password=settings.wrong_password.get_secret_value(),
        expected_success=False,
        error_class="wrong_password",
        description="Авторизация с неверным паролем"
    ),
    LoginData(
        case_id="ТК-А4",
        identifier_kind="username",
        login=settings.unknown_login,
        password=settings.app_password.get_secret_value(),
        expected_success=False,
        error_class="unknown_login",
        description="Авторизация с несуществующим логином"
    ),
]


@allure.feature("Авторизация")
@allure.story("Позитивные сценарии")
@allure.title("ТК-А1: Успешная авторизация")
@pytest.mark.auth
def test_login_success(login_page):
    """Успешная авторизация с валидными данными."""
    log.info("Тест ТК-А1: успешная авторизация")

    with allure.step("Открыть модальное окно авторизации"):
        login_page.open("/")
        login_page.open_login_modal()

    with allure.step("Ввести валидные данные"):
        login_page.fill_login(settings.app_login)
        login_page.fill_password(settings.app_password.get_secret_value())

    with allure.step("Нажать кнопку 'Войти'"):
        login_page.submit()

    with allure.step("Проверить успешный вход"):
        # Ждем, пока модальное окно закроется (признак AJAX-успеха)
        login_page.page.locator(login_page.MODAL).wait_for(state="hidden", timeout=5000)

        # Проверяем, что система считает нас авторизованными
        assert login_page.is_user_logged_in(), "Модальное окно закрылось, но признаки авторизации в шапке не найдены"
        log.info("Успешный вход подтвержден: модалка закрыта, пользователь в системе")

    # with allure.step("Проверить успешный вход"):
    #     # Ждём появления кнопки "Log out", что гарантирует успех
    #     login_page.page.locator(login_page.USER_NAME_HEADER).wait_for(state="visible", timeout=5000)
    #     assert login_page.page.locator(login_page.USER_NAME_HEADER).is_visible(), "Кнопка 'Log out' не появилась"


@allure.feature("Авторизация")
@allure.story("Негативные сценарии")
@allure.title("{case.description}")
@pytest.mark.auth
@pytest.mark.parametrize("case", LOGIN_CASES[1:], ids=[c.case_id for c in LOGIN_CASES[1:]])
def test_login_negative(login_page, case):
    """Негативные сценарии авторизации."""
    log.info("Тест %s: %s", case.case_id, case.description)

    with allure.step(f"Открыть модальное окно авторизации"):
        login_page.open("/")
        login_page.open_login_modal()

    with allure.step("Ввести тестовые данные"):
        if case.login:
            login_page.fill_login(case.login)
        if case.password:
            login_page.fill_password(case.password)

    with allure.step("Нажать кнопку 'Войти'"):
        login_page.submit()

    with allure.step("Проверить отказ во входе"):
        # Проверка, что модалка не закрылась
        assert login_page.page.locator(login_page.MODAL).is_visible(), "Модальное окно закрылось, хотя должен быть отказ"

    with allure.step("Проверить отображение ошибки"):
        # Проверка, что ошибка появилась
        assert login_page.is_error_visible(), "Ошибка не отображается"

    with allure.step("Проверить отсутствие авторизованной сессии"):
        # Проверяем, что модалка всё ещё открыта (вход не произошёл)
        assert login_page.page.locator(
            login_page.MODAL).is_visible(), "Модальное окно закрылось, хотя вход должен быть неуспешным"

        # Проверяем, что в шапке не появились признаки авторизации (кнопка "Выйти" или имя)
        login_button_visible = login_page.page.locator(login_page.LOGIN_BUTTON_HEADER).is_visible()
        assert login_button_visible, "Кнопка 'Войти' исчезла из шапки, хотя авторизация не удалась"

        log.info("Авторизация не произошла: модалка открыта, кнопка 'Войти' на месте")