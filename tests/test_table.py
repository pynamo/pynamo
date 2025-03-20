import pytest

from pynamo import (
    GlobalSecondaryIndex,
    LocalSecondaryIndex,
    PrimaryIndex,
    Table,
)
from pynamo.attribute import Attribute
from pynamo.constants import PRIMARY_INDEX
from pynamo.fields import Integer, String


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


def test_table_overlapping_keys():
    my_table = Table(
        "mytable",
        PrimaryIndex(
            Attribute("PK", String),
            Attribute("SK", String),
        ),
        LocalSecondaryIndex(
            "LSI1",
            Attribute("SK", String),
        ),
        GlobalSecondaryIndex(
            "GSI1",
            Attribute("PK", String),
            Attribute("SK", String),
        ),
    )
    assert my_table.name == "mytable"
    assert my_table.indexes[PRIMARY_INDEX][0] == "PK"
    assert my_table.indexes[PRIMARY_INDEX][1] is not None

    if my_table.indexes[PRIMARY_INDEX][1]:
        assert my_table.indexes[PRIMARY_INDEX][1] == "SK"

    assert my_table.indexes == {
        PRIMARY_INDEX: ["PK", "SK"],
        "LSI1": [None, "SK"],
        "GSI1": ["PK", "SK"],
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
        PrimaryIndex(
            Attribute("PK", String),
            Attribute("PK", String),
        )

    assert (
        exc.value.args[0]
        == "Partition key and sort key must have different names."
    )


def test_table_name_primary_key_missing_field_name():
    with pytest.raises(TypeError) as exc:
        PrimaryIndex(
            Attribute(String),
        )

    assert (
        exc.value.args[0]
        == "Attribute key required for primary index ie: Attribute(<key>, <type>)"
    )


def test_table_name_primary_key_missing_field_name2():
    with pytest.raises(TypeError) as exc:
        PrimaryIndex(
            Attribute("PK", String),
            Attribute(String),
        )

    assert (
        exc.value.args[0]
        == "Attribute key required for primary index ie: Attribute(<key>, <type>)"
    )


def test_table_field_mismatch():
    with pytest.raises(TypeError) as exc:
        Table(
            "mytable",
            PrimaryIndex(
                Attribute("PK", String),
                Attribute("SK", String),
            ),
            GlobalSecondaryIndex(
                "GSI1",
                Attribute("PK", String),
                Attribute("SK", Integer),  # offending attribute
            ),
        )
    assert exc.value.args[0] == "Attribute type mismatch"


def test_table_field_mismatch2():
    with pytest.raises(TypeError) as exc:
        Table(
            "mytable",
            PrimaryIndex(
                Attribute("PK", String),
                Attribute("SK", String),
            ),
            GlobalSecondaryIndex(
                "GSI1",
                Attribute("PK", Integer),  # offending attribute
                Attribute("SK", String),
            ),
        )
    assert exc.value.args[0] == "Attribute type mismatch"
