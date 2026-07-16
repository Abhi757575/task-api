from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import Response



app = FastAPI(
    title="My FastAPI Application",
    description="This is a simple Crud application for managing tasks.",
    version="1.0.0",
    contact={
        "github_username": "Abhi757575",
        "email": "abhimanyuraj2005@gmail.com",
    },
)



tasks = [
    {"id": 1, "title": "Start The DB server", "done": False},
    {"id": 2, "title": "Check The DB server", "done": False},
    {"id": 3, "title": "Stopped the DB server", "done": True},
]

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None    

@app.get("/", summary = "API Information")
def root():
    return {
        "name ": "Task API",
        "version": "1.0.0",
        "endpoints": [
            "/tasks"
        ]
    }

@app.get("/health", summary="Health Check")
def health():
    return {
        "status": "ok"
    }


@app.get("/tasks/{task_id}", summary="Get Task by ID")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
        
    raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")    

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    # Validate title
    if not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    # Generate next ID
    new_id = max(t["id"] for t in tasks) + 1 if tasks else 1

    # Create new task
    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task

@app.put("/tasks/{task_id}", summary="Update Task",description="Updates the title and/or completion status of an existing task."
)
def update_task(task_id: int, updated_task: TaskUpdate):

    for task in tasks:
        if task["id"] == task_id:

            if updated_task.title is not None:
                if not updated_task.title.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="Title cannot be empty"
                    )
                task["title"] = updated_task.title

            if updated_task.done is not None:
                task["done"] = updated_task.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task",    description="Deletes a task by its ID."
)
def delete_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return Response(status_code=204)

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )