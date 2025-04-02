from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .attribute import Attribute


class BindParameter:
    def __init__(self, value: Any):
        self._value = value

    @property
    def value(self) -> Any:
        return self._value


class Expression:
    def __init__(self, left: "Attribute", operator: str, right: BindParameter):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self) -> str:
        return f"{self.left.__class__} {self.operator} {self.right}"
