from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from db import DataBase, UserModel, MessageModel
from uvicorn import run
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Уровень логирования (можно заменить на DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат вывода логов
    handlers=[
        logging.StreamHandler(),  # Вывод логов в консоль
        logging.FileHandler('app.log')  # Вывод логов в файл
    ]
)

db = DataBase()


@asynccontextmanager
async def lifespan(app: FastAPI):

    await db.init_index()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или список конкретных доменов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
async def register_user(user: UserModel):
    print(user)
    success = await db.add_user(user)
    if not success:
        raise HTTPException(status_code=409, detail="User already exists.")
    return {"status": "User registered"}

@app.get("/user/{username}")
async def get_user_key(username: str):
    user = await db.get_public_key(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@app.get("/lookup/{public_key}")
async def get_user_by_key(public_key: str):
    user = await db.get_user(public_key)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@app.post("/send")
async def send_message(message: MessageModel):
    success = await db.add_msg(message)
    return {"status": "Message stored"} if success else {"status": "Failed"}

@app.get("/messages/{public_key}")
async def fetch_messages(public_key: str, last: float = 0):
    messages = await db.get_user_msg(public_key, last)
    return messages

@app.get("/dialog/{dialog_hash}")
async def fetch_dialog_msg(dialog_hash: str, last: float = 0):
    messages = await db.get_dialog_msg(dialog_hash, last)
    return messages

@app.get("/dialogs/{public_key}")
async def fetch_dialogs(public_key: str):
    messages = await db.get_chats(public_key)
    return messages

@app.get("/users/{query}")
async def fetch_users(query: str):
    return await db.get_users(query)

if __name__ == "__main__":
    run(app)