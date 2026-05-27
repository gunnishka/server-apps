from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, EmailStr, conint, constr
from typing import Optional

app = FastAPI()

class CustomExceptionA(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        self.status_code = 400

class CustomExceptionB(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        self.status_code = 404

@app.exception_handler(CustomExceptionA)
async def handler_exception_a(request: Request, exc: CustomExceptionA):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "detail": exc.detail}
    )

@app.exception_handler(CustomExceptionB)
async def handler_exception_b(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status_code": exc.status_code, "detail": exc.detail}
    )

class User(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = 'Unknown'

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('username must be at least 3 characters')
        return v

class ValuePayload(BaseModel):
    value: int

@app.post("/validate-user", response_model=dict)
async def validate_user(user: User):
    return {"username": user.username, "email": user.email, "status": "valid"}

@app.post("/condition-endpoint")
async def condition_endpoint(payload: ValuePayload):
    if payload.value < 0:
        raise CustomExceptionA("Value must be positive")
    return {"value": payload.value}

@app.get("/resource/{resource_id}")
async def get_resource(resource_id: int):
    if resource_id > 100:
        raise CustomExceptionB("Resource not found")
    return {"id": resource_id, "name": f"Resource {resource_id}"}
