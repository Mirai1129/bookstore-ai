from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.database import Database

from app.core.config import settings
from app.schemas.book import Book, BookCreate, BookUpdate


def _is_object_id_valid(object_id: str) -> bool:
    return ObjectId.is_valid(object_id)


def create_book(db: Database, book: BookCreate, seller_id: str) -> Book:
    book_data = book.model_dump()

    book_data["created_at"] = datetime.now()
    book_data["seller_id"] = seller_id
    book_data["is_sold"] = False

    collection = db[settings.COLLECTION_NAME_BOOKS]
    result = collection.insert_one(book_data)

    book_data["_id"] = result.inserted_id

    return Book(**book_data)


def get_book_by_id(db: Database, book_id: str) -> Book | None:
    if not _is_object_id_valid(book_id):
        return None

    collection = db[settings.COLLECTION_NAME_BOOKS]
    book_data = collection.find_one({"_id": ObjectId(book_id)})

    if book_data:
        return Book(**book_data)
    return None


def get_book_by_seller_id(db: Database, seller_id: str) -> List[Book]:
    collection = db[settings.COLLECTION_NAME_BOOKS]
    cursor = collection.find({"seller_id": seller_id})

    return [Book(**doc) for doc in cursor]


def get_all_books(db: Database, skip: int = 0, limit: int = 100) -> List[Book]:
    collection = db[settings.COLLECTION_NAME_BOOKS]

    cursor = collection.find({"is_sold": {"$ne": True}}).skip(skip).limit(limit)

    return [Book(**doc) for doc in cursor]


def update_book(db: Database, book_id: str, book_update: BookUpdate) -> Book | None:
    if not _is_object_id_valid(book_id):
        return None

    collection = db[settings.COLLECTION_NAME_BOOKS]

    existing_book = collection.find_one({"_id": ObjectId(book_id)})

    if not existing_book:
        return None

    if existing_book.get("is_sold") is True:
        return None

    update_data = book_update.model_dump(exclude_unset=True)

    if not update_data:
        return Book(**existing_book)

    updated_book = collection.find_one_and_update(
        {"_id": ObjectId(book_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

    if updated_book:
        return Book(**updated_book)
    return None


def delete_book(db: Database, book_id: str) -> bool:
    if not _is_object_id_valid(book_id):
        return False

    collection = db[settings.COLLECTION_NAME_BOOKS]

    result = collection.delete_one({"_id": ObjectId(book_id)})

    return result.deleted_count > 0