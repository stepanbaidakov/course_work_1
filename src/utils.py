import json
import logging
import math
import os
from collections import defaultdict
from datetime import datetime, time, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

from config import DATA_DIR, LOGS_DIR

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(filename)s %(levelname)s: %(message)s",
    filename=os.path.join(LOGS_DIR, "views.log"),
    filemode="w",
    encoding="utf-8",
)

transform_date_logger = logging.getLogger("app.views.transform_date")
get_range_logger = logging.getLogger("app.views.get_range")
get_transactions_logger = logging.getLogger("app.views.get_transactions")
split_transactions_logger = logging.getLogger("app.views.split_transactions")
calculate_expenses_logger = logging.getLogger("app.views.calculate_expenses")
calculate_incomes_logger = logging.getLogger("app.views.calculate_incomes")
get_currency_rates_logger = logging.getLogger("app.views.get_currency_rates")
get_stock_prices_logger = logging.getLogger("app.views.get_stock_rates")


def transform_date(date_str: str) -> datetime.date:
    """Преобразует входную строку в объект date"""
    transform_date_logger.info("Дата переводится в формат datetime")
    date_object = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return date_object


def get_date_range(date: datetime, range_type: str = "M") -> list[datetime]:
    """Определяет границы временного диапазона в зависимости от range_type"""
    if range_type == "W":
        start_date = date - timedelta(days=date.weekday())
        end_date = datetime.combine(date, time.max)
        get_range_logger.info("Выбран диапазон W")

    elif range_type == "M":
        start_date = date.replace(day=1)
        end_date = datetime.combine(date, time.max)
        get_range_logger.info("Выбран диапазон M")

    elif range_type == "Y":
        start_date = date.replace(month=1, day=1)
        end_date = datetime.combine(date, time.max)
        get_range_logger.info("Выбран диапазон Y")

    elif range_type == "ALL":
        start_date = datetime.combine(date, time.min)
        end_date = datetime(2021, 12, 31, 23, 59, 59, 999999)
        get_range_logger.info("Выбран диапазон до указанной даты")
        print(end_date)
    else:
        get_range_logger.error("Выбран неправильный диапазон")
        raise ValueError("Неправильный диапазон")
    return [start_date, end_date]


def normalize_value(value):
    """Функция переводит неподходящие значения в формат python"""
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    return value


def get_transactions(start_date: datetime, end_date: datetime, path: str) -> list[dict]:
    """Функция выдает транзакции по заданным датам"""
    operations = pd.read_csv(path)
    operations["Дата операции"] = operations["Дата операции"].apply(
        lambda row: datetime.strptime(row, "%d.%m.%Y %H:%M:%S")
    )
    operations_filtered = operations[
        (operations["Дата операции"] >= start_date) & (operations["Дата операции"] <= end_date)
    ]

    if not operations_filtered.empty:
        get_transactions_logger.info("Выводятся транзакции по заданным датам")
        transactions = operations_filtered.to_dict(orient="records")
        normalized = []
        for operation in transactions:
            norm_row = {key: normalize_value(value) for key, value in operation.items()}
            normalized.append(norm_row)
        return normalized
    else:
        get_transactions_logger.error("Транзакций по заданному диапазону не найдено")
        return []


def split_transactions(transactions: list[dict]) -> tuple[list[dict], list[dict]]:
    """Разделяет транзакции на пополнения и траты"""
    plus_transactions = []
    minus_transactions = []

    for operation in transactions:
        operation["Сумма операции"] = float(operation["Сумма операции"].replace(",", "."))
        if float(operation.get("Сумма операции", "")) > 0:
            split_transactions_logger.info("Пополнение")
            plus_transactions.append(operation)
        elif float(operation.get("Сумма операции", "")) < 0:
            split_transactions_logger.info("Трата")
            minus_transactions.append(operation)

    return plus_transactions, minus_transactions


def calculate_expenses(expenses: list[dict]):
    """Траты выводятся в виде словаря json с учетом наличных"""
    expenses_totals = []
    category_sums = defaultdict(float)

    for expense in expenses:
        amount = abs(expense.get("Сумма операции", ""))
        expenses_totals.append(amount)
        category = expense.get("Категория", "")
        category_sums[category] += amount
        category_totals = [{"category": cat, "amount": amt} for cat, amt in category_sums.items()]
    calculate_expenses_logger.info("Создается список по тратам в каждой категории")

    sorted_category_expenses = sorted(category_totals, key=lambda x: x["amount"], reverse=True)
    calculate_expenses_logger.info("Траты по категориям сортируются по возрастанию")

    cash_categories_list = []
    cash_amount = 0
    cash_categories = ["Наличные", "Переводы"]
    main_categories = [
        category for category in sorted_category_expenses if category.get("category", "") not in cash_categories
    ][:6]
    rest_categories = sorted_category_expenses[7:]
    rest_totals = sum(cat["amount"] for cat in rest_categories)
    calculate_expenses_logger.info("Траты разделяется на основные и остальные")

    categories_count = 0
    for cat in rest_categories:
        if cat in rest_categories:
            categories_count += 1

    for category in sorted_category_expenses:
        if category["category"] in cash_categories:
            cash_amount += category["amount"]
            cash_categories_list.append({"category": category["category"], "amount": cash_amount})
    calculate_expenses_logger.info("Траты наличными и переводами записываются отдельно")

    if categories_count > 0:
        main_categories.append({"category": "Остальное", "amount": rest_totals})
        result = {
            "total_amount": sum(expenses_totals),
            "main": main_categories,
            "transfers_and_cash": cash_categories_list,
        }
        calculate_expenses_logger.info(
            "Выводится полный список с тратами по " 'категориям и наличными с разделом "Остальное" '
        )
    else:
        result = {
            "total_amount": sum(expenses_totals),
            "main": main_categories,
            "transfers_and_cash": cash_categories_list,
        }
        calculate_expenses_logger.info(
            'Выводится json-ответ в виде полного списка с тратами по категориям и наличными без раздела "Остальное"'
        )
    return result


def calculate_incomes(incomes: list[dict]):
    """Возвращает пополнения в виде словаря json"""
    incomes_totals = []
    category_sums = defaultdict(float)

    for income in incomes:
        amount = income.get("Сумма операции", "")
        incomes_totals.append(amount)
        category = income.get("Категория")
        category_sums[category] += amount
        category_totals = [{"category": cat, "amount": amt} for cat, amt in category_sums.items()]
    calculate_incomes_logger.info("Создается список по пополнениям в каждой категории")

    sorted_category_incomes = sorted(category_totals, key=lambda x: x["amount"], reverse=True)
    calculate_incomes_logger.info("Пополнения сортируются")
    main_categories = sorted_category_incomes[:6]
    rest_categories = sorted_category_incomes[7:]
    rest_totals = sum(item["amount"] for item in rest_categories)
    calculate_incomes_logger.info("Пополнения разделяется на основные и остальные")

    categories_count = 0
    for cat in rest_categories:
        if cat in rest_categories:
            categories_count += 1
    if categories_count > 0:
        sorted_category_incomes.append({"category": "Остальное", "amount": rest_totals})
        result = {"total_amount": sum(incomes_totals), "main": main_categories}
        calculate_incomes_logger.info(
            "Выводится json-ответ в виде полного списка с пополнениями по " 'категориям с разделом "Остальное" '
        )
    else:
        result = {"total_amount": sum(incomes_totals), "main": main_categories}
        calculate_incomes_logger.info(
            "Выводится json-ответ в веди полного списка с пополнениями по " 'категориям без раздела "Остальное" '
        )
    return result


def get_currency_rates(path=os.path.join(DATA_DIR, "user_settings.json")):
    """Возвращает список с курсами по заданным валютам"""
    rates = []
    load_dotenv()
    headers = {"apikey": os.getenv("API_KEY_CURRENCIES")}
    with open(path) as file:
        content = json.load(file)
    bases = content.get("user_currencies", "")
    get_currency_rates_logger.info("Загружаются данные из файла по интересующим валютам")

    for base in bases:
        response = requests.get(f"https://api.apilayer.com/exchangerates_data/latest?base={base}&symbols=RUB", headers)
        content = response.json()
        get_currency_rates_logger.info("Курсы валют выводятся в виде json-ответа")
        rate = round(content.get("rates", "").get("RUB", ""), 2)
        rates.append({"currency": base, "rate": rate})
        get_currency_rates_logger.info("Курсы валют выводится в виде json-ответа")

    return rates


def get_stocks_prices(path=os.path.join(DATA_DIR, "user_settings.json")):
    """Возвращает список со стоимостями по заданным валютам"""
    with open(path) as file:
        content = json.load(file)

    tickers = content.get("user_stocks")
    load_dotenv()
    prices = []
    get_stock_prices_logger.info("Загружаются данные из файла по интересующим акциям")
    for ticker in tickers:
        response = requests.get(
            f"https://api.twelvedata.com/price?symbol={ticker}&apikey={os.getenv("API_KEY_STOCKS")}"
        )
        data = response.json()
        print(data)
        get_currency_rates_logger.info("Курсы акций выводятся в виде json-ответа")
        price = round(float(data.get("price", "")), 3)
        prices.append({"stock": ticker, "price": price})

    return prices


if __name__ == "__main__":
    transformed = transform_date("2021-03-23 03:40:43")
    # print(transformed)
    date_range = get_date_range(transformed, "W")
    # print(date_range)
    got_transactions = get_transactions(date_range[0], date_range[1], os.path.join(DATA_DIR, "operations.csv"))
    # print(got_transactions)
    plus, minus = split_transactions(got_transactions)
    expenses_calc = calculate_expenses(minus)
    print(expenses_calc)
    # incomes_calc = calculate_incomes(plus)
    # print(incomes_calc)
    # rates2 = get_currency_rates()
    # print(rates2)
    # stocks = get_stocks_prices()
    # print(stocks)
