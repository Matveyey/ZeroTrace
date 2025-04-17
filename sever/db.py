import os
import motor.motor_asyncio
from pymongo.errors import DuplicateKeyError, PyMongoError
from time import time
from typing import Optional, Dict, List, Any
import logging
from pydantic import BaseModel, constr

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserModel(BaseModel):
    username: constr(min_length=3, max_length=50)  # type: ignore
    kem_public_key: str
    signature_public_key: str


class MessageModel(BaseModel):
    sender_public_key: str
    recipient_public_key: str
    shared_secret_aes_ciphertext: str
    shared_secret_kem_ciphertext: str
    ciphertext: str
    nonce: str
    shared_secret_aes_nonce: str
    signature: str
    hash_public: str
    msg_type: int
    dialog_hash: str


class DataBase:
    def __init__(self):
        mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
        self.db = self.client["zero_trace"]
        self.users_collection = self.db["users"]
        self.messages_collection = self.db["messages"]

    async def init_index(self) -> None:
        """Создает уникальные индексы для коллекций."""
        try:
            await self.users_collection.create_index(
                [("username", 1), ("public_key", 1)],
                unique=True,
                name="user_identity_index",
            )
            await self.messages_collection.create_index(
                [
                    ("sender_public_key", 1),
                    ("recipient_public_key", 1),
                    ("dialog_hash", 1),
                    ("timestamp", 1),
                ],
                name="message_route_index",
            )
            logger.info("Database indexes initialized.")
        except PyMongoError as e:
            logger.error(f"Index creation failed: {e}")
            raise

    async def get_public_key(self, username: str) -> Optional[bytes]:
        """Возвращает публичный ключ пользователя."""
        if not username:
            raise ValueError("Username cannot be empty")

        try:
            user = await self.users_collection.find_one(
                {"username": username}, {"_id": 0}
            )

            return user if user else None
        except PyMongoError as e:
            logger.error(f"Failed to fetch public key: {e}")
            raise

    async def get_user(self, public_key: str) -> Optional[Dict[str, Any]]:
        """Возвращает пользователя по публичному ключу."""
        if not public_key:
            raise ValueError("Public key cannot be empty")

        try:
            return await self.users_collection.find_one(
                {"kem_public_key": public_key}, {"_id": 0}
            )
        except PyMongoError as e:
            logger.error(f"Failed to fetch user: {e}")
            raise

    async def add_user(self, user: UserModel) -> bool:
        """Добавляет пользователя в базу. Возвращает False при дубликате."""
        try:
            await self.users_collection.insert_one(user.model_dump())
            logger.info(f"User {user.username} added successfully.")
            return True
        except DuplicateKeyError:
            logger.warning(f"User {user.username} already exists.")
            return False
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error: {e}")
            raise

    async def add_msg(self, message: MessageModel) -> bool:
        """Добавляет сообщение в базу."""
        try:
            query = {**message.model_dump(), "timestamp": time()}
            await self.messages_collection.insert_one(query)
            logger.info("Message added successfully.")
            return True
        except PyMongoError as e:
            logger.error(f"Failed to add message: {e}")
            raise

    async def get_user_msg(
        self, public_key: str, last_check_timestamp: float
    ) -> List[Dict[str, Any]]:
        """Возвращает новые сообщения для пользователя."""
        if not public_key:
            raise ValueError("Public key cannot be empty")

        try:
            cursor = self.messages_collection.find(
                {
                    "$or": [
                        {"sender_public_key": public_key},
                        {"recipient_public_key": public_key},
                    ],
                    "timestamp": {"$gt": last_check_timestamp},
                },
                {"_id": 0},
            ).sort("timestamp", 1)
            return await cursor.to_list(length=100)
        except PyMongoError as e:
            logger.error(f"Failed to fetch messages: {e}")
            raise

    async def get_dialog_msg(
        self, dialog_hash: str, last_check_timestamp: float
    ) -> List[Dict[str, Any]]:
        """Возвращает новые сообщения для чата."""
        if not dialog_hash:
            raise ValueError("dialog hash cannot be empty")

        try:
            cursor = self.messages_collection.find(
                {
                    "dialog_hash": dialog_hash,
                    "timestamp": {"$gt": last_check_timestamp},
                },
                {"_id": 0},
            ).sort("timestamp", 1)
            return await cursor.to_list(length=100)
        except PyMongoError as e:
            logger.error(f"Failed to fetch messages: {e}")
            raise

    async def get_chats(self, public_key: str):
        if not public_key:
            raise ValueError("public key cannot be empty")
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"sender_public_key": public_key},
                        {"recipient_public_key": public_key},
                    ]
                }
            },
            {
                "$group": {
                    "_id": "$dialog_hash",
                    "sender": {"$first": "$sender_public_key"},
                    "recipient": {"$first": "$recipient_public_key"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "dialog_hash": "$_id",
                    "public_key": {
                        "$cond": [
                            {"$eq": ["$sender", public_key]},
                            "$recipient",
                            "$sender",
                        ]
                    },
                }
            },
        ]
        try:
            cursor = self.messages_collection.aggregate(pipeline)
            return await cursor.to_list(length=100)
        except PyMongoError as e:
            print("looo")
            logger.error(f"Failed to fetch messages: {e}")
            raise
    async def get_users(self,query):
        cursor = self.users_collection.find({"username": { "$regex": f"^{query}", "$options": "i" }}, {"_id": 0})
        return await cursor.to_list(length=10)