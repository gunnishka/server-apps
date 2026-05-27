from fastapi import APIRouter, Depends
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return user


@router.get("/{user_id}")
def get_user(user_id: int, user: dict = Depends(get_current_user)):
    return {"requested_id": user_id, "current_user": user}