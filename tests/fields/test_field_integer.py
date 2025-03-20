from typing import Any

import pytest

from pynamo.fields import Integer


@pytest.mark.parametrize(
    "value,expected",
    [
        (123, 123),
        ("123", 123),
        (None, None),
        (False, 0),
        (True, 1),
        (3.14, 3),
    ],
)
def test_integer_deserialize(value: Any, expected: Any):
    assert Integer.deserialize(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (123, "123"),
        ("123", "123"),
        (None, None),
    ],
)
def test_integer_serialize(value: Any, expected: Any):
    assert Integer.serialize(value) == expected
