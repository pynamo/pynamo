from pynamo import Attribute, Model, Table, PrimaryIndex
from pynamo.op import PutItem

from pynamo.fields import String


def test_put_item():
    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class User(Model):
        __table__ = mytable

        id = Attribute(
            String,
            primary_key=True,
        )
        email = Attribute(String)

    o = PutItem(User(id="123", email="user@example.org"))

    assert o.to_dynamodb() == {
        "TableName": "mytable",
        "Item": {
            "PK": {"S": "123"},
            "email": {"S": "user@example.org"},
        },
        "ReturnValues": "NONE",
    }
