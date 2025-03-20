from pynamo import Attribute, Model, PrimaryIndex, Table
from pynamo.fields import String


def test_model():
    class Foo(Model):
        __abstract__ = True

        id = Attribute(String)
        some_attribute = Attribute(String)

    f = Foo(id="123")
    f.some_attribute = "some value"  # type: ignore
    f.random = "random"

    assert f.id == "123"
    assert f.some_attribute == "some value"
    assert f.random == "random"  # type: ignore


def test_model_track_changes_no_changes():
    class Foo(Model):
        __abstract__ = True

        id = Attribute(String)
        name = Attribute(String)

    foo = Foo(id="123", name="silly name")

    assert foo.modified_attributes() == {}


def test_model_track_changes_no_changes2():
    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(String, primary_key=True)
        name = Attribute(String)

    foo = Foo(id="123", name="silly name", blah="blah")

    foo.blah = "not tracked"

    assert foo.modified_attributes() == {}


def test_model_track_changes_with_changes():
    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(String, primary_key=True)
        name = Attribute(String)

    foo = Foo(id="123", name="silly name")

    foo.name = "not silly name"  # type: ignore

    assert foo.modified_attributes() == {"name": "not silly name"}


def test_model_to_dynamodb_item():
    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(String, primary_key=True)
        name = Attribute(String)

    foo = Foo(id="123", name="silly name")
    assert foo.to_dynamodb_item() == {
        "PK": {"S": "123"},
        "name": {"S": "silly name"},
    }


def test_model_primary_key():
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

    foo = Foo(id="123", name="silly name")
    assert foo.primary_key == {
        "PK": {"S": "123"},
    }


def test_model_primary_key_with_sort_key():
    mytable = Table(
        "mytable",
        PrimaryIndex(
            Attribute("PK", String),
            Attribute("SK", String),
        ),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(
            String,
            primary_key=True,
        )
        name = Attribute(String)

    foo = Foo(id="123", name="silly name")
    assert foo.primary_key == {
        "PK": {"S": "123"},
        "SK": {"S": "123"},
    }


def test_model_primary_key_with_sort_key2():
    mytable = Table(
        "mytable",
        PrimaryIndex(
            Attribute("PK", String),
            Attribute("SK", String),
        ),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(
            String,
            partition_key=True,
        )
        date = Attribute(
            String,
            sort_key=True,
        )

    foo = Foo(id="123", date="some date")
    assert foo.primary_key == {
        "PK": {"S": "123"},
        "SK": {"S": "some date"},
    }


def test_model_ref():
    mytable = Table(
        "mytable",
        PrimaryIndex(Attribute("PK", String)),
    )

    class Foo(Model):
        __table__ = mytable

        id = Attribute(String, partition_key=True)
        name = Attribute(String)

    foo = Foo(id="123", name="silly name")

    assert foo.ref == ("Foo", "123", None)
