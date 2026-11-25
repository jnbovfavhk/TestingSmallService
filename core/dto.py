from dataclasses import dataclass
from typing import Literal


@dataclass
class LoginData:
    """Набор данных для теста авторизации."""
    case_id: str  # ID тест-кейса (например, ТК-А1)
    identifier_kind: Literal["username", "email", "phone"]  # тип идентификатора
    login: str  # логин
    password: str  # пароль
    expected_success: bool  # ожидаемый результат
    error_class: str  # класс ошибки (например, "empty_login", "wrong_password")
    description: str  # описание для отчёта