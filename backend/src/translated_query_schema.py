from typing import Any, Literal, Union

from pydantic import BaseModel, Field


ComparisonOperator = Literal[
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
]


class Condition(BaseModel):
    """One complete database condition, such as price < 5000."""

    field: str = Field(
        ...,
        description="The database field being evaluated.",
    )

    operator: ComparisonOperator = Field(
        ...,
        description="The comparison to perform on the field.",
    )

    value: Any = Field(
        ...,
        description="The value used in the comparison.",
    )


class FilterGroup(BaseModel):
    """A group of conditions combined with AND or OR."""

    operator: Literal["AND", "OR"] = Field(
        ...,
        description="How the child conditions/groups should be combined.",
    )

    conditions: list[Union[Condition, "FilterGroup"]] = Field(
        ...,
        min_length=1,
        description="Conditions or nested groups to combine.",
    )


class QueryOperation(BaseModel):
    """Validated internal representation of a query operation."""

    collection_name: str = Field(
        ...,
        description="The MongoDB collection to query.",
    )

    filter: FilterGroup = Field(
        ...,
        description="The validated logical filter for the query.",
    )


FilterGroup.model_rebuild()


if __name__ == "__main__":
    example = QueryOperation(
        collection_name="products",
        filter=FilterGroup(
            operator="AND",
            conditions=[
                Condition(
                    field="brand",
                    operator="eq",
                    value="Adidas",
                ),
                Condition(
                    field="category",
                    operator="eq",
                    value="shoes",
                ),
                Condition(
                    field="price",
                    operator="lt",
                    value=5000,
                ),
                Condition(
                    field="in_stock",
                    operator="eq",
                    value=True,
                ),
            ],
        ),
    )

    print(example.model_dump_json(indent=2))