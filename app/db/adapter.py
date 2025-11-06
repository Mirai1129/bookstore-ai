from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings


class MongoDBAdapter:
    def __init__(self, conn_str: str, db_name: str):
        self.client: MongoClient | None = None
        self.db: Database | None = None

        self.connection_string = conn_str
        self.database_name = db_name

        print(f"DBManager initialized for db: '{db_name}' (not connected yet).")

    def _connect(self):
        print("Connecting to MongoDB...")
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]

            self.client.admin.command('ping')
            print("✅ MongoDB connection successful!")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None

    def get_db(self) -> Database:
        if self.db is None:
            print("DB connection is None, establishing connection...")
            self._connect()

        if self.db is None:
            raise RuntimeError("Database connection could not be established.")

        return self.db

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")


db_manager = MongoDBAdapter(
    conn_str=settings.MONGODB_CONNECTION_STRING,
    db_name=settings.DATABASE_NAME
)


def get_db() -> Database:
    return db_manager.get_db()
