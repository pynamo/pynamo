from pynamo.fields import Boolean
from typing import Any


import pytest


@pytest.mark.parametrize(
    "value,expected",
    [
        ("true", True),
        ("false", False),
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        (None, None),
    ],
)
def test_integer_deserialize(value: Any, expected: Any):
    assert Boolean.deserialize(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (True, True),
        (False, False),
        (None, None),
    ],
)
def test_integer_serialize(value: Any, expected: Any):
    assert Boolean.serialize(value) == expected


with pytest.raises(TypeError):
    Boolean.deserialize("unknown")
