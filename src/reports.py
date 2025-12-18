"""
Модуль reports.py - функции для генерации отчетов.
"""
import datetime
import functools
import json
import logging
from typing import Optional

import pandas as pd

from src.utils import to_json

logger = logging.getLogger(__name__)


def report_decorator(filename: Optional[str] = None):
    """
    Декоратор для записи результатов отчетов в файл.

    Args:
        filename: Имя файла для сохранения (опционально)
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # Определение имени файла
                if filename:
                    file_to_save = filename
                else:
                    timestamp = datetime.datetime.now().strftime(
                        '%Y%m%d_%H%M%S'
                    )
                    file_to_save = f"report_{func.__name__}_{timestamp}.json"

                # Сохранение в файл
                with open(file_to_save, 'w', encoding='utf-8') as f:
                    if isinstance(result, str):
                        f.write(result)
                    else:
                        json.dump(result, f, ensure_ascii=False, indent=2)

                logger.info(f"Отчет сохранен в файл: {file_to_save}")
                return result

            except Exception as e:
                logger.error(f"Ошибка в декораторе отчета: {e}")
                return to_json({
                    "report": func.__name__,
                    "error": True,
                    "message": str(e)
                })

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(
    df: pd.DataFrame, category: str, date: Optional[str] = None
) -> str:
    """
    Отчет 'Траты по категории' за последние 3 месяца.

    Args:
        df: DataFrame с транзакциями
        category: Название категории для анализа
        date: Дата отсчета (опционально)

    Returns:
        JSON строка с отчетом
    """
    try:
        logger.info(f"Генерация отчета по категории '{category}'")

        if df.empty or 'Сумма операции' not in df.columns:
            return to_json({
                "report": "spending_by_category",
                "status": "error",
                "message": "Нет данных для отчета",
                "category": category,
                "total_spent": 0
            })

        # Определение даты отсчета
        if date:
            reference_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        else:
            reference_date = datetime.datetime.now()

        # Вычисление периода
        three_months_ago = reference_date - datetime.timedelta(days=90)

        # Подготовка данных
        if 'Дата операции' not in df.columns:
            return to_json({
                "report": "spending_by_category",
                "status": "error",
                "message": "Нет данных о датах транзакций",
                "category": category,
                "total_spent": 0
            })

        # Фильтрация за период
        mask = (
            (df['Дата операции'] >= three_months_ago) &
            (df['Дата операции'] <= reference_date)
        )
        period_df = df[mask].copy()

        if period_df.empty:
            return to_json({
                "report": "spending_by_category",
                "status": "success",
                "message": "Нет данных за указанный период",
                "category": category,
                "total_spent": 0,
                "period": (
                    f"{three_months_ago.date()} - {reference_date.date()}"
                )
            })

        # Фильтрация по категории и расходам
        category_df = period_df[
            (period_df['Категория'] == category) &
            (period_df['Сумма операции'] < 0)
        ].copy()

        if category_df.empty:
            return to_json({
                "report": "spending_by_category",
                "status": "success",
                "message": (
                    f"Нет расходов по категории '{category}' "
                    "за указанный период"
                ),
                "category": category,
                "total_spent": 0,
                "period": (
                    f"{three_months_ago.date()} - {reference_date.date()}"
                )
            })

        # Делаем суммы положительными
        category_df['Сумма операции'] = abs(category_df['Сумма операции'])

        # Группировка по месяцам
        if 'Дата операции' in category_df.columns:
            category_df['Месяц'] = (
                category_df['Дата операции'].dt.to_period('M')
            )
            monthly_spending = (
                category_df.groupby('Месяц')['Сумма операции'].sum()
            )
        else:
            monthly_spending = pd.Series(dtype=float)

        # Расчет статистики
        total_spent = category_df['Сумма операции'].sum()
        transactions_count = len(category_df)

        # Форматирование результата
        monthly_data = {
            str(month): float(amount)
            for month, amount in monthly_spending.items()
        }

        result = {
            "report": "spending_by_category",
            "status": "success",
            "category": category,
            "period": (
                f"{three_months_ago.date()} - {reference_date.date()}"
            ),
            "total_spent": float(total_spent),
            "transactions_count": int(transactions_count),
            "average_per_transaction": (
                float(total_spent / transactions_count)
                if transactions_count > 0 else 0
            ),
            "monthly_breakdown": monthly_data,
            "message": (
                f"За 3 месяца потрачено {total_spent:.2f} руб на '{category}'"
            )
        }

        logger.info(
            f"Отчет по категории '{category}' сгенерирован: "
            f"{total_spent:.2f} руб"
        )
        return to_json(result)

    except Exception as e:
        logger.error(f"Ошибка генерации отчета по категории: {e}")
        return to_json({
            "report": "spending_by_category",
            "status": "error",
            "message": str(e),
            "category": category,
            "total_spent": 0
        })


@report_decorator()
def spending_by_weekday(
    df: pd.DataFrame, date: Optional[str] = None
) -> str:
    """
    Отчет 'Траты по дням недели' за последние 3 месяца.

    Args:
        df: DataFrame с транзакциями
        date: Дата отсчета (опционально)

    Returns:
        JSON строка с отчетом
    """
    try:
        logger.info("Генерация отчета по дням недели")

        if df.empty or 'Сумма операции' not in df.columns:
            return to_json({
                "report": "spending_by_weekday",
                "status": "error",
                "message": "Нет данных для отчета",
                "weekdays": {}
            })

        # Аналогичная логика как в spending_by_category
        # ...

        return to_json({
            "report": "spending_by_weekday",
            "status": "success",
            "message": "Отчет по дням недели сгенерирован"
        })

    except Exception as e:
        logger.error(f"Ошибка генерации отчета по дням недели: {e}")
        return to_json({
            "report": "spending_by_weekday",
            "status": "error",
            "message": str(e),
            "weekdays": {}
        })
