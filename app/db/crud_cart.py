from datetime import datetime

from pymongo import ReturnDocument
from pymongo.database import Database

from app.core.config import settings
from app.schemas.cart import CartItemAdd


def add_item_to_cart(db: Database, user_id: str, item: CartItemAdd):
    collection = db[settings.COLLECTION_NAME_CARTS]
    now = datetime.now()

    updated_cart = collection.find_one_and_update(
        {
            "user_id": user_id,
            "items.book_id": item.book_id
        },
        {
            "$inc": {"items.$.quantity": item.quantity},
            "$set": {"updated_at": now}
        },
        return_document=ReturnDocument.AFTER
    )

    if updated_cart:
        return updated_cart

    new_item = {
        "book_id": item.book_id,
        "quantity": item.quantity
    }

    updated_cart = collection.find_one_and_update(
        {"user_id": user_id},
        {
            "$push": {"items": new_item},
            "$set": {"updated_at": now},
            "$setOnInsert": {
                "user_id": user_id,
                "created_at": now
            }
        },
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    return updated_cart


def get_cart_by_user_id(db: Database, user_id: str):
    collection = db[settings.COLLECTION_NAME_CARTS]
    return collection.find_one({"user_id": user_id})


def remove_item_from_cart(db: Database, user_id: str, book_id: str):
    collection = db[settings.COLLECTION_NAME_CARTS]
    now = datetime.now()

    result = collection.find_one_and_update(
        {"user_id": user_id},
        {
            "$pull": {"items": {"book_id": book_id}},
            "$set": {"updated_at": now}
        },
        return_document=ReturnDocument.AFTER
    )
    return result


def clear_cart(db: Database, user_id: str):
    collection = db[settings.COLLECTION_NAME_CARTS]
    now = datetime.now()

    result = collection.find_one_and_update(
        {"user_id": user_id},
        {
            "$set": {
                "items": [],
                "updated_at": now
            }
        },
        return_document=ReturnDocument.AFTER
    )
    return result
