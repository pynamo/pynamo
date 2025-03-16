# Pynamo

A lightweight, client-agnostic Python ORM for Amazon DynamoDB.

![Tests](https://github.com/pynamo/pynamo/actions/workflows/tests.yaml/badge.svg)

## Creating a Model

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

```

## GetItem

#### Client Agnostic

```python
request = GetItem(User).where(id="123")
request.to_dynamodb()
# {
#   "TableName": "table",
#   "Key": {"PK": {"S": "123"}},
# }

```

#### With boto3

```python
import boto3

boto3_client = boto3.client("dynamodb")

request = GetItem(User).where(id="123")

res = boto3_client.get_item(**request)

```

#### With aioboto3

```python
session = aioboto3.Session()
async with session.client("dynamodb") as client:
    request = (
        GetItem(Dog)
        .where(id="123",
        )
        .to_dynamodb()
    )

    res = await client.get_item(**request)
```

### With a pynamo session

```python
from pynamo.session import Session

session = Session(boto3_client)

session.execute(
    GetItem(User).where(id="123")
)

```
