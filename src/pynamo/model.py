from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    cast,
)

from .attribute import Attribute, InstrumentedAttribute
from .constants import DEFERRED_ATTRIBUTE_KEY, PRIMARY_INDEX
from .table import Table

models: Dict[str, Any] = {}


class BaseMeta(type):
    __table__: Optional[Table] = None
    __abstract__: bool = False
    __forward_table_mapper__: Dict[str, List[Any]] = {}
    __reverse_table_mapper__: Dict[Any, str] = {}

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        dct: Dict[str, Any],
    ):
        if name in models:
            raise TypeError(f"Model {name} exists")
        if not dct.get("__table__"):
            # if not dct["__abstract__"]:
            #    raise TypeError("__abstract__ must be True if no __table__")

            dct["__forward_table_mapper__"] = {}
            dct["__reverse_table_mapper__"] = {}
            return super().__new__(cls, name, bases, dct)

        dct["__abstract__"] = False

        if "__table__" not in dct:
            raise Exception(f"{name} __table__ required for non-abstract")

        if not isinstance(dct["__table__"], Table):
            raise Exception(f"__table__ must be an instance of Table in {name}")

        table: "Table" = dct["__table__"]

        dupe_attr_checker: Set[str] = set()

        index_map: Dict[Optional[str], Any] = {}

        forward_table_mapper: Dict[Optional[str], Any] = {}
        reverse_table_mapper: Dict[Any, Any] = {}

        inherited_attrs = {}
        for base in bases:
            if isinstance(base, BaseMeta):
                for key, value in base.__dict__.items():
                    if isinstance(value, Attribute):
                        inherited_attrs[key] = value

        dct = {**inherited_attrs, **dct}

        new_attrs: Dict[str, InstrumentedAttribute] = {}

        for key, value in dct.items():
            if not isinstance(value, Attribute):
                continue
            if value.key == DEFERRED_ATTRIBUTE_KEY:
                value.key = key

            if value.key in dupe_attr_checker:
                raise TypeError(f"duplicate attribute key: {value.key}")

            dupe_attr_checker.add(value.key)

            if value.index_name is not None:
                column_names = table.indexes[value.index_name]
            else:
                column_names = [value.key, None]

            index_map.setdefault(value.index_name, [None, None])

            if value.primary_key:
                if index_map[value.index_name][0] is not None:
                    raise TypeError(
                        "Conflicting indexes. Cannot set {key} as a primary "
                        "key in index {table}.{index} because the partition "
                        "key was previously set by attribute: "
                        "`{attribute}`".format(
                            key=value.key,
                            table=table.name,
                            index=value.index_name,
                            attribute=index_map[value.index_name][0],
                        )
                    )

                if index_map[value.index_name][1]:
                    raise TypeError(
                        "Conflicting indexes. Cannot set {key} as a primary "
                        "key in index {table}.{index} because the sort key was "
                        "previously set by attribute: "
                        "`{attribute}`".format(
                            key=value.key,
                            table=table.name,
                            index=value.index_name,
                            attribute=index_map[value.index_name][1],
                        )
                    )

                forward_table_mapper[value.key] = column_names

                reverse_table_mapper[column_names[0]] = value.key
                if column_names[1]:
                    reverse_table_mapper[column_names[1]] = key
                index_map[value.index_name] = [value.key, value.key]

            elif value.partition_key:
                if index_map[value.index_name][0]:
                    raise TypeError(
                        "Conflicting indexes. Cannot set {key} as a partition "
                        "key in index {table}.{index} because the partition "
                        "key was previously set by attribute: "
                        "`{attribute}`".format(
                            key=value.key,
                            table=table.name,
                            index=value.index_name,
                            attribute=index_map[value.index_name][0],
                        )
                    )

                if not column_names[0]:
                    raise TypeError(
                        f"`{value.key}` no partition_key defined in {table.name}.{value.index_name}"
                    )

                forward_table_mapper[value.key] = (column_names[0], None)
                reverse_table_mapper[column_names[0]] = value.key

                index_map[value.index_name][0] = value.key

            elif value.sort_key:
                if index_map[value.index_name][1]:
                    raise TypeError(
                        "Conflicting indexes. Cannot set {key} as a sort key "
                        "in index {table}.{index} because the sort key was "
                        "previously set by attribute: "
                        "`{attribute}`".format(
                            key=value.key,
                            table=table.name,
                            index=value.index_name,
                            attribute=index_map[value.index_name][1],
                        )
                    )
                if not column_names[1]:
                    raise TypeError(
                        f"Attribute '{key}' defined as a sort key, but no sort key defined in {table.name}.{value.index_name}"
                    )
                forward_table_mapper[value.key] = (column_names[1], None)
                reverse_table_mapper[column_names[1]] = value.key
                index_map[value.index_name][1] = value.key
            else:
                forward_table_mapper[value.key] = (value.key, None)
                reverse_table_mapper[value.key] = value.key

            new_attrs[key] = InstrumentedAttribute(value)

        if PRIMARY_INDEX not in index_map:
            raise ValueError("primary index could not be mapped")

        for idx_name, cols in table.indexes.items():
            if idx_name not in index_map:
                raise ValueError(f"index {idx_name} could not be mapped")

            partition_key, sort_key = cols

            if partition_key and not index_map[idx_name][0]:
                raise ValueError(
                    f"Table '{table.name}' defines a partition key '{partition_key}' "
                    f"in index '{idx_name}'"
                    f"but no corresponding mapping was found in model '{name}'."
                )
            if sort_key and not index_map[idx_name][1]:
                raise ValueError(
                    f"Table '{table.name}' defines a sort key '{sort_key}' "
                    f"in index '{idx_name}'"
                    f"but no corresponding mapping was found in model '{name}'."
                )
        dct.update(new_attrs)
        dct["__table__"] = table
        dct["__forward_table_mapper__"] = forward_table_mapper
        dct["__reverse_table_mapper__"] = reverse_table_mapper
        model_class = super().__new__(cls, name, bases, dct)

        for key, value in model_class.__dict__.items():
            if isinstance(value, InstrumentedAttribute):
                value.attribute.model_cls = cast(Type["Model"], model_class)

        return model_class


class Model(metaclass=BaseMeta):
    __abstract__: Optional[bool] = False
    __table__: Optional[Table] = None

    def __init__(self, **kwargs: Any):
        self._original_state: Dict[str, Any] = {}
        self.modified_attrs: Set[str] = set()

        for key, val in kwargs.items():
            self.__setattr__(key, val)

    def __setattr__(self, name: str, val: Any) -> None:
        attr = self.__class__.__dict__.get(name, None)

        if isinstance(attr, InstrumentedAttribute):
            deserialized = attr.attribute.attribute_type.deserialize(val)
            if name in self._original_state:
                if self._original_state[name] != deserialized:
                    self.modified_attrs.add(name)
            else:
                self._original_state[name] = deserialized

            object.__setattr__(self, name, deserialized)
        else:
            # Normal instance attributes should be set directly
            object.__setattr__(self, name, val)

    @staticmethod
    def extract_dynamodb_value(attr_dict: Dict[str, Any]):
        """
        Extracts the first value from a DynamoDB attribute dictionary safely.

        Args:
            attr_dict (dict): A DynamoDB-style attribute dictionary (e.g., {"S": "blah"}).

        Returns:
            Any: The extracted value or None if the format is invalid.
        """
        if not attr_dict:
            return None

        if "NULL" in attr_dict:
            return None
        return next(iter(attr_dict.values()), None)

    @classmethod
    def from_dynamodb_item(cls, item_dict: Dict[str, Any]) -> "Model":
        if cls.__table__ is None:
            raise TypeError("__table__ required")

        instance = cls()

        for key, value in item_dict.items():
            mapped_key = cls.__reverse_table_mapper__.get(key, key)

            if not hasattr(cls, mapped_key):
                continue

            inst_attribute = cls.__dict__[mapped_key]

            if not isinstance(inst_attribute, InstrumentedAttribute):
                continue

            value = instance.extract_dynamodb_value(value)

            if inst_attribute.attribute.prefix:
                if value and value.startswith(inst_attribute.attribute.prefix):
                    value = value[len(inst_attribute.attribute.prefix) :]

            instance.__setattr__(mapped_key, value)
        return instance

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """
        Converts the model instance into a DynamoDB Item request format.

        Ensures that required attributes such as partition keys and sort keys
        are set, applies default values when applicable, and serializes data
        according to DynamoDB attribute types.

        Returns:
            dict: A dictionary formatted for DynamoDB's PutItem operation, containing:
                - "TableName": The name of the DynamoDB table.
                - "Item": A dictionary of attributes formatted for DynamoDB.

        Raises:
            ValueError: If a required partition key or sort key is None.

        Example:
            user = User(id="123", name="Alice")

            user.to_dynamodb_item()

        """
        if self.__class__.__table__ is None:
            raise TypeError("__table__ required")

        item_data: Dict[str, Any] = {}

        for key, attr in self.__class__.__dict__.items():
            if isinstance(attr, InstrumentedAttribute):
                value = getattr(self, key, None)

                value = attr.attribute.attribute_type.serialize(value)
                if value and attr.attribute.prefix:
                    value = f"{attr.attribute.prefix}{value}"

                if value is None or not value:
                    if attr.attribute.partition_key or attr.attribute.sort_key:
                        raise ValueError(
                            f"{key} (index: {attr.attribute.index_name}) cannot be empty",
                        )
                    if not attr.attribute.nullable:
                        raise TypeError(f"{key} is empty and nullable=False")

                mapped_columns: List[Optional[str]] = (
                    self.forward_mapped_columns(attr.attribute.key)
                )

                for col_name in filter(None, mapped_columns):
                    if value is None:
                        item_data[col_name] = {
                            "NULL": True,
                        }
                    else:
                        item_data[col_name] = {
                            attr.attribute.attribute_type.dynamodb_descriptor: value
                        }

        return item_data

    def attr_to_dynamodb(self, attr_name: str):
        attr = self.__class__.__dict__[attr_name]
        value = getattr(self, attr_name, None)

        value = attr.attribute.attribute_type.serialize(value)
        if value and attr.attribute.prefix:
            value = f"{attr.attribute.prefix}{value}"

        if value is None or not value:
            if attr.attribute.partition_key or attr.attribute.sort_key:
                raise ValueError(
                    f"{self.__class__.__name__}.{attr_name} is mapped to an index "
                    f"({attr.attribute.index_name}) and cannot be empty."
                    f"You may optionally pass a `default` parameter for the "
                    f" Attribute() class"
                )
            if not attr.attribute.nullable:
                raise TypeError(f"{attr_name} is empty and nullable=False")

        mapped_columns = self.forward_mapped_columns(attr.attribute.key)

        dynamodb_data: Dict[str, Any] = {}

        col_name: str

        for col_name in filter(None, mapped_columns):
            if value is None:
                dynamodb_data[col_name] = {
                    "NULL": True,
                }
            else:
                dynamodb_data[col_name] = {
                    attr.attribute.attribute_type.dynamodb_descriptor: value
                }

    @property
    def ref(self) -> Optional[Tuple[str, Any, Any]]:
        if self.__class__.__table__ is None:
            return None

        pk_cols = self.__class__.__table__.indexes[PRIMARY_INDEX]

        pk_attr: str = self.__class__.__reverse_table_mapper__[pk_cols[0]]
        pk_partition_key_val: Any = getattr(self, pk_attr)

        if pk_cols[1]:
            sk_attr: str = self.__class__.__reverse_table_mapper__[pk_cols[1]]
            pk_sort_key_val: Any = getattr(self, sk_attr)
        else:
            pk_sort_key_val = None

        return (
            self.__class__.__name__,
            pk_partition_key_val,
            pk_sort_key_val,
        )

    def modified_attributes(self):
        """Returns a dictionary of only modified attributes."""
        return {attr: getattr(self, attr) for attr in self.modified_attrs}

    @classmethod
    def forward_mapped_columns(cls, col_name: str) -> List[Any]:
        # model -> DynamoDB
        return cls.__forward_table_mapper__.get(col_name, [col_name, None])

    @classmethod
    def reversed_mapped_column(cls, key: str) -> str:
        # DynamoDB -> model
        return cls.__reverse_table_mapper__.get(
            key,
            key,
        )

    @property
    def primary_key(self) -> Dict[Any, Any]:
        """
        Returns the primary key representation formatted for DynamoDB.
        """
        if self.__class__.__table__ is None:
            raise TypeError("__table__ required")

        pk_cols = self.__class__.__table__.indexes[PRIMARY_INDEX]

        pk_attr_name: str = self.__class__.__reverse_table_mapper__[pk_cols[0]]
        pk_val: Any = getattr(self, pk_attr_name)

        if not pk_val:
            raise ValueError(f"Partition key {pk_attr_name} cannot be empty")

        pk_inst_attr = self.__class__.__dict__[pk_attr_name]

        dynamodb_data: Dict[str, Any] = {}

        if pk_inst_attr.attribute.prefix:
            pk_val = f"{pk_inst_attr.attribute.prefix}{pk_val}"

        if not pk_cols[0]:
            raise Exception("not sure how this is possible")

        dynamodb_data[pk_cols[0]] = {
            pk_inst_attr.attribute.attribute_type.dynamodb_descriptor: pk_val,
        }

        if pk_cols[1]:
            sk_attr_name: str = self.__class__.__reverse_table_mapper__[
                pk_cols[1]
            ]
            sk_val: Any = getattr(self, sk_attr_name)
            if not sk_val:
                raise ValueError(f"Sort key {sk_attr_name} cannot be empty")

            sk_inst_attr = self.__class__.__dict__[sk_attr_name]

            if sk_inst_attr.attribute.prefix:
                sk_val = f"{sk_inst_attr.attribute.prefix}{sk_val}"

            dynamodb_data[pk_cols[1]] = {
                sk_inst_attr.attribute.attribute_type.dynamodb_descriptor: sk_val,
            }
        return dynamodb_data
