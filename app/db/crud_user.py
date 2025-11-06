from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.database import Database

from app.core.config import settings
from app.schemas.user import User, UserCreate, UserUpdate


def _is_object_id_valid(object_id: str) -> bool:
    return ObjectId.is_valid(object_id)


def create_user(db: Database, user: UserCreate) -> User:
    user_data = user.model_dump()
    user_data["created_at"] = datetime.now(timezone.utc)

    collection = db[settings.COLLECTION_NAME_USERS]

    result = collection.insert_one(user_data)
    user_data["_id"] = result.inserted_id

    return User(**user_data)


def get_user_by_line_id(db: Database, line_id: str) -> User | None:
    collection = db[settings.COLLECTION_NAME_USERS]
    user_data = collection.find_one({"line_id": line_id})

    if user_data:
        return User(**user_data)

    return None


def get_user_by_id(db: Database, user_id: str) -> User | None:
    if not _is_object_id_valid(user_id):
        return None

    collection = db[settings.COLLECTION_NAME_USERS]
    user_data = collection.find_one({"_id": ObjectId(user_id)})

    if user_data:
        return User(**user_data)

    return None


def update_user(db: Database, user_id: str, user_update: UserUpdate) -> User | None:
    if not _is_object_id_valid(user_id):
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        return get_user_by_id(db, user_id)

    collection = db[settings.COLLECTION_NAME_USERS]
    updated_user = collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER  # Make sure `find_one_and_update()` return updated data
    )

    if not updated_user:
        return None

    return User(**updated_user)
