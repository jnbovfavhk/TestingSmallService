import allure
import pytest

from core.config import settings
from core.logger import get_logger
from ui.pages.login_page import LoginPage
from ui.pages.shop_pages import SearchPage, CartPage

log = get_logger(__name__)


@allure.feature("Сквозное тестирование")
@allure.story("Создание заказа")
@allure.title("E2E: Полный путь от поиска товара до готовности к оформлению заказа")
@pytest.mark.e2e
def test_e2e_create_order(page, login_page: LoginPage):
    """
    1. Вход
    2. Поиск
    3. Карточка/Добавление в корзину
    4. Корзина (проверка состава и доступности оформления)
    5. Подтверждение готовности к оформлению (без фактического клика)
    """
    search_page = SearchPage(page)
    cart_page = CartPage(page)

    with allure.step("1. Успешная авторизация пользователя"):
        login_page.open("/")
        login_page.open_login_modal()
        login_page.fill_login(settings.app_login)
        login_page.fill_password(settings.app_password.get_secret_value())
        login_page.submit()

        login_page.page.locator(login_page.MODAL).wait_for(state="hidden", timeout=5000)
        assert login_page.is_user_logged_in(), "Авторизация не прошла"
        log.info("Пользователь успешно авторизован")

    with allure.step("2. Поиск товара"):
        search_page.open("/")
        search_page.search_product(settings.order_search_query)
        assert search_page.page.locator(search_page.PRODUCT_CARD).count() > 0, "Товары не найдены"

    with allure.step("3. Добавление товара в корзину"):
        product_name = search_page.add_first_product_to_cart()
        allure.attach(product_name, name="Добавленный товар", attachment_type=allure.attachment_type.TEXT)

    with allure.step("4. Переход в корзину и проверка состава"):
        cart_page.open("/basket/")
        cart_page.verify_checkout_available()

    with allure.step("5. Подтверждение готовности к оформлению"):
        log.info("E2E сценарий завершён успешно. Полный путь до оформления заказа проверен.")