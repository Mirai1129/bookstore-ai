import cloudinary
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.ai_endpoints import router as ai_endpoints_router
from app.api.v1.book_endpoints import router as book_endpoints_router
from app.api.v1.cart_endpoints import router as cart_endpoints_router
from app.api.v1.order_endpoints import router as order_endpoints_router
from app.api.v1.upload_images import router as upload_images_router
from app.api.v1.user_endpoints import router as user_endpoints_router
from app.core.config import settings

# Loading cloudinary config
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

app = FastAPI()

# TODO fix CORS

origins = [
    "http://localhost:5000",
    "http://127.0.0.1:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(
    router=ai_endpoints_router,
    prefix=settings.API_V1_PREFIX,
    tags=["AI"]
)

app.include_router(
    router=user_endpoints_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Database - User"]
)

app.include_router(
    router=book_endpoints_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Database - Book"]
)

app.include_router(
    router=order_endpoints_router,
    prefix=settings.API_V1_PREFIX + "/orders",
    tags=["Database - Order"]
)

app.include_router(
    router=cart_endpoints_router,
    prefix=settings.API_V1_PREFIX + "/carts",
    tags=["Carts"]
)

app.include_router(
    router=upload_images_router,
    prefix=settings.API_V1_PREFIX + "/upload/images",
    tags=["Upload"]
)


async def index():
    return {"message": "Hello, World!"}
