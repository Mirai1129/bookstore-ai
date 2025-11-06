from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from app.db import crud_book as crud
from app.db.adapter import get_db
from app.schemas.book import Book, BookCreate, BookUpdate

router = APIRouter(prefix="/books")


# TODO: 這是一個「暫時的模擬函數」，你未來必須用你真正的「認證系統」取代它
def get_current_user_id() -> str:
    """
    (暫時) 模擬從 JWT token 或 session 中取得當前登入的 user ID。
    你必須用你真實的 `Depends(get_current_user)` 依賴來替換它。
    """
    # 在真實的 APP 中，你會在這裡解碼 Token
    # 為了測試，我們先寫死一個賣家 ID
    return "temp_seller_id_from_token"


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_new_book(
        book: BookCreate,
        db: Database = Depends(get_db),
        seller_id: str = Depends(get_current_user_id)
):
    return crud.create_book(db=db, book=book, seller_id=seller_id)


@router.get("/{book_id}", response_model=Book)
def get_book_by_id(book_id: str, db: Database = Depends(get_db)):
    book = crud.get_book_by_id(db=db, book_id=book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book


@router.get("/seller/{seller_id}", response_model=List[Book])
def get_books_by_seller_id(seller_id: str, db: Database = Depends(get_db)):
    books = crud.get_book_by_seller_id(db=db, seller_id=seller_id)
    return books


@router.patch("/{book_id}", response_model=Book)
def update_existing_book(
        book_id: str,
        book_update: BookUpdate,
        db: Database = Depends(get_db),
        current_user_id: str = Depends(get_current_user_id)
):
    book = crud.get_book_by_id(db=db, book_id=book_id)

    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    if book.seller_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this book"
        )

    updated_book = crud.update_book(
        db=db,
        book_id=book_id,
        book_update=book_update
    )

    if updated_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found during update"
        )

    return updated_book


@router.delete("/{book_id}", status_code=status.HTTP_200_OK)
def delete_existing_book(
        book_id: str,
        db: Database = Depends(get_db),
        current_user_id: str = Depends(get_current_user_id)
):
    book = crud.get_book_by_id(db=db, book_id=book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    if book.seller_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this book"
        )

    deleted = crud.delete_book(db=db, book_id=book_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found during deletion"
        )

    return {"message": "Book deleted successfully"}
