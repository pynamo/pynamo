from typing import Dict, Any, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from ..model import Model
    from ..attribute import Expression


class Operation:
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
        raise NotImplementedError()
