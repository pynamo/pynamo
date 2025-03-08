from typing import Any, Dict, TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    from .get_item import GetItem
    from .put_item import PutItem


class TransactWriteItems:
    def __init__(self, *args: Union["GetItem", "PutItem"]):
        self.operations = [arg for arg in args]

    def to_dynamodb(self) -> Dict[str, Any]:
        operations_to_dynamodb: List[Dict[str, Any]] = []

        for operation in self.operations:
            if operation.__class__.__name__ == "Put":
                operations_to_dynamodb.append(
                    {
                        "Put": operation.to_dynamodb(),
                    }
                )

        return {"TransactItems": operations_to_dynamodb}
