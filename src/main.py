"""
Основной модуль для запуска приложения.
"""
import json
import logging

import pandas as pd

from src.reports import spending_by_category
from src.services import investment_piggybank, simple_search
from src.utils import load_and_prepare_data, to_json
from src.views import main_page

logger = logging.getLogger(__name__)


def run_all_functionalities():
    """
    Запуск всех реализованных функциональностей.
    """
    try:
        logger.info("Запуск всех функциональностей приложения")

        # Загрузка данных
        df = load_and_prepare_data("data/operations.xlsx")

        if df.empty:
            logger.warning("Файл с данными пуст или не найден")
            df = pd.DataFrame()  # Создаем пустой DataFrame для тестирования

        results = []

        # 1. Главная страница
        logger.info("1. Запуск функции главной страницы")
        main_page_result = main_page("2021-12-31 23:59:59")
        results.append({
            "function": "main_page",
            "result": json.loads(main_page_result)
        })

        # 2. Отчет по категории
        logger.info("2. Запуск отчета по категории")
        if not df.empty:
            category_report = spending_by_category(df, "Супермаркеты")
            results.append({
                "function": "spending_by_category",
                "result": json.loads(category_report)
            })

        # 3. Инвесткопилка
        logger.info("3. Запуск сервиса инвесткопилки")
        investment_result = investment_piggybank()
        results.append({
            "function": "investment_piggybank",
            "result": json.loads(investment_result)
        })

        # 4. Простой поиск
        logger.info("4. Запуск простого поиска")
        if not df.empty:
            transactions = df.to_dict('records')
            search_result = simple_search("кафе", transactions)
            results.append({
                "function": "simple_search",
                "result": json.loads(search_result)
            })

        # Сохранение результатов
        with open("all_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        msg = (
            "Все функциональности успешно выполнены. "
            "Результаты сохранены в all_results.json"
        )
        logger.info(msg)

        return to_json({
            "status": "success",
            "message": "Все функциональности выполнены",
            "results_count": len(results)
        })

    except Exception as e:
        logger.error(f"Ошибка при выполнении функциональностей: {e}")
        return to_json({
            "status": "error",
            "message": str(e)
        })


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Запуск всех функциональностей
    result = run_all_functionalities()
    print(result)
