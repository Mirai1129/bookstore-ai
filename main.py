from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from predict_fuse import get_predict_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

@app.post("/checkBook")
async def check_book():
    return get_predict_data()

@app.post("/uploadImage")
async def upload_image(image):
    pass
