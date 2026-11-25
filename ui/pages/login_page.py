from playwright.sync_api import Page, expect

from core.logger import get_logger
from ui.base_element import BaseElement
from ui.base_page import BasePage

log = get_logger(__name__)


class LoginPage(BasePage):
    """Page Object для страницы авторизации."""

    # Локаторы
    LOGIN_BUTTON_HEADER = "a[data-name='auth']:visible"  # кнопка "Войти" в шапке
    MODAL = "form[action='/auth/?login=yes']"  # модальное окно
    LOGIN_FIELD = "input[name='USER_LOGIN']"
    PASSWORD_FIELD = "input[name='USER_PASSWORD']"
    SUBMIT_BUTTON = "button.auth__bottom-btn[type='submit']"
    ERROR_MESSAGE = "label.error, .alert"
    USER_NAME_HEADER = ".header-cabinet__name"
    CLOSE_BUTTON = "span.top-close"


    # LOGIN_BUTTON_HEADER = "a[href='/login']"
    #
    # # Сама форма и поля
    # MODAL = ".page-title"  # На этом сайте логин на отдельной странице, а не в модалке
    # LOGIN_FIELD = "input[name='Email']"
    # PASSWORD_FIELD = "input[name='Password']"
    # SUBMIT_BUTTON = "input[type='submit'][value='Log in']"
    #
    # # Ошибка и успех
    # ERROR_MESSAGE = ".message-error"
    # USER_NAME_HEADER = "a[href='/logout']"  # После входа появляется кнопка "Log out"

    def __init__(self, page: Page):
        super().__init__(page)
        self.login_button = BaseElement(page, self.LOGIN_BUTTON_HEADER)
        self.login_field = BaseElement(page, self.LOGIN_FIELD)
        self.password_field = BaseElement(page, self.PASSWORD_FIELD)
        self.submit_button = BaseElement(page, self.SUBMIT_BUTTON)
        self.error_message = BaseElement(page, self.ERROR_MESSAGE)
        self.user_name = BaseElement(page, self.USER_NAME_HEADER)
        self.close_button = BaseElement(page, self.CLOSE_BUTTON)

    def open_login_modal(self) -> None:
        """Открыть модальное окно авторизации."""
        log.info("Открытие модального окна авторизации")
        self.login_button.click("Открытие модалки логина")
        self.page.locator(self.MODAL).wait_for(state="visible", timeout=5000)

    def open_login_page(self) -> None:
        self.page.locator(self.LOGIN_BUTTON_HEADER).click()
        self.page.locator(self.MODAL).wait_for(state="visible", timeout=5000)

    def fill_login(self, login: str) -> None:
        """Заполнить поле логина."""
        self.login_field.fill(login, "Ввод логина")

    def fill_password(self, password: str) -> None:
        """Заполнить поле пароля."""
        self.password_field.fill(password, "Ввод пароля")

    def submit(self) -> None:
        """Нажать кнопку входа."""
        self.submit_button.click("Отправка формы")

    def get_error_text(self) -> str:
        """Получить текст ошибки."""
        return self.error_message.get_text()

    def is_error_visible(self) -> bool:
        """Проверить, видна ли ошибка."""
        return self.error_message.is_visible()

    def is_user_logged_in(self) -> bool:
        """Проверить, что пользователь авторизован (имя в шапке)."""
        try:
            self.page.wait_for_timeout(1500)

            if "?login=yes" in self.page.url:
                return True

            login_btn_hidden = not self.page.locator(self.LOGIN_BUTTON_HEADER).is_visible()
            if login_btn_hidden:
                log.info("Вход подтвержден по исчезновению кнопки 'Войти'")
                return True

        except Exception as e:
            log.error("Ошибка при проверке авторизации: %s", e)
            return False

    def close_modal(self) -> None:
        """Закрыть модальное окно."""
        self.close_button.click("Закрытие модалки")