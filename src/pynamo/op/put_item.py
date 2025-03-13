from typing import TYPE_CHECKING, Any, Dict, Literal

if TYPE_CHECKING:
    from ..model import Model


class PutItem:
    def __init__(self, instance: "Model"):
        self.instance = instance

    def to_dynamodb(
        self,
        return_values: Literal[
            "NONE",
            "ALL_OLD",
        ] = "NONE",
    ) -> Dict[str, Any]:
        if self.instance.__table__ is None:
            raise TypeError("Table required")
        return {
            "TableName": self.instance.__table__.name,
            "Item": self.instance.to_dynamodb_item(),
            "ReturnValues": return_values,
        }
