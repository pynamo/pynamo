from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

if TYPE_CHECKING:
    from ..attribute import Attribute, BindParameter, Expression
    from ..model import Model

from ..constants import PRIMARY_INDEX


class Query:
    def __init__(
        self,
        model: Type["Model"],
    ):
        self.model = model
        self._conditions: List[Tuple["Attribute", str, "BindParameter"]] = []
        # self.table_name = None
        # self.table: Optional["Table"] = None
        self.partition_key: Optional[str] = None
        self.sort_key: Optional[str] = None

    def _set_key(
        self,
        key_value: Optional[str],
        key_name: str,
        is_partition: bool,
    ):
        if key_value:
            if self.model.__table__ is None:
                raise TypeError("table required")

            index_name = self.model.__index_name__ or PRIMARY_INDEX

            keys = self.model.__table__.indexes.get(index_name)
            if not keys:
                raise TypeError(
                    f"Index '{index_name}' not found in table '{self.model.__table__.name}'"
                )

            expected_key = keys[0] if is_partition else keys[1]

            if key_value != expected_key:
                raise TypeError(
                    f"Attribute '{key_name}' is not part of index '{index_name}'"
                )
            else:
                if is_partition:
                    if self.partition_key:
                        raise TypeError(f"Duplicate partition key: {key_name}")
                    else:
                        self.partition_key = key_name

                if not is_partition:
                    if self.sort_key:
                        raise TypeError(f"Duplicate sort key {key_name}")
                    else:
                        self.sort_key = key_name

    def where(self, *args: "Expression"):
        if getattr(self, "model") is None:
            raise TypeError("Model required")

        for exp in args:
            # attr_model = exp.left.model_cls
            if self.model != exp.left.model_cls:
                raise TypeError("Differing model classes")

            mapped_columns = self.model.forward_mapped_columns(exp.left.key)

            self._set_key(
                mapped_columns[0],
                exp.left.key,
                is_partition=True,
            )
            self._set_key(
                mapped_columns[1],
                exp.left.key,
                is_partition=False,
            )

            column = exp.left
            operator = exp.operator
            bind_param = exp.right
            self._conditions.append((column, operator, bind_param))

        return self

    def to_dynamodb(self, start_key: Any = None) -> Dict[str, Any]:
        if self.model.__table__ is None:
            raise TypeError("table required")

        where_clauses: List[str] = []
        attribute_values: Dict[str, Any] = {}

        for column, operator, bind_param in self._conditions:
            cols = self.model.forward_mapped_columns(column.key)

            for col_name in cols:
                if col_name is None:
                    continue
                where_clauses.append(f"{col_name} {operator} :{col_name}")
                attribute_values[f":{col_name}"] = {
                    column.attribute_type.dynamodb_descriptor: bind_param._value
                }
        exp = " AND ".join(where_clauses)
        query_params = {
            "TableName": self.model.__table__.name,
            "KeyConditionExpression": exp,
            "ExpressionAttributeValues": attribute_values,
        }
        if start_key:
            query_params["ExclusiveStartKey"] = start_key

        return query_params
