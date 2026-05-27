import os
from fastapi import FastAPI
from app.routers import tasks, users, admin, websocket
from app.room_manager import manager

app = FastAPI(title="Task Manager")

app.include_router(tasks.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(websocket.router)


@app.get("/health")
def health():
    return {"status": "ok", "env": os.getenv("APP_ENV", "local")}


@app.get("/rooms/{room_id}/users")
def get_room_users(room_id: str):
    return {"room_id": room_id, "users": manager.get_users(room_id)}