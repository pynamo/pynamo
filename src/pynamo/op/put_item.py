from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ..model import Model


class PutItem:
    def __init__(self, obj: "Model"):
        self.obj = obj

    def to_dynamodb(self) -> Dict[str, Any]:
        return self.obj.to_dynamodb_item()
