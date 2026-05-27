from fastapi import Header, HTTPException
from app.storage import storage


def get_current_user(
    x_user_id: int = Header(None, alias="X-User-Id"),
    x_user_role: str = Header(default="user", alias="X-User-Role")
):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id required")
    return {"id": int(x_user_id), "role": x_user_role}


def require_admin(user: dict = None):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def get_storage():
    return storage