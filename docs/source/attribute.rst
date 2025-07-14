##########
Attributes
##########

Represents an attribute (column) in a DynamoDB table. This class defines the metadata for a field, including key configuration, indexing, default values, and nullability.
Attributes can be used to define partition keys, sort keys, or secondary index keys, and are typically assigned inside a model class definition.




Basic Example
^^^^^^^^^^^^^

In this example, it's assumed that the DynamoDB attribute is named ``foo``


::

    from pynamo import Attribute
    from pynamo.fields import String


    foo = Attribute(String)


Alternate Column Name
^^^^^^^^^^^^^^^^^^^^^

To have the attribute name mapped to a different DynamoDB attribute, pass
a string as the first argument:


::

    from pynamo import Attribute
    from pynamo.fields import String


    foo = Attribute("other", String)



Prefix
^^^^^^

You can specify a prefix, useful for single-table patterns

::

    from pynamo import Attribute
    from pynamo.fields import String


    id = Attribute("id", String, primary_key=True, prefix="USER#")



Default values

::

    from pynamo import Attribute
    from pynamo.fields import DateTime

    from datetime import datetime


    def my_default_dt():
        return datetime.now(datetime.UTC)

    date_created = Attribute(DateTime, default=my_default_dt)



Nullable values

::

    from pynamo import Attribute
    from pynamo.fields import String


    foo = Attribute(String, nullable=True)
