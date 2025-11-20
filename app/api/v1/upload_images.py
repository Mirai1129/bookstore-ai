import asyncio
import time
from typing import Annotated

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from starlette.concurrency import run_in_threadpool

router = APIRouter()


def upload_single_file_to_cloudinary(file: UploadFile, filename: str):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            public_id=filename,
            folder="my_book_app/books",
            resource_type="image",
            overwrite=True
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"Error uploading {filename}: {e}")
        raise e


@router.post("/")
async def upload_book_images(
        front: Annotated[UploadFile, File(description="Front cover image")],
        spine: Annotated[UploadFile, File(description="Spine image")],
        back: Annotated[UploadFile, File(description="Back cover image")],
        user_id: Annotated[str, Form(description="User ID (Line ID)")],
):
    timestamp = int(time.time())

    upload_tasks = []

    files_map = {
        "front": front,
        "spine": spine,
        "back": back
    }

    for angle, file in files_map.items():
        filename = f"{user_id}_{timestamp}_{angle}"

        task = run_in_threadpool(
            upload_single_file_to_cloudinary,
            file,
            filename
        )
        upload_tasks.append(task)

    try:
        urls_list = await asyncio.gather(*upload_tasks)

        return {
            "front": urls_list[0],
            "spine": urls_list[1],
            "back": urls_list[2]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
