from pydantic import BaseModel, Field
from typing import Optional,Union


class NumericComparison(BaseModel):
    lt: Optional[float] = Field(None, alias="$lt")
    lte: Optional[float] = Field(None, alias="$lte")
    gt: Optional[float] = Field(None, alias="$gt")
    gte: Optional[float] = Field(None, alias="$gte")

class MongoQueryFilter(BaseModel):
    title: Optional[str] = None
    price: Optional[Union[float, NumericComparison]] = None
    category: Optional[str] = None
    in_stock: Optional[bool] = None

    class Config:
        populate_by_name = True
        extra = "forbid"