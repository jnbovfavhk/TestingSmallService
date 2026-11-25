"""Точка входа для ручного запуска тестов (опционально)."""
import subprocess
import sys


def run_tests():
    """Запустить все тесты."""
    subprocess.run([sys.executable, "-m", "pytest", "-v"], check=True)


def run_tests_with_allure():
    """Запустить тесты и открыть Allure отчёт."""
    subprocess.run([sys.executable, "-m", "pytest", "-v"], check=True)
    subprocess.run(["allure", "serve", "reports/allure-results"], check=True)


if __name__ == "__main__":
    run_tests_with_allure()