import datetime
import decimal
import uuid
from typing import Any, Optional
from pynamo import _pynamo


class Field:
    """
    Base class for defining a data field in DynamoDB.

    This class provides a foundation for mapping Python objects to DynamoDB's
    expected attribute format. It ensures that values are properly serialized
    before being sent to DynamoDB and correctly deserialized when retrieved.

    Each subclass should define:
        - The `dynamodb_descriptor` (e.g., "S" for strings, "N" for numbers).
        - Custom serialization and deserialization logic specific to the field
          type.

    Responsibilities:
        - **Serialization:** Converts Python objects into DynamoDB-compatible
                             values.
        - **Deserialization:** Converts DynamoDB-stored values back into Python
                               objects.
        - **Validation:** Ensures that values conform to the expected field type.

    Attributes:
        dynamodb_descriptor (str):
            A string identifier representing the DynamoDB data type.
            Must be overridden in subclasses to specify the field's type.

    Methods:
        serialize(value: Any) -> Any:
            Converts a Python value into a DynamoDB-compatible format.

        deserialize(value: Any) -> Any:
            Converts a DynamoDB-stored or user-supplied value back into a
            Python object.
    """

    dynamodb_descriptor: str = "S"  # default to string

    @staticmethod
    def serialize(value: Any) -> Optional[Any]:
        """
        Converts a Python value into a format suitable for DynamoDB storage.

        This method is responsible for converting Python objects into a
        DynamoDB-compatible scalar format. It does NOT return a complete
        DynamoDB JSON representation (e.g., {"S": "value"}), but instead
        only the raw value that DynamoDB expects. The actual type wrapper
        (e.g., {"S": ...}) is handled elsewhere.

        Args:
            value (Any): The Python value to be serialized.

        Returns:
            Optional[str]: A string representation of the input value.
                           Returns None if the input value is None.

        Example:
            >>> Field.serialize(123)
            '123'

            >>> Field.serialize(None)
            None

        """
        if value is None:
            return None
        return str(value)

    @staticmethod
    def deserialize(value: Any) -> Optional[Any]:
        """
        Converts a raw scalar value (either user input or a value retrieved
        from DynamoDB) into a corresponding Python type.

        This method is designed to handle:
          - **User input**: Values provided programmatically by the application.
          - **DynamoDB retrieved values**: Scalar values extracted from
                DynamoDB JSON format.

        It will **not** receive a full DynamoDB JSON objects such as:

            {"S": "some string"}  # Incorrect input
            {"N": "123"}          # Incorrect input

        Instead, it will receive **only the extracted scalar value**:

            "some string"  # Correct input (from user or DynamoDB)
            "123"          # Correct input (from user or DynamoDB)

        Unpacking the DynamoDB JSON objects are handled elsewhere.


        Args:
            value (Any): The raw scalar value to be converted.
                         This may come from user input or DynamoDB.

        Returns:
            Optional[Any]: A Python representation of the input value.
                           Returns None if the input value is None.

        Example:
            >>> Field.deserialize('123')
            '123'

            >>> Field.deserialize(None)
            None

            >>> Field.deserialize('True')
            'True'
        """
        if value is None:
            return None
        return str(value)


class String(Field):
    pass


class Integer(Field):
    dynamodb_descriptor = "N"

    @staticmethod
    def deserialize(value: Optional[Any]) -> Optional[int]:
        return _pynamo.deserialize_integer(value)


class DateTime(Field):
    dynamodb_descriptor = "S"

    @staticmethod
    def serialize(value: Any) -> Any:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def deserialize(value: Any) -> Optional[datetime.datetime]:
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            return datetime.datetime.fromisoformat(value.isoformat())
        return datetime.datetime.fromisoformat(value)


class Date(Field):
    dynamodb_descriptor = "S"

    @staticmethod
    def serialize(value: Any) -> Any:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def deserialize(value: Optional[Any]) -> Optional[datetime.date]:
        if value is None:
            return None
        if isinstance(value, str):
            return datetime.date.fromisoformat(
                value,
            )
        if isinstance(value, datetime.date):
            return value
        raise TypeError(value)


class UUID(Field):
    dynamodb_descriptor = "S"

    @staticmethod
    def deserialize(value: Optional[Any]) -> Optional[uuid.UUID]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(value)


class Float(Field):
    dynamodb_descriptor = "N"

    @staticmethod
    def deserialize(value: Optional[Any]) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, float):
            return value
        return float(str(value))


class Decimal(Field):
    dynamodb_descriptor = "N"

    @staticmethod
    def deserialize(value: Optional[Any]) -> Optional[decimal.Decimal]:
        return _pynamo.deserialize_decimal(value)


class Boolean(Field):
    dynamodb_descriptor = "BOOL"

    @staticmethod
    def serialize(value: Optional[bool]) -> Optional[bool]:
        if value is None:
            return None
        return value

    @staticmethod
    def deserialize(value: Optional[Any]) -> Optional[bool]:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            if value.lower() in ("y", "yes", "t", "true", "on", "1"):
                return True
            if value.lower() in ("n", "no", "f", "false", "off", "0"):
                return False
        raise TypeError(value)
