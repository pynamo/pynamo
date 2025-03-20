from pynamo import Attribute, Model, PrimaryIndex, Table
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

        blah = Attribute(String)

    foo = Foo(id="someid", name="SomeName", blah="blah")

    foo.name = "ChangedName"  # type: ignore
    foo.blah = "ChangedBlah"  # type: ignore

    update_request = UpdateItem(foo)

    assert update_request.to_dynamodb() == {
        "TableName": "mytable",
        "Key": {"PK": {"S": "someid"}},
        "UpdateExpression": "SET #ATTR0 = :ATTR0, #ATTR1 = :ATTR1",
        "ExpressionAttributeNames": {"#ATTR0": "blah", "#ATTR1": "name"},
        "ExpressionAttributeValues": {
            ":ATTR0": {"S": "ChangedBlah"},
            ":ATTR1": {"S": "ChangedName"},
        },
        "ReturnValues": "ALL_NEW",
    }
