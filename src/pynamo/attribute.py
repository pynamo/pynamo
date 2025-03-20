from typing import TYPE_CHECKING, Any, Callable, Optional, Type, Union

if TYPE_CHECKING:
    from .fields import Field
    from .model import Model


from .constants import DEFERRED_ATTRIBUTE_KEY, PRIMARY_INDEX
from .expression import BindParameter, Expression


class Attribute:
    """
    Represents an attribute (column) in a DynamoDB table.

    This class defines the metadata for a DynamoDB attribute, including its key type,
    indexing options, default values, and nullable constraints. Attributes can serve
    as primary keys (partition or sort keys) and be indexed for efficient querying.

    Args:
        *args (Union[str, Type["Field"]]):
            - If a string is provided, it is treated as the attribute's key name.
            - If a `Field` type is provided, it defines the attribute's data type.
        primary_key (Optional[bool], default=False):
            Specifies whether this attribute is the **Primary Key**.
        partition_key (Optional[bool], default=False):
            Specifies whether this attribute is the **Partition Key**.
        sort_key (Optional[bool], default=False):
            Specifies whether this attribute is the **Sort Key**.
        index_name (Optional[str], default=None):
            The name of the index if this attribute is part of a **secondary index**.
        prefix (Optional[str], default=None):
            A prefix added to the attribute value before storing in DynamoDB.
        default (Optional[Union[str, Callable[[], str]]], default=None):
            A default value for the attribute, which can be a static string or
            a callable function that generates the default dynamically.
        nullable (Optional[bool], default=False):
            If `True`, the attribute can allows None values ("NULL")

    Raises:
        TypeError:
            - If no `Field` type is provided.
            - If the attribute is incorrectly marked as both a partition key and a sort key.
            - If the attribute is incorrectly marked as both a primary key and another key type.

    Example Usage:
        >>> from pynamo import String, Attribute, DateTime
        >>> id = Attribute(String, primary_key=True)
        >>> name = Attribute("different_name", String, default="Unknown")
        >>> created_at = Attribute(DateTime)
    """

    def __init__(
        self,
        *args: Union[str, Type["Field"]],
        partition_key: Optional[bool] = False,
        sort_key: Optional[bool] = False,
        primary_key: Optional[bool] = False,
        index_name: Optional[str] = None,
        prefix: Optional[str] = None,
        default: Optional[Union[str, Callable[[], str]]] = None,
        nullable: Optional[bool] = False,
    ):
        self.partition_key = partition_key
        self.sort_key = sort_key
        self.index_name = index_name
        self.prefix = prefix
        self.default = default
        self.primary_key = primary_key
        self.nullable = nullable
        self.model_cls: Optional[Type["Model"]] = None

        self.key = DEFERRED_ATTRIBUTE_KEY

        for arg in args:
            if isinstance(arg, str):
                self.key = arg
                self.col_name = arg
                continue
            self.attribute_type = arg

        if not hasattr(self, "attribute_type"):
            raise TypeError("Field required")

        if self.partition_key and self.sort_key:
            raise TypeError(
                "An attribute cannot be both a partition key and a sort key. "
            )

        if self.primary_key and self.partition_key:
            raise TypeError(
                "An attribute cannot be both a primary key and a partition key."
            )
        if self.primary_key and self.sort_key:
            raise TypeError(
                "An attribute cannot be both a primary key and a sort key."
            )
        if self.primary_key or self.partition_key or self.sort_key:
            self.index_name = index_name or PRIMARY_INDEX

    def __set_name__(self, owner, name):
        self.model_cls = name

    def __eq__(self, other: Any) -> "Expression":  # type: ignore
        return Expression(self, "=", BindParameter(other))

    def __lt__(self, other: Any) -> "Expression":
        return Expression(self, "<", BindParameter(other))

    def __lte__(self, other: Any) -> "Expression":
        return Expression(self, "<=", BindParameter(other))

    def __gt__(self, other: Any) -> "Expression":
        return Expression(self, ">", BindParameter(other))

    def __gte__(self, other: Any) -> "Expression":
        return Expression(self, ">=", BindParameter(other))

    def __add__(self, other: Any) -> "Expression":
        return Expression(self, "+", BindParameter(other))

    def __sub__(self, other: Any) -> "Expression":
        return Expression(self, "-", BindParameter(other))

    def __repr__(self):
        return f"Attribute({self.attribute_type}, key={self.key})"


class InstrumentedAttribute:
    """
    A descriptor that manages access to a dynamically instrumented attribute
    in a DynamoDB model.

    This class acts as a property descriptor, enabling attribute access,
    default value handling, and storage within the model's internal dictionary.

    Args:
        attribute (Attribute):
            The `Attribute` instance being instrumented.

    Methods:
        __get__(instance: Optional["Model"], owner: Type["Model"]) -> Optional[Any]:
            Retrieves the value of the attribute from the instance.
            If accessed from the class level, returns the `Attribute` itself.

        __set__(instance: Optional["Model"], value: Optional[Any]) -> None:
            Assigns a value to the attribute in the instance.
            If `None` is assigned and the attribute has a default value,
            the default is used instead.

    Example:
        >>> from pynamo import Attribute, String
        >>> class User(Model):
        >>>     id = InstrumentedAttribute(Attribute("id", String, partition_key=True))
        >>>     name = InstrumentedAttribute(Attribute("name", String, default="Unknown"))
        >>>
        >>> user = User()
        >>> print(user.name)  # "Unknown" (default value)
        >>> user.name = "Alice"
        >>> print(user.name)  # "Alice"
    """

    def __init__(self, attribute: "Attribute"):
        self.attribute = attribute

    def __get__(
        self,
        instance: Optional["Model"],
        owner: Type["Model"],
    ) -> Optional[Any]:
        if instance is None:
            return self.attribute
        value = instance.__dict__.get(self.attribute.key)

        return value

    def __set__(
        self,
        instance: Optional["Model"],
        value: Optional[Any],
    ) -> None:
        if value is None:
            if self.attribute.default:
                if callable(self.attribute.default):
                    value = self.attribute.default()
                else:
                    value = self.attribute.default

        instance.__dict__[self.attribute.key] = value
