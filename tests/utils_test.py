import pytest
import logging
import datetime
from src.utils import transform_date, get_date_range


@pytest.fixture
def date():
    return "20.12.2020"


def test_transform_date(date):
    assert transform_date(date) == datetime.datetime(2020, 12, 20, 0, 0)


@pytest.mark.parametrize(
    "date, range_, dates",
    [
        (
            datetime.datetime(2021, 12, 20, 0, 0),
            "W",
            [
                datetime.datetime(2021, 12, 20, 0, 0),
                datetime.datetime(2021, 12, 20, 23, 59, 59, 999999),
            ],
        ),
        (
            datetime.datetime(2021, 12, 20, 0, 0),
            "M",
            [
                datetime.datetime(2021, 12, 1, 0, 0),
                datetime.datetime(2021, 12, 20, 23, 59, 59, 999999),
            ],
        ),
        (
            datetime.datetime(2021, 1, 20, 0, 0),
            "Y",
            [datetime.datetime(2021, 1, 1, 0, 0), datetime.datetime(2021, 1, 20, 23, 59, 59, 999999)],
        ),
        (
            datetime.datetime(2021, 12, 20, 0, 0),
            "ALL",
            [datetime.datetime(2021, 12, 20, 0, 0), datetime.datetime(2021, 12, 31, 23, 59)],
        ),
    ],
)
def test_get_date_range(date, range_, dates):
    assert get_date_range(date, range_) == dates

@pytest.mark.parametrize("start_date, end_date, list")
