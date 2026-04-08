from fastapi import FastAPI, HTTPException, Response, Header, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import Annotated
import time
import uuid
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired

app = FastAPI(title="FastAPI Auth & Headers Demo")

SECRET_KEY = "super-secret-key-change-in-production-123456789"
signer = TimestampSigner(SECRET_KEY)

USERS = {
    "user123": {
        "password": "password123",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Иван Иванов"
    }
}


class LoginData(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(data: LoginData, response: Response):
    user = USERS.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail={"message": "Invalid credentials"})

    user_id = user["user_id"]
    timestamp = int(time.time())
    token = signer.sign(f"{user_id}.{timestamp}").decode("utf-8")

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=300
    )

    return {"message": "Login successful"}


def get_current_user(session_token: Annotated[str | None, Header()] = None):
    if not session_token:
        raise HTTPException(status_code=401, detail={"message": "Unauthorized"})

    try:
        data = signer.unsign(session_token, max_age=300, return_timestamp=True)
        payload, server_ts = data
        payload_str = payload.decode("utf-8")
        user_id, last_activity_str = payload_str.split(".")
        last_activity = int(last_activity_str)

        current_time = int(time.time())
        elapsed = current_time - last_activity

        if elapsed > 300:
            raise HTTPException(status_code=401, detail={"message": "Session expired"})

        user = next((u for u in USERS.values() if u["user_id"] == user_id), None)
        if not user:
            raise HTTPException(status_code=401, detail={"message": "Invalid session"})

        if elapsed >= 180:
            new_timestamp = current_time
            new_token = signer.sign(f"{user_id}.{new_timestamp}").decode("utf-8")
            return {"user": user, "new_token": new_token}

        return {"user": user, "new_token": None}

    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})
    except Exception:
        raise HTTPException(status_code=401, detail={"message": "Invalid session"})


@app.get("/profile")
async def profile(current_user: dict = Depends(get_current_user), response: Response = None):
    user = current_user["user"]
    new_token = current_user["new_token"]

    if new_token and response:
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=300
        )

    return {
        "message": "Profile accessed successfully",
        "user_id": user["user_id"],
        "username": user.get("name", "Unknown")
    }


class CommonHeaders(BaseModel):
    user_agent: Annotated[str, Header(alias="User-Agent")]
    accept_language: Annotated[str, Header(alias="Accept-Language")]

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        if not v or "," not in v:
            raise ValueError("Accept-Language должен содержать хотя бы один язык")
        return v


@app.get("/headers")
async def get_headers(headers: Annotated[CommonHeaders, Header()]):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }


@app.get("/info")
async def get_info(headers: Annotated[CommonHeaders, Header()], response: Response):
    response.headers["X-Server-Time"] = time.strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }