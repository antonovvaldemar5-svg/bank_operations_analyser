import json

from src.services import investment_bank, investment_piggybank, simple_search


def test_investment_bank_edge_cases():
    """Тестирование граничных случаев для investment_bank"""
    # Тест с положительными суммами (не должны учитываться)
    transactions = [
        {'Дата операции': '2021-12-01', 'Сумма операции': 100.0}
    ]
    result = investment_bank('2021-12', transactions, 10)
    assert result == 0.0

    # Тест с разными лимитами
    transactions = [
        {'Дата операции': '2021-12-01', 'Сумма операции': -1712.0}
    ]
    result_10 = investment_bank('2021-12', transactions, 10)
    result_50 = investment_bank('2021-12', transactions, 50)
    result_100 = investment_bank('2021-12', transactions, 100)

    # Правильные расчеты:
    assert result_10 == 8.0  # 1712 -> 1720 = +8
    assert result_50 == 38.0  # 1712 -> 1750 = +38
    assert result_100 == 88.0  # 1712 -> 1800 = +88

    def test_services_real_calls():
        """Реальные вызовы функций services."""
        from src.services import simple_search

        transactions = [
            {
                "Дата операции": "2021-12-01",
                "Сумма операции": -1500.0,
                "Категория": "Супермаркет",
                "Описание": "Пятерочка"
            },
            {
                "Дата операции": "2021-12-02",
                "Сумма операции": -300.0,
                "Категория": "Кафе",
                "Описание": "Starbucks"
            }
        ]

        result = simple_search("супермаркет", transactions)
        parsed = json.loads(result)
        assert parsed["count"] == 1

        result = simple_search("кафе", transactions)
        parsed = json.loads(result)
        assert parsed["count"] == 1

        def test_investment_piggybank_real():
            """Реальный тест для investment_piggybank."""
            from src.services import investment_piggybank


            result = investment_piggybank()
            import json
            parsed = json.loads(result)
            assert isinstance(parsed, dict)
            assert "status" in parsed

            def test_investment_piggybank_simple():
                """Простой тест для investment_piggybank."""
                from src.services import investment_piggybank

                # Просто вызываем
                result = investment_piggybank()
                import json
                parsed = json.loads(result)
                assert isinstance(parsed, dict)
