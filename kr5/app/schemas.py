from pydantic import BaseModel, Field, field_validator
from typing import Optional


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: str = Field(default="todo")
    priority: int = Field(..., ge=1, le=5)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in {"todo", "in_progress", "done"}:
            raise ValueError("Status must be: todo, in_progress, done")
        return v


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: int
    owner_id: int


class StatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in {"todo", "in_progress", "done"}:
            raise ValueError("Status must be: todo, in_progress, done")
        return v