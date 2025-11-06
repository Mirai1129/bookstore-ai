from datetime import datetime

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.database import Database

from app.core.config import settings
from app.schemas.order import Order, OrderCreate, OrderStatus, OrderUpdate


def _is_object_id_valid(object_id: str) -> bool:
    return ObjectId.is_valid(object_id)


def create_order(db: Database, order: OrderCreate, buyer_id: str) -> Order:
    order_data = order.model_dump()

    order_data["buyer_id"] = buyer_id
    order_data["purchase_date"] = datetime.now()

    order_data["status"] = OrderStatus.PENDING

    collection = db[settings.COLLECTION_NAME_ORDERS]
    result = collection.insert_one(order_data)

    order_data["_id"] = result.inserted_id

    return Order(**order_data)


def get_order_by_id(db: Database, order_id: str) -> Order | None:
    if not _is_object_id_valid(order_id):
        return None

    collection = db[settings.COLLECTION_NAME_ORDERS]
    order_data = collection.find_one({"_id": ObjectId(order_id)})

    if order_data:
        return Order(**order_data)
    return None


def update_order(db: Database, order_id: str, order_update: OrderUpdate) -> Order | None:
    if not _is_object_id_valid(order_id):
        return None

    update_data = order_update.model_dump(exclude_unset=True)

    if not update_data:
        return get_order_by_id(db, order_id)

    collection = db[settings.COLLECTION_NAME_ORDERS]

    updated_order = collection.find_one_and_update(
        {"_id": ObjectId(order_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if updated_order:
        return Order(**updated_order)
    return None
