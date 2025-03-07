from pynamo import (
    GlobalSecondaryIndex,
    LocalSecondaryIndex,
    PrimaryIndex,
    Table,
)

from pynamo.constants import PRIMARY_INDEX
from pynamo.fields import String
from pynamo.attribute import Attribute
import pytest


def test_table():
    my_table = Table(
        "mytable",
        PrimaryIndex(
            Attribute("PK", String),
            Attribute("SK", String),
        ),
        LocalSecondaryIndex(
            "LSI1",
            Attribute("LSI1SK", String),
        ),
        GlobalSecondaryIndex(
            "GSI1",
            Attribute("GSI1PK", String),
            Attribute("GSI1SK", String),
        ),
    )
    assert my_table.name == "mytable"
    assert my_table.indexes[PRIMARY_INDEX][0] == "PK"
    assert my_table.indexes[PRIMARY_INDEX][1] is not None

    if my_table.indexes[PRIMARY_INDEX][1]:
        assert my_table.indexes[PRIMARY_INDEX][1] == "SK"

    assert my_table.indexes == {
        PRIMARY_INDEX: ["PK", "SK"],
        "LSI1": [None, "LSI1SK"],
        "GSI1": ["GSI1PK", "GSI1SK"],
    }


def test_table_name_missing_primary_index():
    with pytest.raises(TypeError) as exc:
        Table("mytable")

    assert exc.value.args[0] == "primary index required"


def test_table_name_duplicate_primary_index():
    with pytest.raises(TypeError) as exc:
        Table(
            "mytable",
            PrimaryIndex(Attribute("PK", String)),
            PrimaryIndex(Attribute("SK", String)),
        )

    assert exc.value.args[0] == "Primary index already defined"


def test_table_name_duplicate_keys():
    with pytest.raises(TypeError) as exc:
        Table(
            "mytable",
            PrimaryIndex(
                Attribute("PK", String),
                Attribute("PK", String),
            ),
        )

    assert exc.value.args[0] == "PK already exists"
