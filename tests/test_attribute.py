from pynamo import Attribute
from pynamo.constants import DEFERRED_ATTRIBUTE_KEY
from pynamo.fields import String


def test_attribute_deferred_type():
    attr = Attribute(String)
    assert attr.attribute_type == String


def test_attribute_deferred_key():
    attr = Attribute(String)
    assert attr.key == DEFERRED_ATTRIBUTE_KEY
    assert attr.attribute_type == String


def test_attribute_explicit_key():
    attr = Attribute("foo", String)
    assert attr.key == "foo"


def test_attribute_with_prefix():
    attr = Attribute(String, prefix="Foo#")
    assert isinstance(attr.prefix, str)
    assert attr.prefix == "Foo#"


def test_attribute_with_callable_default():
    def foo():
        return "abc"

    attr = Attribute(String, default=foo)
    assert callable(attr.default)
    assert attr.default() == "abc"


def test_attribute_with_string_default():
    attr = Attribute(String, default="abc")
    assert attr.default == "abc"


def test_attribute_greater_than():
    attr = Attribute(String)

    exp = attr > 123
    assert exp.__class__.__name__ == "Expression"
    assert exp.operator == ">"
    assert isinstance(exp.left, Attribute)


def test_attribute_less_than():
    attr = Attribute(String)

    exp = attr < 123
    assert exp.__class__.__name__ == "Expression"
