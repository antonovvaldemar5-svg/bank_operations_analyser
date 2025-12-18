import datetime
import json
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.utils import load_transactions_from_excel


def test_load_transactions_from_excel_file_not_found():
    """Тестирование загрузки несуществующего файла"""
    result = load_transactions_from_excel("non_existent.xlsx")
    assert result.empty
    assert isinstance(result, pd.DataFrame)


@patch('pandas.read_excel')
def test_load_transactions_from_excel_success(mock_read_excel):
    """Тестирование успешной загрузки Excel файла"""
    mock_df = pd.DataFrame({
        'Дата операции': ['01.01.2021 12:00:00'],
        'Сумма операции': [100.0]
    })
    mock_read_excel.return_value = mock_df

    result = load_transactions_from_excel("test.xlsx")
    assert not result.empty
    assert len(result) == 1


def test_prepare_for_json_complex():
    """Тестирование подготовки сложных структур для JSON"""
    import datetime

    import numpy as np

    complex_data = {
        'int': np.int64(42),
        'float': np.float64(3.14),
        'datetime': datetime.datetime(2021, 12, 31),
        'list': [1, 2, 3],
        'dict': {'a': 1, 'b': 2},
        'nested': {
            'series': pd.Series([1, 2, 3]),
            'df': pd.DataFrame({'col': [1, 2]})
        }
    }

    from src.utils import prepare_for_json
    result = prepare_for_json(complex_data)

    assert isinstance(result, dict)
    assert result['int'] == 42
    assert result['float'] == 3.14


def test_to_json_with_exception():
    """Тестирование to_json с исключением"""
    from src.utils import to_json

    class Unserializable:
        def __repr__(self):
            raise Exception("Cannot serialize")

    result = to_json({"bad": Unserializable()})
    import json

    try:
        parsed = json.loads(result)
        assert "error" in str(parsed).lower()
    except json.JSONDecodeError:
        assert "error" in result.lower()


@pytest.mark.parametrize("date_str,should_fail", [
    ("2021-13-01 12:00:00", True),  # Неверный месяц
    ("2021-12-32 12:00:00", True),  # Неверный день
    ("", True),  # Пустая строка
    ("2021-12-01 25:00:00", True),  # Неверный час
])
def test_parse_date_edge_cases(date_str, should_fail):
    """Параметризованный тест для parse_date"""
    from src.utils import parse_date

    if should_fail:
        with pytest.raises(ValueError):
            parse_date(date_str)
    else:
        result = parse_date(date_str)
        assert isinstance(result, datetime.datetime)


def test_utils_real_calls():
    """Реальные вызовы функций utils."""
    from src.utils import prepare_for_json, to_json

    # Реальный вызов to_json с нормальными данными
    data = {"name": "test", "value": 42, "list": [1, 2, 3]}
    json_str = to_json(data)
    parsed = json.loads(json_str)
    assert parsed["name"] == "test"
    assert parsed["value"] == 42

    # Реальный вызов prepare_for_json
    import numpy as np
    test_data = {
        "number": 123,
        "text": "hello",
        "array": np.array([1, 2, 3]),
        "date": datetime.datetime.now()
    }
    result = prepare_for_json(test_data)
    assert isinstance(result, dict)
    assert result["number"] == 123
    assert result["text"] == "hello"


def test_load_and_prepare_data_real():
    """Реальный тест для load_and_prepare_data."""
    # Создаем тестовый Excel файл или мокаем
    from unittest.mock import MagicMock, patch

    import pandas as pd

    from src.utils import load_and_prepare_data

    with patch('pandas.read_excel') as mock_read:
        # Мок с реальными данными
        mock_df = pd.DataFrame({
            'Дата операции': ['01.01.2021 12:00:00', '02.01.2021 13:00:00'],
            'Сумма операции': ['-100.0', '200.0'],
            'Категория': ['Food', 'Salary']
        })
        mock_read.return_value = mock_df

        df = load_and_prepare_data("test.xlsx")
        assert not df.empty
        assert 'Дата операции' in df.columns


def test_load_and_prepare_data_simple():
    """Простой тест для load_and_prepare_data."""
    from unittest.mock import patch

    import pandas as pd

    from src.utils import load_and_prepare_data

    with patch('pandas.read_excel') as mock_read:
        mock_df = pd.DataFrame({'test': [1, 2, 3]})
        mock_read.return_value = mock_df

        df = load_and_prepare_data("any.xlsx")
        assert not df.empty
