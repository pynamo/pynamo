from typing import TYPE_CHECKING, Any, Dict, Self, Type

if TYPE_CHECKING:
    from ..attribute import Expression
    from ..model import Model


class GetItem:
    def __init__(self, model_cls: Type["Model"]):
        self.model_cls = model_cls

    def where(self, *args: "Expression") -> Self:
        instance = self.model_cls()

        for exp in args:
            attr = exp.left
            if attr.model_cls is None:
                raise Exception("model_cls is None")

            attr = exp.left
            value: Any = exp.right.value
            setattr(instance, attr.key, value)

        self.instance = instance
        return self

    def to_dynamodb(self) -> Dict[str, Any]:
        table_name = (
            self.model_cls.__table__.name if self.model_cls.__table__ else None
        )

        return {
            "TableName": table_name,
            "Key": self.instance.primary_key,
        }
