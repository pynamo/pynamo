from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

def deserialize_integer(value: Any) -> Optional[int]: ...
def deserialize_decimal(value: Any) -> Optional["Decimal"]: ...
