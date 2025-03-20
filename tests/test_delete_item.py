from pynamo import Attribute, Model, PrimaryIndex, Table
from pynamo.fields import String
from pynamo.op import DeleteItem


def test_delete_item_from_model_instance():
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

    request = DeleteItem(Foo(id="123"))

    assert request.to_dynamodb() == {
        "TableName": "mytable",
        "Key": {"PK": {"S": "123"}},
    }


def test_delete_item_using_class_method():
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

    request = DeleteItem.where(Foo.id == "123")

    assert request.to_dynamodb() == {
        "TableName": "mytable",
        "Key": {"PK": {"S": "123"}},
    }
