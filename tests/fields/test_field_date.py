from pynamo.fields import Date
from typing import Any

import datetime

import pytest


@pytest.mark.parametrize(
    "value",
    [
        datetime.date(2025, 1, 1),
        datetime.datetime.today().date(),
        "2025-02-23",
        None,
    ],
)
def test_date_deserialize(value: Any):
    deserialized = Date.deserialize(value)
    assert isinstance(deserialized, (datetime.date, type(None)))


@pytest.mark.parametrize(
    "value,expected",
    [
        (datetime.date(2025, 1, 1), "2025-01-01"),
        (None, None),
    ],
)
def test_date_serialize(value: Any, expected: Any):
    assert Date.serialize(value) == expected


def test_date_value_error():
    with pytest.raises(ValueError):
        Date.deserialize("wrong date isoformat")


def test_date_type_error():
    with pytest.raises(TypeError):
        Date.deserialize(123)
