from datetime import datetime
from typing import Optional, List, Annotated

from pydantic import BaseModel, Field, ConfigDict

from .common import PyObjectId


class CartItem(BaseModel):
    book_id: str = Field(..., description="Book ID")
    quantity: int = Field(default=1, gt=0, description="Quantity of the book")

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class CartBase(BaseModel):
    user_id: str = Field(..., description="User ID (Line ID)")

    items: List[CartItem] = Annotated[List[CartItem], Field(default_factory=list, description="List of items in cart")]

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class CartCreate(CartBase):
    pass


class CartUpdate(BaseModel):
    items: Optional[List[CartItem]] = None
    updated_at: Optional[datetime] = None


class Cart(CartBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CartItemAdd(BaseModel):
    book_id: str = Field(..., description="Book ID to add")
    quantity: int = Field(default=1, gt=0, description="Quantity")
