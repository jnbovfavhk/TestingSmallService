from playwright.sync_api import Page, expect

from core.logger import get_logger
from ui.base_element import BaseElement
from ui.base_page import BasePage

log = get_logger(__name__)


class SearchPage(BasePage):
    """Страница поиска и каталога."""
    SEARCH_INPUT = "input[id='title-search-input']"
    SEARCH_BUTTON = "#title-search button.btn-search"
    PRODUCT_CARD = ".catalog-block__item"
    PRODUCT_TITLE = ".catalog-block__info-title"
    ADD_TO_CART_BTN = "button.to_cart"  # Кнопка "В корзину" (для товаров не в корзине)
    IN_CART_CONTROL = ".in_cart"  # Контролы "+ 1 -" (для товаров уже в корзине)

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
        # Находим первый товар в выдаче
        first_product = self.page.locator(self.PRODUCT_CARD).first

        # Получаем название товара
        product_title = first_product.locator(self.PRODUCT_TITLE).text_content()
        log.info("Работа с товаром: %s", product_title)

        # Скроллим к товару, чтобы все элементы внутри стали видимыми
        first_product.scroll_into_view_if_needed()
        self.page.wait_for_timeout(500)

        # Проверяем: товар уже в корзине? (ищем видимый .in_cart внутри карточки)
        in_cart_visible = first_product.locator(self.IN_CART_CONTROL).is_visible()

        if in_cart_visible:
            log.info("Товар уже находится в корзине (найден элемент .in_cart), добавление пропущено")
        else:
            # Товар не в корзине — ищем видимую кнопку "В корзину" внутри карточки и кликаем
            add_btn = first_product.locator(self.ADD_TO_CART_BTN)
            add_btn.wait_for(state="visible", timeout=5000)
            add_btn.click()
            log.info("Товар добавлен в корзину (клик по button.to_cart)")

        # Ждём обновления UI
        self.page.wait_for_timeout(1500)
        return product_title


class CartPage(BasePage):
    """Страница корзины."""
    CART_ITEM = ".basket-items-list-item-wrapper"
    CART_TOTAL = ".basket-coupon-block-total-price-current"
    CHECKOUT_BTN = "button.basket-btn-checkout"

    def __init__(self, page: Page):
        super().__init__(page)
        self.checkout_btn = BaseElement(page, self.CHECKOUT_BTN)

    def verify_checkout_available(self) -> None:
        """Проверяет, что товар в корзине и кнопка 'Оформить заказ' доступна (но НЕ кликает)."""
        log.info("Проверка готовности к оформлению заказа")

        # 1. Проверяем, что товар есть в корзине
        cart_item_visible = self.page.locator(self.CART_ITEM).first.is_visible()
        log.info("Товар в корзине виден: %s", cart_item_visible)
        assert cart_item_visible, "Товар не найден в корзине"

        # 2. Проверяем, что кнопка "Оформить заказ" видна и активна
        checkout_visible = self.page.locator(self.CHECKOUT_BTN).first.is_visible()
        log.info("Кнопка 'Оформить заказ' видна: %s", checkout_visible)
        assert checkout_visible, "Кнопка 'Оформить заказ' не найдена или неактивна"

        # 3. Проверяем, что кнопка не заблокирована (не disabled)
        checkout_enabled = self.page.locator(self.CHECKOUT_BTN).first.is_enabled()
        log.info("Кнопка 'Оформить заказ' активна (не disabled): %s", checkout_enabled)
        assert checkout_enabled, "Кнопка 'Оформить заказ' заблокирована"

        log.info("Путь до оформления заказа проверен успешно. Клик не выполняется")


# class CheckoutPage(BasePage):
#     """Страница оформления заказа."""
#     # Локаторы
#     INPUT_NAME = "input[autocomplete='name']"
#     INPUT_PHONE = "input[autocomplete='tel']"
#     INPUT_EMAIL = "input[autocomplete='email']"
#     SUBMIT_ORDER_BTN = "button[type='submit']:has-text('Оформить'), .btn-order, button:has-text('Оформить заказ')"
#
#     def __init__(self, page: Page):
#         super().__init__(page)
#         self.submit_btn = BaseElement(page, self.SUBMIT_ORDER_BTN)
#
#     def fill_checkout_form(self, name: str, phone: str, email: str) -> None:
#         log.info("Заполнение данных заказа")
#         # Заполняем только видимые обязательные поля
#         name_el = self.page.locator(self.INPUT_NAME).first
#         if name_el.is_visible():
#             name_el.fill(name)
#
#         phone_el = self.page.locator(self.INPUT_PHONE).first
#         if phone_el.is_visible():
#             phone_el.fill(phone)
#
#         email_el = self.page.locator(self.INPUT_EMAIL).first
#         if email_el.is_visible():
#             email_el.fill(email)
#
#     def submit_order(self) -> str:
#         """Отправляет форму и возвращает номер заказа."""
#         log.info("Отправка формы заказа")
#         self.submit_btn.click("Нажатие кнопки 'Оформить заказ'")
#
#         # Ждем появления сообщения об успехе или изменения URL
#         self.page.locator(self.ORDER_SUCCESS_MSG).first.wait_for(state="visible", timeout=10000)
#
#         # Пытаемся вытащить номер заказа для отчета
#         try:
#             order_num = self.page.locator(self.ORDER_NUMBER).first.text_content()
#             log.info("Заказ успешно создан: %s", order_num)
#             return order_num
#         except Exception:
#             return "Номер заказа не найден в DOM, но сообщение об успехе отображается"