Usage
=====

This quickstart demonstrates how to define a table, model, and basic usage.


First create a table

::

    from pynamo import Table, PrimaryIndex, Attribute
    from pynamo.fields import Integer, String

    my_table = Table(
        "mytable",
        PrimaryIndex(
            Attribute("PK", Integer),
        ),
    )



Then create a model


::

    from pynamo import Model
    from pynamo.fields import String

    class User(Model):
        __table__ = my_table
        id = Attribute(String, primary_key=True)
        email = Attribute(String)


Get Item

::

    from pynamo import GetItem

    request = GetItem(User).where(id="123")
    request.to_dynamodb()
    # {
    #   "TableName": "table",
    #   "Key": {"PK": {"S": "123"}},
    # }


Use with your favorite client

::

    import boto3

    boto3_client = boto3.client("dynamodb")

    request = GetItem(User).where(id="123")

    res = boto3_client.get_item(**request)
