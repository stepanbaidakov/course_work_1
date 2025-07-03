import re
import logging
from config import DATA_DIR, LOGS_DIR
import os
import pandas as pd
import json

log_path = os.path.join(LOGS_DIR, "services.log")
services_logger = logging.Logger(__name__)
file_handler = logging.FileHandler(log_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(filename)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.DEBUG)

def find_by_number(path: str):
    operations = pd.read_csv(path)
    services_logger.info("Загружается файл с транзакциями")
    pattern =  re.compile(r"\+\d+\s\d+\s\d+\W\d+\W\d+")
    find_filter = operations["Описание"].astype(str).apply(lambda x: bool(pattern.search(x)))
    services_logger.info("Производится поиск операций содержащие номер")
    number_operations = operations[find_filter]
    result = number_operations.to_dict(orient="records")
    services_logger.info("Найденные операции возвращаются в виде json-ответа")
    json_result = json.dumps(result, ensure_ascii=False)
    return json_result
print(find_by_number(os.path.join(DATA_DIR, "operations.csv")))