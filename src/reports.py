import os.path
from typing import Optional
import pandas as pd
import datetime
from config import DATA_DIR, LOGS_DIR
import logging

log_path = os.path.join(LOGS_DIR, "services.log")
services_logger = logging.Logger(__name__)
file_handler = logging.FileHandler(log_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)

def report(func):
    def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            result_str = str(result)
            with open(os.path.join(DATA_DIR, "reports.txt"), "w", encoding="utf-8") as file:
                file.write(result_str)
            return result
    return wrapper

@report
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    transactions["Дата операции"] = transactions["Дата операции"].apply(
        lambda row: datetime.datetime.strptime(row, "%d.%m.%Y %H:%M:%S"))

    spendings = transactions[transactions["Описание"] == category]

    if date is not None:
        date = datetime.datetime.strptime(date, "%d.%m.%Y")
    else:
        date = datetime.datetime.today()
    end_date = date
    start_date = date - datetime.timedelta(days=90)
    spendings_filtered = spendings[
        (spendings["Дата операции"] >= start_date) & (spendings["Дата операции"] <= end_date)
        ]
    print(spendings_filtered.shape)

    return spendings_filtered

# spending_by_category(pd.read_csv(os.path.join(DATA_DIR, "operations.csv")), "Колхоз", "20.03.2024")
print(spending_by_category(pd.read_csv(os.path.join(DATA_DIR, "operations.csv")), "Колхоз", "20.03.2020"))
# print(hello())