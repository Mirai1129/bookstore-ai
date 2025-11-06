from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from .common import PyObjectId


class BookBase(BaseModel):
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Book author")
    price: int = Field(..., description="Book price")
    condition: str = Field(..., description="Book condition")
    description: Optional[str] = Field(None, description="Book description")
    image_url: str = Field(..., description="Book image url")

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    price: Optional[int] = None
    condition: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_sold: Optional[bool] = None


class Book(BookBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(...)
    seller_id: str = Field(..., description="Book seller_id (from token)")
    is_sold: bool = Field(...)
