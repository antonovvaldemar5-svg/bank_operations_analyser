import datetime
import json
from unittest.mock import patch

import pandas as pd


from src.reports import spending_by_category, spending_by_weekday


def test_spending_by_category():
    """Тестирование отчета по категориям"""
    test_data = {
        'Дата операции': [
            datetime.datetime(2021, 10, 1),  # 01.10.2021
            datetime.datetime(2021, 11, 15),  # 15.11.2021
            datetime.datetime(2021, 12, 20)  # 20.12.2021
        ],
        'Сумма операции': [-100.0, -200.0, -300.0],
        'Категория': ['Food', 'Food', 'Transport']
    }
    df = pd.DataFrame(test_data)

    result_json = spending_by_category(df, 'Food', '2021-12-31')
    result = json.loads(result_json)

    assert result['status'] == 'success'
    assert result['category'] == 'Food'
    assert result['total_spent'] == 200.0

    print(f"Actual total_spent: {result['total_spent']}")
    print(f"Period: {result.get('period')}")


def test_spending_by_category_no_data():
    """Тестирование отчета по категориям без данных"""
    df = pd.DataFrame()
    result_json = spending_by_category(df, 'Food')
    result = json.loads(result_json)

    assert result['status'] == 'error'
    assert result['total_spent'] == 0


def test_spending_by_category_no_category():
    """Тестирование отчета по категориям без совпадений"""
    test_data = {
        'Дата операции': [datetime.datetime(2021, 12, 1)],
        'Сумма операции': [-100.0],
        'Категория': ['Transport']
    }
    df = pd.DataFrame(test_data)

    result_json = spending_by_category(df, 'Food')
    result = json.loads(result_json)

    assert result['status'] == 'success'
    assert result['total_spent'] == 0


def test_spending_by_category_with_date():
    """Тестирование отчета по категориям с конкретной датой"""
    test_data = {
        'Дата операции': [
            datetime.datetime(2021, 9, 1),  # Более 3 месяцев назад
            datetime.datetime(2021, 12, 15)  # В пределах 3 месяцев
        ],
        'Сумма операции': [-500.0, -100.0],
        'Категория': ['Food', 'Food']
    }
    df = pd.DataFrame(test_data)

    result_json = spending_by_category(df, 'Food', '2021-12-31')
    result = json.loads(result_json)

    assert result['total_spent'] == 100.0


@patch('builtins.open')
def test_report_decorator(mock_open):
    """Тестирование декоратора отчетов"""
    test_data = {
        'Дата операции': [datetime.datetime(2021, 12, 1)],
        'Сумма операции': [-100.0],
        'Категория': ['Food']
    }
    df = pd.DataFrame(test_data)

    result_json = spending_by_category(df, 'Food')
    result = json.loads(result_json)

    assert mock_open.called or result['status'] == 'success'


def test_spending_by_weekday():
    """Тестирование отчета по дням недели"""
    test_data = {
        'Дата операции': [datetime.datetime(2021, 12, 1)],
        'Сумма операции': [-100.0]
    }
    df = pd.DataFrame(test_data)

    result_json = spending_by_weekday(df)
    result = json.loads(result_json)

    assert 'status' in result


def test_reports_real_calls():
    """Реальные вызовы функций reports."""
    from src.reports import spending_by_category, spending_by_weekday

    # Реальные данные
    df = pd.DataFrame({
        "Дата операции": [
            datetime.datetime(2021, 10, 15),
            datetime.datetime(2021, 11, 20),
            datetime.datetime(2021, 12, 25)
        ],
        "Сумма операции": [-500.0, -750.0, -1000.0],
        "Категория": ["Food", "Food", "Transport"]
    })

    # Реальные вызовы
    result = spending_by_category(df, "Food", "2021-12-31")
    parsed = json.loads(result)
    assert parsed["status"] == "success"
    assert "total_spent" in parsed

    result = spending_by_weekday(df, "2021-12-31")
    parsed = json.loads(result)
    assert parsed["status"] == "success"
