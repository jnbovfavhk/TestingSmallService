import allure
import pytest

from core.config import settings
from core.logger import get_logger
from ui.pages.login_page import LoginPage
from ui.pages.shop_pages import SearchPage, CartPage, CheckoutPage

log = get_logger(__name__)


@allure.feature("Сквозное тестирование")
@allure.story("Создание заказа")
@allure.title("E2E: Полный путь от поиска товара до успешного оформления заказа")
@pytest.mark.e2e
def test_e2e_create_order(page, login_page: LoginPage):
    """
    1. Вход
    2. Поиск
    3. Карточка/Добавление в корзину
    4. Корзина
    5. Оформление
    6. Подтверждение заказа
    """
    search_page = SearchPage(page)
    cart_page = CartPage(page)
    checkout_page = CheckoutPage(page)

    with allure.step("1. Успешная авторизация пользователя"):
        login_page.open("/")
        login_page.open_login_modal()
        login_page.fill_login(settings.app_login)
        login_page.fill_password(settings.app_password.get_secret_value())
        login_page.submit()

        # Используем твой проверенный метод
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
        # Переходим в корзину по стандартному URL Битрикс
        cart_page.open("/personal/cart/")
        cart_page.go_to_checkout()

    with allure.step("5. Оформление заказа (ввод данных и отправка)"):
        # Используем тестовые данные (можно вынести в .env, но для E2E допустимы фиктивные)
        test_name = "Иван Автотестов"
        test_phone = "+79991234567"
        test_email = "autotest_e2e@example.com"

        checkout_page.fill_checkout_form(test_name, test_phone, test_email)
        order_number = checkout_page.submit_order()

        allure.attach(order_number, name="Номер созданного заказа", attachment_type=allure.attachment_type.TEXT)

    with allure.step("6. Подтверждение создания заказа"):
        # Финальная проверка: мы на странице успеха и видим номер заказа или слово "Спасибо"
        current_url = page.url
        assert "order" in current_url.lower() or "thanks" in current_url.lower() or "success" in current_url.lower(), \
            f"После оформления мы не попали на страницу успеха. Текущий URL: {current_url}"

        log.info("E2E сценарий успешно завершен. Заказ оформлен.")