from fastapi import APIRouter, Depends, HTTPException
from app.schemas import TaskCreate, TaskOut, StatusUpdate
from app.dependencies import get_current_user, get_storage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=201)
def create_task(
    task: TaskCreate,
    user: dict = Depends(get_current_user),
    store=Depends(get_storage)
):
    task_data = task.model_dump()
    task_data["owner_id"] = user["id"]
    return store.add(task_data)


@router.get("", response_model=list[TaskOut])
def get_tasks(
    status: str = None,
    min_priority: int = None,
    user: dict = Depends(get_current_user),
    store=Depends(get_storage)
):
    tasks = store.get_all(owner_id=user["id"])
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if min_priority is not None:
        tasks = [t for t in tasks if t["priority"] >= min_priority]
    return tasks


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    user: dict = Depends(get_current_user),
    store=Depends(get_storage)
):
    task = store.get(task_id)
    if not task or task["owner_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_status(
    task_id: int,
    status_update: StatusUpdate,
    user: dict = Depends(get_current_user),
    store=Depends(get_storage)
):
    task = store.get(task_id)
    if not task or task["owner_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Task not found")
    task["status"] = status_update.status
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user: dict = Depends(get_current_user),
    store=Depends(get_storage)
):
    task = store.get(task_id)
    if not task or task["owner_id"] != user["id"]:
        raise HTTPException(status_code=404, detail="Task not found")
    store.delete(task_id)