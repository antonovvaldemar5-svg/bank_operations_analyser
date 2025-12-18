"""
Модуль services.py - сервисы для анализа данных.
"""
import json
import logging
from typing import Any, Dict, List

import pandas as pd

from src.utils import load_and_prepare_data, to_json

logger = logging.getLogger(__name__)


def investment_bank(
    month: str, transactions: List[Dict[str, Any]], limit: int
) -> float:
    """
    Рассчитывает сумму накоплений через округление трат.

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций
        limit: Предел округления (10, 50 или 100)

    Returns:
        Сумма накоплений за указанный месяц

    Raises:
        ValueError: Если limit не 10, 50 или 100
    """
    if limit not in [10, 50, 100]:
        raise ValueError("Лимит округления должен быть 10, 50 или 100")

    try:
        logger.info(
            f"Расчет инвесткопилки для месяца {month} с лимитом {limit}"
        )

        if not transactions:
            return 0.0

        # Конвертация в DataFrame
        df = pd.DataFrame(transactions)

        # Преобразование дат
        if 'Дата операции' in df.columns:
            df['Дата операции'] = pd.to_datetime(
                df['Дата операции'], errors='coerce'
            )

            # Фильтрация по месяцу
            target_year, target_month = map(int, month.split('-'))
            mask = (
                (df['Дата операции'].dt.year == target_year) &
                (df['Дата операции'].dt.month == target_month)
            )

            month_df = df[mask]

            if month_df.empty:
                return 0.0

            # Расчет накоплений
            total_investment = 0.0

            for amount in month_df['Сумма операции']:
                if amount < 0:  # Только расходы
                    amount_abs = abs(amount)
                    rounded = ((amount_abs + limit - 1) // limit) * limit
                    investment = rounded - amount_abs
                    total_investment += investment

            result = round(total_investment, 2)
            logger.info(f"Рассчитано накоплений: {result} руб")
            return result
        else:
            return 0.0

    except Exception as e:
        logger.error(f"Ошибка расчета инвесткопилки: {e}")
        return 0.0


def investment_piggybank() -> str:
    """
    Обертка для investment_bank с загрузкой данных из Excel.

    Returns:
        JSON строка с результатами
    """
    try:
        logger.info("Запуск сервиса Инвесткопилка")

        # Загрузка данных
        df = load_and_prepare_data("operations.xlsx")

        if df.empty or 'Округление на инвесткопилку' not in df.columns:
            return to_json({
                "service": "investment_piggybank",
                "status": "error",
                "message": "Нет данных об инвесткопилке",
                "total_investment": 0
            })

        # Определение последнего месяца
        if 'Дата операции' in df.columns:
            last_date = df['Дата операции'].max()
            month_str = last_date.strftime('%Y-%m')
        else:
            month_str = "2021-12"

        # Загрузка настроек
        try:
            with open("user_settings.json", 'r', encoding='utf-8') as f:
                settings = json.load(f)
                limit = settings.get("investment_rounding_limit", 50)
        except FileNotFoundError:
            limit = 50

        # Конвертация в список словарей
        transactions = df.to_dict('records')

        # Расчет
        total = investment_bank(month_str, transactions, limit)

        # Дополнительная статистика
        investment_ops = df[df['Округление на инвесткопилку'] > 0]

        result = {
            "service": "investment_piggybank",
            "status": "success",
            "month": month_str,
            "limit": limit,
            "total_investment": float(total),
            "investment_operations_count": int(len(investment_ops)),
            "total_operations_count": int(len(df)),
            "message": f"Накоплено {total:.2f} руб за {month_str}"
        }

        logger.info(f"Инвесткопилка: {result['message']}")
        return to_json(result)

    except Exception as e:
        logger.error(f"Ошибка в investment_piggybank: {e}")
        return to_json({
            "service": "investment_piggybank",
            "status": "error",
            "message": str(e),
            "total_investment": 0
        })


def simple_search(keyword: str, transactions: List[Dict[str, Any]]) -> str:
    """
    Простой поиск транзакций по ключевому слову.

    Args:
        keyword: Строка для поиска
        transactions: Список транзакций

    Returns:
        JSON строка с результатами поиска
    """
    try:
        logger.info(f"Поиск по ключевому слову: '{keyword}'")

        if not transactions:
            return to_json({
                "service": "simple_search",
                "status": "error",
                "message": "Нет данных для поиска",
                "results": [],
                "count": 0
            })

        # Конвертация в DataFrame для удобства
        df = pd.DataFrame(transactions)

        # Поиск в описании и категории
        results = []
        for _, row in df.iterrows():
            description = str(row.get('Описание', '')).lower()
            category = str(row.get('Категория', '')).lower()
            keyword_lower = keyword.lower()

            if keyword_lower in description or keyword_lower in category:
                result_item = {
                    "date": str(row.get('Дата операции', '')),
                    "amount": float(row.get('Сумма операции', 0)),
                    "category": str(row.get('Категория', '')),
                    "description": str(row.get('Описание', ''))
                }
                results.append(result_item)

        return to_json({
            "service": "simple_search",
            "status": "success",
            "keyword": keyword,
            "count": len(results),
            "results": results,
            "message": f"Найдено {len(results)} транзакций по запросу '{keyword}'"  # noqa: E501
        })

    except Exception as e:
        logger.error(f"Ошибка поиска: {e}")
        return to_json({
            "service": "simple_search",
            "status": "error",
            "message": str(e),
            "results": [],
            "count": 0
        })
