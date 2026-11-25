import allure
from playwright.sync_api import Page, expect

from core.logger import get_logger
from ui.base_element import BaseElement
from ui.base_page import BasePage

log = get_logger(__name__)


class SearchPage(BasePage):
    """Страница поиска и каталога."""
    SEARCH_INPUT = "input[id='title-search-input']"
    SEARCH_BUTTON = "button.btn-search"
    PRODUCT_CARD = ".catalog-item, .product-item"
    PRODUCT_TITLE = ".catalog-item-title, .product-item-title, h3"
    ADD_TO_CART_BTN = "button.add2basket, .btn-add2basket, button:has-text('В корзину')"

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = BaseElement(page, self.SEARCH_INPUT)
        self.search_button = BaseElement(page, self.SEARCH_BUTTON)
        self.add_to_cart_btn = BaseElement(page, self.ADD_TO_CART_BTN)

    def search_product(self, query: str) -> None:
        log.info("Поиск товара: %s", query)
        self.search_input.fill(query, "Ввод поискового запроса")
        self.search_button.click("Нажатие кнопки поиска")
        # Ждем загрузки результатов
        self.page.locator(self.PRODUCT_CARD).first.wait_for(state="visible", timeout=10000)

    def add_first_product_to_cart(self) -> str:
        """Добавляет первый товар из выдачи в корзину и возвращает его название."""
        product_title = self.page.locator(self.PRODUCT_TITLE).first.text_content()
        log.info("Добавление в корзину товара: %s", product_title)
        self.add_to_cart_btn.first.click("Добавление первого товара в корзину")

        # Ждем появления уведомления или обновления корзины (типично для Битрикс)
        self.page.wait_for_timeout(1500)
        return product_title


class CartPage(BasePage):
    """Страница корзины."""
    CART_ITEM = ".cart-item, .bx-item"
    CART_TOTAL = ".cart-total-price, .summ, .total-price"
    CHECKOUT_BTN = "a.checkout-btn, .btn-checkout, button:has-text('Оформить заказ'), a:has-text('Оформить заказ')"

    def __init__(self, page: Page):
        super().__init__(page)
        self.checkout_btn = BaseElement(page, self.CHECKOUT_BTN)

    def go_to_checkout(self) -> None:
        log.info("Переход к оформлению заказа")
        # Проверяем, что товар в корзине
        expect(self.page.locator(self.CART_ITEM).first).to_be_visible(timeout=5000)
        self.checkout_btn.click("Нажатие кнопки 'Оформить заказ'")


class CheckoutPage(BasePage):
    """Страница оформления заказа."""
    # Локаторы
    INPUT_NAME = "input[placeholder*='Имя'], input[name*='NAME'], input.fio"
    INPUT_PHONE = "input[placeholder*='Телефон'], input[name*='PHONE'], input.phone"
    INPUT_EMAIL = "input[placeholder*='Email'], input[name*='EMAIL'], input.email"
    SUBMIT_ORDER_BTN = "button[type='submit']:has-text('Оформить'), .btn-order, button:has-text('Оформить заказ')"
    ORDER_SUCCESS_MSG = "text=Спасибо за заказ, text=Ваш заказ успешно оформлен, .success-message"
    ORDER_NUMBER = "text=№, .order-number"

    def __init__(self, page: Page):
        super().__init__(page)
        self.submit_btn = BaseElement(page, self.SUBMIT_ORDER_BTN)

    def fill_checkout_form(self, name: str, phone: str, email: str) -> None:
        log.info("Заполнение данных заказа")
        # Заполняем только видимые обязательные поля
        name_el = self.page.locator(self.INPUT_NAME).first
        if name_el.is_visible():
            name_el.fill(name, "Ввод имени")

        phone_el = self.page.locator(self.INPUT_PHONE).first
        if phone_el.is_visible():
            phone_el.fill(phone, "Ввод телефона")

        email_el = self.page.locator(self.INPUT_EMAIL).first
        if email_el.is_visible():
            email_el.fill(email, "Ввод email")

    def submit_order(self) -> str:
        """Отправляет форму и возвращает номер заказа."""
        log.info("Отправка формы заказа")
        self.submit_btn.click("Нажатие кнопки 'Оформить заказ'")

        # Ждем появления сообщения об успехе или изменения URL
        self.page.locator(self.ORDER_SUCCESS_MSG).first.wait_for(state="visible", timeout=10000)

        # Пытаемся вытащить номер заказа для отчета
        try:
            order_num = self.page.locator(self.ORDER_NUMBER).first.text_content()
            log.info("Заказ успешно создан: %s", order_num)
            return order_num
        except Exception:
            return "Номер заказа не найден в DOM, но сообщение об успехе отображается"