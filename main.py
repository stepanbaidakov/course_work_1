from src.reports import find_spending_by_category
from src.services import find_by_number
from src.views import views_main


def main():
    """Функция запуска проекта"""
    transactions = views_main()
    yield transactions

    print("Для получения трат по категории введите нужную Вам категорию и дату по усмотрению")
    category = input("Введите категорию для получения трат по ней: ")
    whether_date = input("Xотите ли Вы указать дату: ").capitalize()
    if whether_date == "Да":
        date = input("Укажите дату в формате YYYY.MM.DD HH:MM:DD: ")
        spendings_by_category = find_spending_by_category(category, date)
    else:
        spendings_by_category = find_spending_by_category(category)
        # Если дату не указывать, то ответ всегда будет пустой DataFrame, так как транзакции существуют только до начала 2022
    print("Выводятся траты в заданной категории")
    yield spendings_by_category

    print("Выводятся транзакции содержащие номера")
    finded_by_number = find_by_number()
    yield finded_by_number


for step in main():
    print(step)
