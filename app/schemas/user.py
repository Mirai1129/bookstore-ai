from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from .common import PyObjectId


class UserBase(BaseModel):
    line_id: str = Field(..., description="LINE User ID")
    name: str = Field(..., description="LINE User's Display Name")

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )


class User(UserBase):
    """
    Read User base model.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(..., description="User's Creation Date")


class UserCreate(UserBase):
    """
    Create User base model.
    """
    pass


class UserUpdate(BaseModel):
    """
    Update User base model.
    """
    name: Optional[str] = None
