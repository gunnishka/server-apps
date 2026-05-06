from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db_connection, create_tables

app = FastAPI()

create_tables()


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: str
    description: str
    completed: bool


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool


def row_to_todo(row) -> TodoResponse:
    return TodoResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"]),
    )

@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO todos (title, description, completed) VALUES (?, ?, 0)",
        (todo.title, todo.description),
    )
    conn.commit()
    new_id = cursor.lastrowid
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return row_to_todo(row)


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Todo with id={todo_id} not found")
    return row_to_todo(row)


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate):
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Todo with id={todo_id} not found")

    conn.execute(
        "UPDATE todos SET title = ?, description = ?, completed = ? WHERE id = ?",
        (todo.title, todo.description, int(todo.completed), todo_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    conn.close()
    return row_to_todo(row)


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db_connection()
    existing = conn.execute("SELECT id FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Todo with id={todo_id} not found")

    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
    return {"message": f"Todo with id={todo_id} deleted successfully"}