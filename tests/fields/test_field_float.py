from pynamo.fields import Float
from typing import Any


import pytest


@pytest.mark.parametrize(
    "value,expected",
    [
        (123, 123),
        (float(123), float(123)),
        ("123.0", 123.0),
        (None, None),
    ],
)
def test_float_deserialize(value: Any, expected: Any):
    assert Float.deserialize(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (123.4, "123.4"),
        (None, None),
    ],
)
def test_float_serialize(value: Any, expected: Any):
    assert Float.serialize(value) == expected
