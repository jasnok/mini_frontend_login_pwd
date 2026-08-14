from datetime import datetime

from pydantic import BaseModel, Field


class CartCreate(BaseModel):
    user_id: str = Field(min_length=1, examples=["testuser"])
    item_id: str = Field(min_length=1, examples=["P001"])
    count: int = Field(gt=0, examples=[2])


class CartUpdate(BaseModel):
    count: int = Field(gt=0, examples=[5])


class CartPublic(BaseModel):
    id: str = Field(examples=["202608140001"])
    user_id: str
    item_id: str
    count: int
    created_date: datetime
