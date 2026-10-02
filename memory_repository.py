"""
memory_repository.py — In-memory implementation of TaskRepository.

This is the original storage mechanism.  Useful for tests or running
without a database.
"""

from typing import Optional
from repository import TaskRepository


class MemoryTaskRepository(TaskRepository):
    """Stores tasks in a plain Python list (data lost on restart)."""

    def __init__(self) -> None:
        self._tasks: list[dict] = [
            {"id": 1, "title": "Start The DB server", "done": False},
            {"id": 2, "title": "Check The DB server", "done": False},
            {"id": 3, "title": "Stopped the DB server", "done": True},
        ]

    async def get_all(self) -> list[dict]:
        return list(self._tasks)

    async def get_by_id(self, task_id: int) -> Optional[dict]:
        for task in self._tasks:
            if task["id"] == task_id:
                return task
        return None

    async def create(self, title: str) -> dict:
        new_id = max(t["id"] for t in self._tasks) + 1 if self._tasks else 1
        new_task = {"id": new_id, "title": title, "done": False}
        self._tasks.append(new_task)
        return new_task

    async def update(self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[dict]:
        for task in self._tasks:
            if task["id"] == task_id:
                if title is not None:
                    task["title"] = title
                if done is not None:
                    task["done"] = done
                return task
        return None

    async def delete(self, task_id: int) -> bool:
        for task in self._tasks:
            if task["id"] == task_id:
                self._tasks.remove(task)
                return True
        return False
