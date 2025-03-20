from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Optional, Type

if TYPE_CHECKING:
    from ..attribute import Attribute, BindParameter, Expression
    from ..table import Table
    from ..model import Model


class Query:
    def __init__(
        self,
        index_name: Optional[str] = None,
    ):
        self._conditions: List[Tuple["Attribute", str, "BindParameter"]] = []
        self.index_name = index_name
        self.table_name = None
        self.table: Optional["Table"] = None
        self.model: Optional[Type["Model"]] = None
        self.partition_key: Optional[str] = None
        self.sort_key: Optional[str] = None

    def _set_key(
        self,
        key_value: Optional[str],
        key_name: str,
        is_partition: bool,
    ):
        if self.table is None:
            raise TypeError("Table")
        if key_value:
            if self.index_name is not None:
                keys = self.table.indexes.get(self.index_name)
                if not keys:
                    raise TypeError(
                        f"Index '{self.index_name}' not found in table '{self.table.name}'"
                    )

                expected_key = keys[0] if is_partition else keys[1]

                if key_value != expected_key:
                    raise TypeError(
                        f"Attribute '{key_name}' is not part of index '{self.index_name}'"
                    )
                else:
                    if is_partition:
                        if self.partition_key:
                            raise TypeError(
                                f"Duplicate partition key: {key_name}"
                            )
                        else:
                            self.partition_key = key_name

                    if not is_partition:
                        if self.sort_key:
                            raise TypeError(f"Duplicate sort key {key_name}")
                        else:
                            self.sort_key = key_name

            else:
                # Check against all indexes
                valid = any(
                    key_value == keys[0] or key_value == keys[1]
                    for keys in self.table.indexes.values()
                )
                if not valid:
                    raise TypeError(
                        f"Attribute '{key_name}' is not part of any index on table '{self.table.name}'"
                    )

                # If valid, set the index
                for idx, keys in self.table.indexes.items():
                    expected_key = keys[0] if is_partition else keys[1]
                    if key_value == expected_key:
                        self.index_name = idx
                        return

    @classmethod
    def where(cls, *args: "Expression"):
        q_instance = cls()

        for exp in args:
            model = exp.left.model_cls
            if model is None:
                raise TypeError("Expression model_cls is not defined")

            if model.__table__ is None:
                raise TypeError(f"Cannot query abstract class ({model})")

            q_instance.model = model

            if q_instance.table is None:
                q_instance.table = model.__table__
            elif q_instance.table.name != model.__table__.name:
                raise TypeError(
                    f"Cannot query across multiple tables: {q_instance.table.name} & {model.__table__}"
                )

            mapped_columns = model.forward_mapped_columns(exp.left.key)

            q_instance._set_key(
                mapped_columns[0],
                exp.left.key,
                is_partition=True,
            )
            q_instance._set_key(
                mapped_columns[1],
                exp.left.key,
                is_partition=False,
            )

            column = exp.left
            operator = exp.operator
            bind_param = exp.right
            q_instance._conditions.append((column, operator, bind_param))

        return q_instance

    def to_dynamodb(self, start_key: Any = None) -> Dict[str, Any]:
        if not self.table:
            raise TypeError("abstract")

        if self.model is None:
            raise TypeError("Model")

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
            "TableName": self.table.name,
            "KeyConditionExpression": exp,
            "ExpressionAttributeValues": attribute_values,
        }
        if start_key:
            query_params["ExclusiveStartKey"] = start_key

        return query_params
