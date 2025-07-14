Models
======


Example model:


::

    from pynamo import Model
    from pynamo.fields import String

    class User(Model):
        __table__ = my_table
        id = Attribute(String, primary_key=True)
        email = Attribute(String)




Model with a partition key and sort key:



::

    from pynamo import Model
    from pynamo.fields import String, DateTime

    class User(Model):
        __table__ = my_table
        id = Attribute(String, partition_key=True)
        date_created = Attribute(DateTime, sort_key=True)
        email = Attribute(String)
