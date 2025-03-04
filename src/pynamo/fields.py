from typing import Any, Optional


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
    def serialize(value: Any) -> Optional[str]:
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
            >>> DynamoDBType.serialize(123)
            '123'

            >>> DynamoDBType.serialize(None)
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
            >>> DynamoDBType.deserialize('123')
            '123'

            >>> DynamoDBType.deserialize(None)
            None

            >>> DynamoDBType.deserialize('True')
            'True'
        """
        if value is None:
            return None
        return str(value)


class String(Field):
    pass
