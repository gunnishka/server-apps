from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

app = FastAPI(title="User Creation API")

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    is_subscribed: Optional[bool] = False
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, value:str) -> str:
        if not value.strip():
            raise ValueError("Имя не может быть пустым")
        if len(value.strip()) < 2:
            raise ValueError("Имя должно быть не менее 2 символов")
        return value

    @field_validator('age')
    @classmethod
    def validate_age(cls, value: int) -> int:
        if value <= 0: 
            raise ValueError("Возраст не может быть отрицательным")
        return value
    
@app.post("/create_user", response_model=UserCreate, status_code=201)
async def create_user(user: UserCreate):
    return user
    