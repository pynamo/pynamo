from pynamo import Attribute, GetItem, Model, PrimaryIndex, Table
from pynamo.fields import String


def test_get_item_from_model_instance():
    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(
            String,
            primary_key=True,
        )

    request = GetItem(Foo).where(Foo.id == "123")

    assert request.to_dynamodb() == {
        "TableName": "mytable",
        "Key": {"PK": {"S": "123"}},
    }


def test_get_item_from_kwargs():
    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(
            String,
            primary_key=True,
        )

    request = GetItem(Foo).where(id="123")

    assert request.to_dynamodb() == {
        "TableName": "mytable",
        "Key": {"PK": {"S": "123"}},
    }


"""
def test_get_item_using_class_method():
    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(
            String,
            primary_key=True,
        )
        name = Attribute(
            String,
        )

    request = GetItem.where(Foo.id == "123", Foo.name == "My Name")

    assert request.to_dynamodb() == {
        "TableName": "mytable",
        "Key": {"PK": {"S": "123"}},
    }
"""
