from pynamo import Attribute, Model, Table, PrimaryIndex
from pynamo.fields import String
from pynamo.op import UpdateItem


def test_update_item():
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
        name = Attribute(String)

    foo = Foo(id="someid", name="SomeName")

    foo.name = "ChangedName"  # type: ignore

    update_request = UpdateItem(foo)

    assert update_request.to_dynamodb() == {
        "TableName": "mytable",
        "Key": {"PK": {"S": "someid"}},
        "UpdateExpression": "SET #ATTR0 = :ATTR0",
        "ExpressionAttributeNames": {"#ATTR0": "name"},
        "ExpressionAttributeValues": {":ATTR0": {"S": "ChangedName"}},
        "ReturnValues": "ALL_NEW",
    }
