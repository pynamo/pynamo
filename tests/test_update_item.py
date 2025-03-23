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

    update_request = UpdateItem(foo)

    req = update_request.to_dynamodb()

    assert req["TableName"] == "mytable"
    assert req["Key"] == {"PK": {"S": "someid"}}
    assert req["ExpressionAttributeNames"]["#ATTR0"] == "name"
    assert req["UpdateExpression"] == "SET #ATTR0 = :ATTR0"
    assert req["ExpressionAttributeValues"][":ATTR0"] == {"S": "ChangedName"}
    assert req["ReturnValues"] == "ALL_NEW"
