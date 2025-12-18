import pytest

from src.main import run_all_functionalities


def test_main_smoke():
    """Дымовой тест для main модуля."""
    # Просто импортируем и вызываем
    result = run_all_functionalities()
    import json
    parsed = json.loads(result)
    assert isinstance(parsed, dict)

    import pytest

    def test_main_import():
        """Просто импортируем main."""
        import src.main
        assert True

    def test_run_all_functionalities():
        """Тестируем основную функцию."""
        from src.main import run_all_functionalities
        result = run_all_functionalities()
        assert isinstance(result, str)  # Возвращает JSON строку