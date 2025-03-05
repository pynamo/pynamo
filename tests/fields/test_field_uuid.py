from pynamo.fields import UUID
from typing import Any
import uuid

import pytest


@pytest.mark.parametrize(
    "value",
    [
        uuid.uuid4(),
        None,
        "7ba6f2cc-b4e5-4998-b731-3e69c808b851",
        "5faf58e9036044249d11cec9e2f4395a",
    ],
)
def test_uuid_deserialize(value: Any):
    deserialized = UUID.deserialize(value)
    assert isinstance(deserialized, (uuid.UUID, type(None)))


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, None),
    ],
)
def test_uuid_serialize(value: Any, expected: Any):
    assert UUID.serialize(value) == expected
