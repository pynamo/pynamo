# Pynamo

A lightweight, client-agnostic Python ORM for Amazon DynamoDB.

![Tests](https://github.com/pynamo/pynamo/actions/workflows/tests.yaml/badge.svg)

## Quick Example

```python

from pynamo import Table, PrimaryIndex, Attribute, Model, GetItem
from pynamo.fields import String


my_table = Table(
    "table",
    PrimaryIndex(
        Attribute("PK", String),
    )
)


class User(Model):
    __table__ = my_table
    id = Attribute(String, primary_key=True)
    email = Attribute(String)

request = GetItem.where(Foo.id == "123", Foo.name == "My Name")

request.to_dynamodb()
# {
#   "TableName": "table",
#   "Key": {"PK": {"S": "123"}},
# }

```
