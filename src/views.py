"""
Модуль views.py - функции для веб-страниц.
"""
import datetime
import json
import logging

import pandas as pd

from src.utils import load_and_prepare_data, parse_date, to_json

logger = logging.getLogger(__name__)


def get_greeting() -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Returns:
        Строка с приветствием
    """
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_cards_summary(df: pd.DataFrame, date_str: str):
    """
    Рассчитывает сводку по картам за период с начала месяца.

    Args:
        df: DataFrame с транзакциями
        date_str: Дата в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
        Список с данными по картам
    """
    try:
        target_date = parse_date(date_str)
        start_of_month = datetime.datetime(
            target_date.year, target_date.month, 1
        )

        # Фильтрация за период
        period_df = df[
            (df['Дата операции'] >= start_of_month) &
            (df['Дата операции'] <= target_date)
        ]

        if period_df.empty or 'Номер карты' not in period_df.columns:
            return []

        cards_summary = []
        for card in period_df['Номер карты'].unique():
            card_df = period_df[period_df['Номер карты'] == card]

            # Расходы (отрицательные суммы)
            expenses = card_df[card_df['Сумма операции'] < 0]
            expenses_sum = expenses['Сумма операции'].sum()
            total_spent = abs(expenses_sum)

            # Кешбэк: 1 рубль на каждые 100 рублей
            cashback = total_spent / 100 if total_spent > 0 else 0

            cards_summary.append({
                "last_digits": (
                    str(card)[-4:] if card and len(str(card)) >= 4 else "0000"
                ),
                "total_spent": round(float(total_spent), 2),
                "cashback": round(float(cashback), 2)
            })

        return cards_summary

    except Exception as e:
        logger.error(f"Ошибка расчета данных по картам: {e}")
        return []


def get_top_transactions(
    df: pd.DataFrame, date_str: str, top_n: int = 5
):
    """
    Возвращает топ-N транзакций по сумме платежа.

    Args:
        df: DataFrame с транзакциями
        date_str: Дата в формате 'YYYY-MM-DD HH:MM:SS'
        top_n: Количество топ транзакций

    Returns:
        Список топ транзакций
    """
    try:
        target_date = parse_date(date_str)
        start_of_month = datetime.datetime(
            target_date.year, target_date.month, 1
        )

        period_df = df[
            (df['Дата операции'] >= start_of_month) &
            (df['Дата операции'] <= target_date)
        ]

        if period_df.empty:
            return []

        # Сортировка по абсолютной сумме
        top_df = period_df.reindex(
            period_df['Сумма платежа'].abs().sort_values(ascending=False).index
        ).head(top_n)

        top_transactions = []
        for _, row in top_df.iterrows():
            transaction = {
                "date": row['Дата операции'].strftime('%d.%m.%Y'),
                "amount": float(row['Сумма платежа']),
                "category": str(row.get('Категория', 'Неизвестно')),
                "description": str(row.get('Описание', 'Без описания'))
            }
            top_transactions.append(transaction)

        return top_transactions

    except Exception as e:
        logger.error(f"Ошибка получения топ транзакций: {e}")
        return []


def get_currency_rates(currencies):
    """
    Получает курс валют через API.

    Args:
        currencies: Список кодов валют

    Returns:
        Список курсов валют
    """
    # Заглушка для демонстрации
    rates = {
        "USD": 73.21,
        "EUR": 87.08,
        "CNY": 11.45
    }

    return [
        {"currency": curr, "rate": rates.get(curr, 0)}
        for curr in currencies if curr in rates
    ]


def get_stock_prices(stocks):
    """
    Получает цены акций через API.

    Args:
        stocks: Список тикеров акций

    Returns:
        Список цен акций
    """
    # Заглушка для демонстрации
    prices = {
        "AAPL": 150.12,
        "AMZN": 3173.18,
        "GOOGL": 2742.39,
        "MSFT": 296.71,
        "TSLA": 1007.08
    }

    return [
        {"stock": stock, "price": prices.get(stock, 0)}
        for stock in stocks if stock in prices
    ]


def main_page(date_string: str) -> str:
    """
    Главная страница - возвращает данные для отображения.

    Args:
        date_string: Дата в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
        JSON строка с данными для главной страницы
    """
    try:
        logger.info(
            f"Обработка запроса главной страницы для даты: {date_string}"
        )

        # Загрузка настроек пользователя
        try:
            with open("user_settings.json", 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {
                "user_currencies": ["USD", "EUR"],
                "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
            }

        # Загрузка данных
        df = load_and_prepare_data("operations.xlsx")

        if df.empty:
            return to_json({
                "error": True,
                "message": "Нет данных для анализа",
                "date_requested": date_string,
                "status": "error"  # Добавляем статус
            })

        # Формирование ответа
        response = {
            "greeting": get_greeting(),
            "cards": get_cards_summary(df, date_string),
            "top_transactions": get_top_transactions(df, date_string),
            "currency_rates": get_currency_rates(
                settings.get("user_currencies", [])
            ),
            "stock_prices": get_stock_prices(
                settings.get("user_stocks", [])
            ),
            "date_requested": date_string,
            "status": "success"  # Добавляем статус
        }

        logger.info(f"Успешно сформирован ответ для даты: {date_string}")
        return to_json(response)

    except Exception as e:
        logger.error(f"Критическая ошибка в main_page: {e}")
        return to_json({
            "error": True,
            "message": f"Внутренняя ошибка сервера: {str(e)}",
            "date_requested": date_string,
            "status": "error"  # Добавляем статус
        })
