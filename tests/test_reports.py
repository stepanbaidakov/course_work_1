import os

import pandas as pd
import pytest

from config import DATA_DIR
from src.reports import find_spending_by_category


@pytest.fixture
def sample_csv_file():
    df = pd.DataFrame([{"Дата операции": "20.03.2020 23:59:59", "Описание": "Магнит", "Сумма": 1000}])
    df_str = str(df)
    report_path = os.path.join(DATA_DIR, "reports_test.txt")
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(df_str)

    file_path = os.path.join(DATA_DIR, "operations_test.csv")
    df.to_csv(file_path, index=False)

    yield file_path


def test_spending_by_category_report(sample_csv_file):

    result = find_spending_by_category("Магнит", "2020.03.20 23:59:59")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 56
    assert result.iloc[0]["Описание"] == "Магнит"

    report_path = os.path.join(DATA_DIR, "reports_test.txt")
    assert os.path.exists(report_path)

    with open(report_path, "r", encoding="utf-8") as file:
        content = file.read()
    assert "Магнит" in content
