from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user, require_admin, get_storage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    user: dict = Depends(require_admin),
    store=Depends(get_storage)
):
    tasks = store.get_all()
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    for t in tasks:
        s = t["status"]
        if s in by_status:
            by_status[s] += 1
    return {"total_tasks": len(tasks), "by_status": by_status}


@router.delete("/tasks/{task_id}", status_code=204)
def delete_any_task(
    task_id: int,
    user: dict = Depends(require_admin),
    store=Depends(get_storage)
):
    if not store.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")