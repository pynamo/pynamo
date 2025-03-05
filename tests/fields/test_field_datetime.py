from pynamo.fields import DateTime
from typing import Any

import datetime

import pytest


@pytest.mark.parametrize(
    "value",
    [
        datetime.datetime(2025, 1, 1),
        datetime.datetime.today().date(),
        "2025-02-23T16:18:25.966407+00:00",
        None,
    ],
)
def test_datetime_deserialize(value: Any):
    deserialized = DateTime.deserialize(value)
    assert isinstance(deserialized, (datetime.datetime, type(None)))


@pytest.mark.parametrize(
    "value,expected",
    [
        (datetime.datetime(2025, 1, 1), "2025-01-01T00:00:00"),
        (None, None),
    ],
)
def test_datetime_serialize(value: Any, expected: Any):
    assert DateTime.serialize(value) == expected
