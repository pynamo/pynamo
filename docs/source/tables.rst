Tables
======

Define your table classes to map directly to your DynamoDB tables


.. warning::

   The ``Table`` class does not perform any introspection or validation against the actual DynamoDB table.
   It does **not** verify that the declared primary key, sort key, or attribute types match what is configured in DynamoDB.
   You are responsible for ensuring that your table definitions align with your table schema.



::

    from pynamo import Table, PrimaryIndex, Attribute
    from pynamo.fields import String

    my_table = Table(
        "mytable",
        PrimaryIndex(
            Attribute("PK", String),
        ),
    )


If your table has both a partition key and sort key:


::

    from pynamo import Table, PrimaryIndex, Attribute
    from pynamo.fields import String

    my_table = Table(
        "mytable",
        PrimaryIndex(
            Attribute("PK", String),
            Attribute("SK", String),
        ),
    )
