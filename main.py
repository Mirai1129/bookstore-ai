import torch
from PIL import Image
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from training.model_multiview import MultiViewResNet
from predict_fuse import predict_single_book

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["POST"],
    allow_headers=["*"]
)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = MultiViewResNet().to(device)
model.load_state_dict(torch.load("multiview_book_model.pt", map_location=device))
model.eval()


@app.get("/")
async def index():
    return FileResponse("index.html", media_type="text/html")

@app.post("/predict")
async def predict(
        front: UploadFile | None = File(None),
        spine: UploadFile | None = File(None),
        back: UploadFile | None = File(None)
):
    files = {
        "front": front,
        "spine": spine,
        "back": back
    }

    if not any(files.values()):
        return {"error": "請至少上傳一張圖片"}

    img_front = Image.open(front.file).convert("RGB") if front else None
    img_spine = Image.open(spine.file).convert("RGB") if spine else None
    img_back = Image.open(back.file).convert("RGB") if back else None

    result = predict_single_book(
        model=model,
        device=device,
        front_img=img_front,
        spine_img=img_spine,
        back_img=img_back
    )

    return result