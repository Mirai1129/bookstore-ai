from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pymongo.database import Database

from app.core.config import settings
from app.db import crud_cart
from app.db import crud_order as crud
from app.db.adapter import get_db
from app.schemas.order import Order, OrderCreate, OrderUpdate, OrderStatus

router = APIRouter()


def get_current_user_id(x_user_id: str = Header(..., alias="X-User-ID")) -> str:
    return x_user_id


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_new_order(
        order: OrderCreate,
        db: Database = Depends(get_db),
        buyer_id: str = Depends(get_current_user_id)
):
    try:
        book_object_ids = [ObjectId(bid) for bid in order.book_ids]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Book ID format"
        )

    books_collection = db[settings.COLLECTION_NAME_BOOKS]

    available_books_cursor = books_collection.find({
        "_id": {"$in": book_object_ids},
        "is_sold": {"$ne": True}
    })
    available_books = list(available_books_cursor)

    if len(available_books) != len(order.book_ids):
        found_ids = {str(b["_id"]) for b in available_books}
        missing_ids = set(order.book_ids) - found_ids

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Some books are no longer available or do not exist. IDs: {missing_ids}"
        )

    real_total_price = sum(book.get("price", 0) for book in available_books)

    if real_total_price != order.total_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Price mismatch. Database total: {real_total_price}, Request total: {order.total_price}"
        )

    new_order = crud.create_order(db=db, order=order, buyer_id=buyer_id)

    if not new_order:
        raise HTTPException(status_code=500, detail="Failed to create order")

    books_collection.update_many(
        {"_id": {"$in": book_object_ids}},
        {"$set": {"is_sold": True}}
    )

    crud.update_order(
        db=db,
        order_id=str(new_order.id),
        order_update=OrderUpdate(status=OrderStatus.PAID)
    )
    new_order.status = OrderStatus.PAID

    crud_cart.clear_cart(db, buyer_id)

    return new_order


@router.patch("/{order_id}", response_model=Order)
def update_order_status(
        order_id: str,
        order_update: OrderUpdate,
        db: Database = Depends(get_db),
        current_user_id: str = Depends(get_current_user_id)
):
    order = crud.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.buyer_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )

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
