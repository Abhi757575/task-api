"""
main.py — FastAPI application with pluggable storage backend.

Which repository is used is determined by the DATABASE_URL environment
variable:
  • Set     → PgTaskRepository  (persistent, needs Postgres)
  • Not set → MemoryTaskRepository (ephemeral, no dependencies)

Routes and request/response schemas are IDENTICAL regardless of backend.
"""

import os
from contextlib import asynccontextmanager

# pyrefly: ignore [missing-import]
import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

from repository import TaskRepository

# ---------------------------------------------------------------------------
# Load .env (no-ops gracefully if the file is missing)
# ---------------------------------------------------------------------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

# ---------------------------------------------------------------------------
# Application state populated during lifespan
# ---------------------------------------------------------------------------
repo: TaskRepository  # set during startup


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Create / tear-down the repository and optional Redis connection."""
    global repo

    pool: asyncpg.Pool | None = None
    redis_conn = None

    if DATABASE_URL:
        # --- Postgres backend ---
        from pg_repository import PgTaskRepository

        pool = await asyncpg.create_pool(DATABASE_URL)
        repo = PgTaskRepository(pool)
        print("✅ Connected to PostgreSQL")
    else:
        # --- Fallback to in-memory ---
        from memory_repository import MemoryTaskRepository

        repo = MemoryTaskRepository()
        print("⚠️  No DATABASE_URL — using in-memory storage (data will not persist)")

    # --- Optional Redis ping (stretch goal, W4 prep) ---
    if REDIS_URL:
        try:
            # pyrefly: ignore [missing-import]
            import redis.asyncio as aioredis

            redis_conn = aioredis.from_url(REDIS_URL)
            pong = await redis_conn.ping()
            print(f"✅ Redis ping → {pong}")
        except Exception as exc:
            print(f"⚠️  Redis not available: {exc}")

    yield  # ---- application runs here ----

    # --- Cleanup ---
    if pool:
        await pool.close()
        print("🔒 PostgreSQL pool closed")
    if redis_conn:
        await redis_conn.close()
        print("🔒 Redis connection closed")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Task API",
    description="A CRUD API for managing tasks — backed by PostgreSQL.",
    version="2.0.0",
    contact={
        "github_username": "Abhi757575",
        "email": "abhimanyuraj2005@gmail.com",
    },
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------------------------------------------------------------------------
# Routes  (100 % unchanged from A2 — only `repo` calls replaced raw list ops)
# ---------------------------------------------------------------------------
@app.get("/", summary="API Information")
def root():
    return {
        "name": "Task API",
        "version": "2.0.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health", summary="Health Check")
async def health():
    """Returns OK and shows which storage backend is active."""
    backend = "postgres" if DATABASE_URL else "memory"
    return {"status": "ok", "storage": backend}


@app.get("/tasks", summary="List all tasks")
async def list_tasks():
    return await repo.get_all()


@app.get("/tasks/{task_id}", summary="Get Task by ID")
async def get_task(task_id: int):
    task = await repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    return task


@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return await repo.create(task.title)


@app.put("/tasks/{task_id}", summary="Update Task",
         description="Updates the title and/or completion status of an existing task.")
async def update_task(task_id: int, updated_task: TaskUpdate):
    if updated_task.title is not None and not updated_task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    result = await repo.update(task_id, title=updated_task.title, done=updated_task.done)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return result


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task",
            description="Deletes a task by its ID.")
async def delete_task(task_id: int):
    deleted = await repo.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return Response(status_code=204)