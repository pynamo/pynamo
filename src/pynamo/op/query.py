from typing import TYPE_CHECKING, Any, Dict, List, Tuple

if TYPE_CHECKING:
    from ..attribute import Attribute, BindParameter, Expression
    from ..model import Model


class Query:
    def __init__(self, model: "Model"):
        self._model = model
        self._conditions: List[Tuple["Attribute", str, "BindParameter"]] = []
        self._index_name = None

    def mapped_columns(self, col_name: str):
        return self._model.__forward_table_mapper__.get(
            col_name,
            (
                col_name,
                None,
            ),
        )

    def where(self, *args: "Expression"):
        for exp in args:
            column = exp.left
            # if not isinstance(column, Attribute):
            #    raise TypeError("Not an instance of Attribute")
            operator = exp.operator
            bind_param = exp.right
            self._conditions.append((column, operator, bind_param))
        return self

    def to_dynamodb(self, start_key: Any = None) -> Dict[str, Any]:
        if not self._model.__table__:
            raise TypeError("abstract")

        table_name = self._model.__table__.name

        where_clauses = []
        attribute_values = {}

        for column, operator, bind_param in self._conditions:
            cols = self.mapped_columns(column.key)

            for col_name in cols:
                if col_name is None:
                    continue
                where_clauses.append(f"{col_name} {operator} :{col_name}")
                attribute_values[f":{col_name}"] = {
                    column.attribute_type.dynamodb_descriptor: bind_param._value
                }
        exp = " AND ".join(where_clauses)
        query_params = {
            "TableName": table_name,
            "KeyConditionExpression": exp,
            "ExpressionAttributeValues": attribute_values,
        }
        if start_key:
            query_params["ExclusiveStartKey"] = start_key

        return query_params
