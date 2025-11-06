from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from app.db import crud_order as crud

from app.db.adapter import get_db

from app.schemas.order import Order, OrderCreate, OrderUpdate


# TODO: change to get real id
from app.api.v1.book_endpoints import get_current_user_id


router = APIRouter(prefix="/orders")


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_new_order(
        order: OrderCreate,
        db: Database = Depends(get_db),
        buyer_id: str = Depends(get_current_user_id)
):

    # TODO: 1. 檢查 `order.book_ids` 中的書是否都存在且未售出
    # TODO: 2. 檢查 `order.total_price` 是否和書本價格總和一致

    return crud.create_order(db=db, order=order, buyer_id=buyer_id)


@router.patch("/{order_id}", response_model=Order)
def update_order_status(
        order_id: str,
        order_update: OrderUpdate,
        db: Database = Depends(get_db),
        current_user_id: str = Depends(get_current_user_id) # TODO: only user or admin can do
):
    order = crud.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.buyer_id != current_user_id:
       raise HTTPException(status.HTTP_403_FORBIDDEN, ...)

    updated_order = crud.update_order(
        db=db,
        order_id=order_id,
        order_update=order_update
    )

    if updated_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found during update"
        )

    return updated_order