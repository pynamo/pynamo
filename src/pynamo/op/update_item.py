from typing import TYPE_CHECKING, Any, Dict, Literal, Type

if TYPE_CHECKING:
    from ..attribute import Expression
    from ..model import Model

from .base import Operation


class UpdateItem(Operation):
    def __init__(self, obj: "Model"):
        """
        Initializes a PutItem instance.

        Args:
            obj (Model): The model instance to be serialized for DynamoDB.
        """
        self.obj = obj
        self.condition = None

    @classmethod
    def where(cls, *args: "Expression") -> "UpdateItem":
        """
        Initialize an UpdateItem instance

        eg:
            UpdateItem.where(User.id = 123)
        """

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

    def to_dynamodb(
        self,
        return_values: Literal[
            "NONE",
            "ALL_OLD",
            "UPDATED_OLD",
            "ALL_NEW",
            "UPDATED_NEW",
        ] = "ALL_NEW",
    ) -> Dict[str, Any]:
        if self.obj.__class__.__table__ is None:
            raise TypeError("__table__ required")

        table_name = self.obj.__class__.__table__.name

        expression_attribute_names: Dict[Any, Any] = {}
        expression_attribute_values: Dict[Any, Any] = {}

        expressions: list[str] = []

        for attr_name in self.obj.modified_attrs:
            attr = self.obj.__class__.__dict__[attr_name]

            value = getattr(self.obj, attr_name, None)

            if value is None or not value:
                if not attr.attribute.nullable:
                    raise ValueError(f"{attr_name} cannot be empty")

            mapped_columns = self.obj.forward_mapped_columns(attr.attribute.key)

            substitued_counter = 0

            col_name: str

            for col_name in filter(None, mapped_columns):
                substitued = f"ATTR{substitued_counter}"

                expressions.append(f"#{substitued} = :{substitued}")
                expression_attribute_names[f"#{substitued}"] = col_name

                if value:
                    expression_attribute_values[f":{substitued}"] = {
                        attr.attribute.attribute_type.dynamodb_descriptor: value
                    }
                else:
                    expression_attribute_values[f":{substitued}"] = {
                        "NULL": True,
                    }

                substitued_counter += 1

        update_expression = f"SET {', '.join(expressions)}"

        dynamodb_request = {
            "TableName": table_name,
            "Key": self.obj.primary_key,
            "UpdateExpression": update_expression,
            "ExpressionAttributeNames": expression_attribute_names,
            "ExpressionAttributeValues": expression_attribute_values,
            "ReturnValues": return_values,
        }

        return dynamodb_request
