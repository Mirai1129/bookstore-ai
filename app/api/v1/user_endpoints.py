from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from app.db import crud_user as crud
from app.db.adapter import get_db
from app.schemas.user import User, UserCreate, UserUpdate

router = APIRouter(prefix="/users")


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Database = Depends(get_db)):
    existing_user = crud.get_user_by_line_id(db, line_id=user.line_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="User with this LINE ID already exists."
        )

    return crud.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=User)
def get_user_by_id(user_id: str, db: Database = Depends(get_db)): # maybe not be used
    user = crud.get_user_by_id(db, user_id=user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.get("/line/{line_id}", response_model=User)
def get_user_by_line_id(line_id: str, db: Database = Depends(get_db)):
    user = crud.get_user_by_line_id(db, line_id=line_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.patch("/{user_id}", response_model=User)
def update_existing_user(user_id: str, user_update: UserUpdate, db: Database = Depends(get_db)):
    updated_user = crud.update_user(db, user_id=user_id, user_update=user_update)

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return updated_user
