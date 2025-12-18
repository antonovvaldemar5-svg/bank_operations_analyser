import datetime
import json
import logging

import numpy as np
import pandas as pd

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_date(date_string: str) -> datetime.datetime:
    """
    Парсит строку даты в объект datetime.

    Args:
        date_string: Дата в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
        Объект datetime.datetime
    """
    try:
        return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logger.error(f"Ошибка парсинга даты {date_string}: {e}")
        raise


def load_transactions_from_excel(filepath: str = "operations.xlsx"):
    """
    Загружает транзакции из Excel файла.

    Args:
        filepath: Путь к Excel файлу

    Returns:
        DataFrame с транзакциями
    """
    try:
        logger.info(f"Загрузка данных из {filepath}")
        df = pd.read_excel(filepath, sheet_name=0)
        logger.info(f"Успешно загружено {len(df)} записей")
        return df
    except Exception as e:
        logger.error(f"Ошибка загрузки файла {filepath}: {e}")
        return pd.DataFrame()


def load_and_prepare_data(filepath: str = "operations.xlsx"):
    """
    Загружает и подготавливает данные для анализа.

    Args:
        filepath: Путь к Excel файлу

    Returns:
        Подготовленный DataFrame
    """
    df = load_transactions_from_excel(filepath)

    if df.empty:
        logger.warning("Получен пустой DataFrame")
        return df

    # Преобразование дат
    if 'Дата операции' in df.columns:
        try:
            df['Дата операции'] = pd.to_datetime(
                df['Дата операции'],
                format='%d.%m.%Y %H:%M:%S',
                errors='coerce'
            )
            df['Дата'] = df['Дата операции'].dt.date
            df['Месяц'] = df['Дата операции'].dt.to_period('M')
            df['День недели'] = df['Дата операции'].dt.day_name()
            df['Рабочий день'] = df['Дата операции'].dt.weekday < 5
        except Exception as e:
            logger.error(f"Ошибка обработки дат: {e}")

    # Обработка сумм
    if 'Сумма операции' in df.columns:
        df['Сумма операции'] = pd.to_numeric(
            df['Сумма операции'], errors='coerce'
        )

    return df


def prepare_for_json(data):
    """
    Подготавливает данные для JSON сериализации.

    Args:
        data: Данные для сериализации

    Returns:
        Данные, готовые для JSON
    """
    if isinstance(data, (np.integer, np.int64, np.int32)):
        return int(data)
    elif isinstance(data, (np.floating, np.float64, np.float32)):
        return float(data)
    elif isinstance(data, (pd.Timestamp, datetime.datetime)):
        return data.isoformat()
    elif isinstance(data, pd.Series):
        return data.to_dict()
    elif isinstance(data, pd.DataFrame):
        return data.to_dict('records')
    elif isinstance(data, dict):
        return {k: prepare_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [prepare_for_json(item) for item in data]
    else:
        return data


def to_json(data):
    """
    Конвертирует данные в JSON строку.

    Args:
        data: Словарь с данными

    Returns:
        JSON строка
    """
    try:
        prepared_data = prepare_for_json(data)
        return json.dumps(prepared_data, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка сериализации JSON: {e}")
        return json.dumps(
            {"error": f"JSON serialization failed: {str(e)}"},
            ensure_ascii=False
        )
