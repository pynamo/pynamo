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

    q = Query.where(Foo.id == "123", Foo.date == "2025-01-01")

    assert q.to_dynamodb() == {
        "TableName": "mytable",
        "KeyConditionExpression": "PK = :PK AND SK = :SK",
        "ExpressionAttributeValues": {
            ":PK": {
                "S": "123",
            },
            ":SK": {
                "S": "2025-01-01",
            },
        },
    }
