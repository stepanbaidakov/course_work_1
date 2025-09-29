import json
import os

from config import DATA_DIR
from src.utils import (calculate_expenses, calculate_incomes, get_currency_rates, get_date_range, get_stocks_prices,
                       get_transactions, split_transactions, transform_date)


def views_main():
    """Возвращает полный список всех транзакций и курсов"""
    print(
        "Здравствуйте! Добро пожаловать в программу работы с банковскими транзакциями."
    )
    print("Укажите дату в формате YYYY-MM-DD HH:MM:SS от которой будет производится поиск транзакций.")
    date = input("Введите дату: ")
    print("Введите диапазон по которому будет производиться поиск транзакций: ")
    range_of_dates = input("Введите диапазон: ").upper()

    transformed_date = transform_date(date)
    date_range = get_date_range(transformed_date, range_of_dates)
    got_transactions = get_transactions(
        date_range[0], date_range[1], os.path.join(DATA_DIR, "operations.csv")
    )
    plus, minus = split_transactions(got_transactions)
    expenses_calc = calculate_expenses(minus)

    incomes_calc = calculate_incomes(plus)
    response = {}

    while True:
        print("Введите валюты по которым хотите получить курс")
        user_input_currencies = input("Введите валюты: ").upper()

        print("Введите акции по которым хотите получить курс")

        user_input_stocks = input("Введите акции: ").upper()
        if "," in user_input_currencies:
            user_currencies_splitted = user_input_currencies.split(", ")
        else:
            user_currencies_splitted = [user_input_currencies]
        if "," in user_input_stocks:
            user_stocks_splitted = user_input_stocks.split(", ")
        else:
            user_stocks_splitted = [user_input_stocks]
        data = {
            "user_currencies": user_currencies_splitted,
            "user_stocks": user_stocks_splitted,
        }
        with open(
            os.path.join(DATA_DIR, "user_settings.json"), "w", encoding="utf-8"
        ) as file:
            json.dump(data, file)

        got_currencies_rates = get_currency_rates()
        got_stocks_prices = get_stocks_prices()
        break

    response["expenses"] = expenses_calc
    response["incomes"] = incomes_calc
    response["currency_rates"] = got_currencies_rates
    response["stock_prices"] = got_stocks_prices
    print("Выводится json ответ")
    return response


if __name__ == "__main__":
    print(views_main())
