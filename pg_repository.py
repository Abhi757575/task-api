"""
pg_repository.py — PostgreSQL implementation of TaskRepository.

Uses asyncpg for async Postgres access.  Connection pool is created once
on startup and closed on shutdown via the lifespan hooks in main.py.
"""

# pyrefly: ignore [missing-import]
import asyncpg
from typing import Optional
from repository import TaskRepository


class PgTaskRepository(TaskRepository):
    """Stores tasks in a PostgreSQL database (data persists across restarts)."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def get_all(self) -> list[dict]:
        async with self._pool.acquire() as conn:
            rows = await conn.fetch("SELECT id, title, done FROM tasks ORDER BY id")
            return [dict(row) for row in rows]

    async def get_by_id(self, task_id: int) -> Optional[dict]:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, title, done FROM tasks WHERE id = $1", task_id
            )
            return dict(row) if row else None

    async def create(self, title: str) -> dict:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO tasks (title) VALUES ($1) RETURNING id, title, done",
                title,
            )
            return dict(row)

    async def update(self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Optional[dict]:
        async with self._pool.acquire() as conn:
            # Build SET clause dynamically
            sets: list[str] = []
            values: list = []
            idx = 1

            if title is not None:
                sets.append(f"title = ${idx}")
                values.append(title)
                idx += 1
            if done is not None:
                sets.append(f"done = ${idx}")
                values.append(done)
                idx += 1

            if not sets:
                # Nothing to update — just return the current row
                return await self.get_by_id(task_id)

            values.append(task_id)
            query = (
                f"UPDATE tasks SET {', '.join(sets)} "
                f"WHERE id = ${idx} "
                f"RETURNING id, title, done"
            )
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else None

    async def delete(self, task_id: int) -> bool:
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM tasks WHERE id = $1", task_id
            )
            # result looks like "DELETE 1" or "DELETE 0"
            return result == "DELETE 1"
