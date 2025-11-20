from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core import ENV_FILE_PATH


class Settings(BaseSettings):
    API_V1_PREFIX: str = '/api/v1'

    # Secrets
    API_SERVER_PORT: int = Field(default=8080)
    MONGODB_CONNECTION_STRING: str = Field(validation_alias='MONGODB_CONNECTION_URL')

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = Field(..., validation_alias='CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY: str = Field(..., validation_alias='CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET: str = Field(..., validation_alias='CLOUDINARY_API_SECRET')

    # Database
    DATABASE_NAME: str = Field(validation_alias='DATABASE_NAME')
    COLLECTION_NAME_BOOKS: str = "books"
    COLLECTION_NAME_CARTS: str = "carts"
    COLLECTION_NAME_USERS: str = "users"
    COLLECTION_NAME_ORDERS: str = "orders"

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        extra='ignore'
    )


settings = Settings()
