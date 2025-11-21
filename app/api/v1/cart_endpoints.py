from fastapi import APIRouter, Depends, HTTPException, status, Header
from pymongo.database import Database

from app.db import crud_cart as crud
from app.db.adapter import get_db
from app.schemas.cart import Cart, CartItemAdd

router = APIRouter()


def get_current_user_id(x_user_id: str = Header(..., alias="X-User-ID")) -> str:
    return x_user_id


@router.post("/items", response_model=Cart, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
        item: CartItemAdd,
        user_id: str = Depends(get_current_user_id),
        db: Database = Depends(get_db)
):
    updated_cart = crud.add_item_to_cart(db, user_id, item)

    if not updated_cart:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart"
        )

    return updated_cart


@router.delete("/items/{book_id}", response_model=Cart)
def remove_item_from_cart(
        book_id: str,
        user_id: str = Depends(get_current_user_id),
        db: Database = Depends(get_db)
):
    cart = crud.remove_item_from_cart(db, user_id, book_id)

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found or item not in cart"
        )
    return cart


@router.get("/", response_model=Cart)
def get_my_cart(
        user_id: str = Depends(get_current_user_id),
        db: Database = Depends(get_db)
):
    cart = crud.get_cart_by_user_id(db, user_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    return cart
