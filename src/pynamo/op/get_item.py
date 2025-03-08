from typing import TYPE_CHECKING, Any, Dict, Type

if TYPE_CHECKING:
    from ..attribute import Expression
    from ..model import Model


class GetItem:
    def __init__(self, obj: "Model"):
        self.obj = obj

    @classmethod
    def where(cls, *args: "Expression"):
        instance = None

        for exp in args:
            attr = exp.left
            if attr.model_cls is None:
                raise Exception("model_cls is None")

            model_cls: Type["Model"] = attr.model_cls
            if instance is None:
                instance = model_cls()

            attr = exp.left
            value: Any = exp.right.value
            setattr(instance, attr.key, value)

        if instance:
            return cls(instance)
        raise NotImplementedError()

    def to_dynamodb(self) -> Dict[str, Any]:
        table_name = self.obj.__table__.name if self.obj.__table__ else None

        return {
            "TableName": table_name,
            "Key": self.obj.primary_key,
        }
