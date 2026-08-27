from typing import Literal

from pydantic import BaseModel


class TranslatedCondition(BaseModel):
    """One condition extracted from the user's request."""

    field: str
    operator: Literal["eq", "ne", "gt", "gte", "lt", "lte"]
    value: str | int | float | bool


class TranslatedQuery(BaseModel):
    """Structured query produced by the translation layer."""

    logic: Literal["AND", "OR"]
    conditions: list[TranslatedCondition]