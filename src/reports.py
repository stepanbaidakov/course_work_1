import datetime
import logging
import os.path
from typing import Optional

import pandas as pd

from config import DATA_DIR, LOGS_DIR

log_path = os.path.join(LOGS_DIR, "services.log")
services_logger = logging.Logger(__name__)
file_handler = logging.FileHandler(log_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)


def report(func):
    """Принимает функцию"""
    def wrapper(*args, **kwargs):
        """Записывает данные отчета в файл"""
        result = func(*args, **kwargs)
        result_str = str(result)
        with open(os.path.join(DATA_DIR, "reports.txt"), "w", encoding="utf-8") as file:
            file.write(result_str)
        return result

    return wrapper


@report
def find_spending_by_category(
    category: str,
    date: Optional[str] = None,
    transactions: pd.DataFrame = pd.read_csv(os.path.join(DATA_DIR, "operations.csv")),
) -> pd.DataFrame:
    """Функция возвращает траты по заданной категории за последние три месяца"""

    transactions["Дата операции"] = transactions["Дата операции"].apply(
        lambda row: datetime.datetime.strptime(row, "%d.%m.%Y %H:%M:%S")
    )
    transactions["Сумма операции"] = transactions["Сумма операции"].astype(str).str.replace(",", ".").astype(float)
    spendings = transactions[(transactions["Описание"] == category) & (transactions["Сумма операции"] < 0)]
    if date is not None:
        date = datetime.datetime.strptime(date, "%Y.%m.%d %H:%M:%S")
    else:
        date = datetime.datetime.today()
    end_date = date
    start_date = date - datetime.timedelta(days=90)
    spendings_filtered = spendings[
        (spendings["Дата операции"] >= start_date) & (spendings["Дата операции"] <= end_date)
    ]
    return spendings_filtered


# if __name__ == "__main__":
#     sort = find_spending_by_category("Магнит", "2020.03.03 03:42:32")
#     # spending_by_category(pd.read_csv(os.path.join(DATA_DIR, "operations.csv")), "Колхоз", "20.03.2024")
#     # print(type(sort))
#     print(sort)
