# Pynamo

A lightweight, client-agnostic Python ORM for Amazon DynamoDB.

![Tests](https://github.com/pynamo/pynamo/actions/workflows/tests.yaml/badge.svg)

## Quick Example

```python

from pynamo import Table, PrimaryIndex, Attribute, Model
from pynamo.fields import String


my_table = Table(
    "table",
    PrimaryIndex(
        "PK", String
    )
)


class User(Model):
    __table__ = my_table
    id = Attribute(String, primary_key=True)
    email = Attribute(String)
```
