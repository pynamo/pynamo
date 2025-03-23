from pynamo import (
    Attribute,
    Model,
    PrimaryIndex,
    Table,
)
from pynamo.fields import DateTime, String
from pynamo.op import Query


def test_query():
    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String), Attribute("SK", String)),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(String, partition_key=True)
        date = Attribute(DateTime, sort_key=True)

    q = Query(Foo).where(Foo.id == "123", Foo.date == "2025-01-01")

    req = q.to_dynamodb()
    """
    {
        "TableName": "mytable",
        "ExpressionAttributeNames": {
            "#ATTR0": "PK",
            "#ATTR1": "SK",
        },
        "KeyConditionExpression": "#ATTR0 = :ATTR0 AND #ATTR1 = :ATTR1",
        "ExpressionAttributeValues": {
            ":ATTR0": {
                "S": "123",
            },
            ":ATTR1": {
                "S": "2025-01-01",
            },
        },
    }
    """

    assert req["TableName"] == "mytable"
    assert req["ExpressionAttributeNames"]["#ATTR0"] == "PK"
    assert req["ExpressionAttributeNames"]["#ATTR1"] == "SK"
    assert (
        req["KeyConditionExpression"] == "#ATTR0 = :ATTR0 AND #ATTR1 = :ATTR1"
    )
    assert req["ExpressionAttributeValues"][":ATTR0"] == {"S": "123"}
    assert req["ExpressionAttributeValues"][":ATTR1"] == {"S": "2025-01-01"}
