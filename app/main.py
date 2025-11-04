from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.ai_endpoints import router as ai_endpoints_router
from app.api.v1.db_endpoints import router as db_endpoints_router
from app.core.config import settings

app = FastAPI()

# TODO fix CORS

# origins = [
#     "http://localhost",
#     "http://localhost:3000",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(
    router=ai_endpoints_router,
    prefix=settings.API_V1_PREFIX,
    tags=["AI"]
)

app.include_router(
    router=db_endpoints_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Database"]
)

app.get("/")
async def index():
    return {"message": "Hello, World!"}
