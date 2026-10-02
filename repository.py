"""
repository.py — Repository interface (abstract base class) for task storage.

Any concrete repository (in-memory, Postgres, etc.) must implement these
methods.  The service layer and routes depend ONLY on this interface.
"""

from abc import ABC, abstractmethod
from typing import Optional


class TaskRepository(ABC):
    """Abstract base class defining the task storage contract."""

    @abstractmethod
    async def get_all(self) -> list[dict]:
        """Return every task as a list of dicts."""
        ...

    @abstractmethod
    async def get_by_id(self, task_id: int) -> Optional[dict]:
        """Return a single task dict, or None if not found."""
        ...

    @abstractmethod
    async def create(self, title: str) -> dict:
        """Insert a new task and return it (with generated id)."""
        ...

    @abstractmethod
    async def update(self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[dict]:
        """Update fields of an existing task.  Return the updated task, or None."""
        ...

    @abstractmethod
    async def delete(self, task_id: int) -> bool:
        """Delete a task by id.  Return True if deleted, False if not found."""
        ...
