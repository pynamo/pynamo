from typing import Any

import pytest

from pynamo.fields import String


@pytest.mark.parametrize(
    "value,expected",
    [
        (123, "123"),
        (None, None),
        ("123", "123"),
        (False, "False"),
        (True, "True"),
        (3.14, "3.14"),
    ],
)
def test_string_deserialize(value: Any, expected: Any):
    assert String.deserialize(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (123, "123"),
        (None, None),
        ("123", "123"),
        (False, "False"),
        (True, "True"),
        (3.14, "3.14"),
    ],
)
def test_string_serialize(value: Any, expected: Any):
    assert String.serialize(value) == expected
