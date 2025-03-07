from typing import TYPE_CHECKING, Dict, Set, Union, Optional

if TYPE_CHECKING:
    from .attribute import Attribute


from .constants import PRIMARY_INDEX, DEFERRED_ATTRIBUTE_KEY


class PrimaryIndex:
    """
    Represents the Primary Index (Partition Key and optional Sort Key) for a
    table.

    Args:
        A variable-length argument list expecting:
            - args[0]: The Partition Key (required, must be an instance of
            `Attribute`).
            - args[1]: The Sort Key (optional, must be an instance of
            `Attribute`).

    Raises:
        TypeError: If the Partition Key or Sort Key does not have a defined key.
    """

    def __init__(
        self,
        partition_key: "Attribute",
        *args: "Attribute",
    ) -> None:
        self.name = PRIMARY_INDEX
        if partition_key.key == DEFERRED_ATTRIBUTE_KEY:
            raise TypeError(
                "Attribute key required for primary index ie: Attribute(<key>, <type>)"
            )
        self.partition_key: "Attribute" = partition_key

        self.sort_key: Optional["Attribute"] = args[0] if args else None
        if self.sort_key and self.sort_key.key == DEFERRED_ATTRIBUTE_KEY:
            raise TypeError(
                "Attribute key required for primary index ie: Attribute(<key>, <type>)"
            )


class LocalSecondaryIndex:
    """
    Represents a Local Secondary Index (LSI) in DynamoDB.

    A Local Secondary Index allows querying data within the same partition key
    but using an alternative sort key. This class validates the index name
    and ensures the sort key is a valid Attribute instance.

    Args:
        name (str): The name of the local secondary index.
        sort_key (Attribute): The attribute that serves as the sort key for the LSI.

    """

    def __init__(self, name: str, sort_key: "Attribute"):
        self.name = name
        self.partition_key = None
        self.sort_key = sort_key


class GlobalSecondaryIndex:
    def __init__(
        self,
        name: str,
        partition_key: "Attribute",
        sort_key: Optional["Attribute"] = None,
    ):
        self.name = name
        self.partition_key = partition_key
        self.sort_key = sort_key


class Table:
    def __init__(
        self,
        name: str,
        *args: Union[
            PrimaryIndex,
            LocalSecondaryIndex,
            GlobalSecondaryIndex,
        ],
    ):
        self.name = name

        self.indexes: Dict[str, list[Optional[str]]] = {}

        attribute_names: Set[str] = set()
        index_names: Set[str] = set()

        for arg in args:
            keys = [
                arg.partition_key.key if arg.partition_key else None,
                arg.sort_key.key if arg.sort_key else None,
            ]

            self.indexes.setdefault(arg.name, keys)

            if arg.sort_key:
                if arg.sort_key.key in attribute_names:
                    raise TypeError(f"{arg.sort_key.key} already exists")
                attribute_names.add(arg.sort_key.key)

            if arg.partition_key:
                if arg.partition_key.key in attribute_names:
                    raise TypeError(f"{arg.partition_key.key} already exists")
                attribute_names.add(arg.partition_key.key)

            if arg.name in index_names:
                raise TypeError("Primary index already defined")
            index_names.add(arg.name)

        if PRIMARY_INDEX not in self.indexes:
            raise TypeError("primary index required")
