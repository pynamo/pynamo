import decimal
from typing import Any

import pytest

from pynamo.fields import Decimal


@pytest.mark.parametrize(
    "value",
    [
        decimal.Decimal(5),
        "123.0",
        None,
    ],
)
def test_decimal_deserialize(value: Any):
    deserialized = Decimal.deserialize(value)

    assert isinstance(deserialized, (decimal.Decimal, type(None)))


@pytest.mark.parametrize(
    "value,expected",
    [
        (decimal.Decimal("123.4567"), "123.4567"),
        (None, None),
    ],
)
def test_decimal_serialize(value: Any, expected: Any):
    assert Decimal.serialize(value) == expected
