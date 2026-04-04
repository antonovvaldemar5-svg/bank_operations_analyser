import datetime
import json
from unittest.mock import mock_open, patch

import pandas as pd

from src.views import (
    get_cards_summary,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    main_page,
)


def test_get_greeting_morning():
    """Тестирование приветствия утром"""
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 8
        result = get_greeting()
        assert result == "Доброе утро"


def test_get_greeting_afternoon():
    """Тестирование приветствия днем"""
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 14
        result = get_greeting()
        assert result == "Добрый день"


def test_get_greeting_evening():
    """Тестирование приветствия вечером"""
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 20
        result = get_greeting()
        assert result == "Добрый вечер"


def test_get_greeting_night():
    """Тестирование приветствия ночью"""
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value.hour = 2
        result = get_greeting()
        assert result == "Доброй ночи"


def test_get_cards_summary():
    """Тестирование сводки по картам"""
    test_data = {
        'Дата операции': [
            datetime.datetime(2021, 12, 1),
            datetime.datetime(2021, 12, 15),
            datetime.datetime(2021, 12, 20)
        ],
        'Номер карты': ['1234567890123456', '1234567890123456', '9876543210987654'],
        'Сумма операции': [-100.0, -200.0, -300.0]
    }
    df = pd.DataFrame(test_data)

    date_str = "2021-12-31 23:59:59"
    result = get_cards_summary(df, date_str)

    assert len(result) == 2
    assert result[0]['last_digits'] == '3456'
    assert result[0]['total_spent'] == 300.0
    assert result[0]['cashback'] == 3.0


def test_get_cards_summary_no_data():
    """Тестирование сводки по картам без данных"""
    df = pd.DataFrame()
    result = get_cards_summary(df, "2021-12-31 23:59:59")
    assert result == []


def test_get_top_transactions():
    """Тестирование топ транзакций"""
    test_data = {
        'Дата операции': [
            datetime.datetime(2021, 12, 1),
            datetime.datetime(2021, 12, 15),
            datetime.datetime(2021, 12, 20)
        ],
        'Сумма платежа': [1000.0, 500.0, 1500.0],
        'Категория': ['Cat1', 'Cat2', 'Cat3'],
        'Описание': ['Desc1', 'Desc2', 'Desc3']
    }
    df = pd.DataFrame(test_data)

    date_str = "2021-12-31 23:59:59"
    result = get_top_transactions(df, date_str, top_n=2)

    assert len(result) == 2
    assert result[0]['amount'] == 1500.0
    assert result[1]['amount'] == 1000.0


def test_get_currency_rates():
    """Тестирование получения курсов валют"""
    currencies = ["USD", "EUR", "CNY"]
    result = get_currency_rates(currencies)

    assert len(result) == 3
    assert all('currency' in item and 'rate' in item for item in result)
    assert any(item['currency'] == 'USD' for item in result)


def test_get_stock_prices():
    """Тестирование получения цен акций"""
    stocks = ["AAPL", "AMZN", "GOOGL"]
    result = get_stock_prices(stocks)

    assert len(result) == 3
    assert all('stock' in item and 'price' in item for item in result)
    assert any(item['stock'] == 'AAPL' for item in result)


@patch('src.views.load_and_prepare_data')
@patch('builtins.open', new_callable=mock_open, read_data='{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}')
def test_main_page_success(mock_file, mock_load_data):
    """Тестирование успешного выполнения main_page"""
    test_df = pd.DataFrame({
        'Дата операции': [datetime.datetime(2021, 12, 1)],
        'Сумма операции': [-100.0],
        'Сумма платежа': [-100.0],
        'Номер карты': ['1234567890123456'],
        'Категория': ['Test'],
        'Описание': ['Test']
    })
    mock_load_data.return_value = test_df

    date_str = "2021-12-31 23:59:59"
    result = main_page(date_str)

    parsed = json.loads(result)
    assert parsed['status'] == 'success'
    assert 'greeting' in parsed
    assert 'cards' in parsed
    assert 'top_transactions' in parsed


@patch('src.views.load_and_prepare_data')
def test_main_page_no_data(mock_load_data):
    """Тестирование main_page без данных"""
    mock_load_data.return_value = pd.DataFrame()

    date_str = "2021-12-31 23:59:59"
    result = main_page(date_str)

    parsed = json.loads(result)
    assert parsed['error'] == True
