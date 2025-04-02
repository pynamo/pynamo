from typing import TYPE_CHECKING, Any, Dict, List, Union

if TYPE_CHECKING:
    from .delete_item import DeleteItem
    from .get_item import GetItem
    from .put_item import PutItem
    from .update_item import UpdateItem


class TransactWriteItems:
    def __init__(
        self, *args: Union["GetItem", "PutItem", "UpdateItem", "DeleteItem"]
    ):
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
