from itertools import count


class TaskStorage:
    def __init__(self):
        self.db: dict[int, dict] = {}
        self._id_seq = count(start=1)

    def add(self, task: dict) -> dict:
        task["id"] = next(self._id_seq)
        self.db[task["id"]] = task
        return task

    def get_all(self, owner_id: int = None) -> list[dict]:
        result = []
        for t in self.db.values():
            if owner_id is not None and t["owner_id"] != owner_id:
                continue
            result.append(t)
        return result

    def get(self, task_id: int) -> dict | None:
        return self.db.get(task_id)

    def delete(self, task_id: int) -> bool:
        if task_id in self.db:
            del self.db[task_id]
            return True
        return False

    def clear(self):
        self.db.clear()


storage = TaskStorage()