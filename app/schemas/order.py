from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from .common import PyObjectId


class OrderBase(BaseModel):
    book_ids: List[str] = Field(..., description="List of book _ids being purchased")
    total_price: int = Field(..., description="Total price of the order")

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class OrderCreate(OrderBase):
    pass


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class Order(OrderBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    buyer_id: str = Field(..., description="User ID of the buyer (from token)")
    purchase_date: datetime = Field(..., description="Purchase date (set by server)")

    status: OrderStatus = Field(..., description="Order status")


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
