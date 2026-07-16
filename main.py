from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="My FastAPI Application",
    description="This is a simple Crud application for managing tasks.",
    version="1.0.0",
)

tasks = [
    {"id": 1, "title": "Start The DB server", "done": False},
    {"id": 2, "title": "Check The DB server", "done": False},
    {"id": 3, "title": "Stopped the DB server", "done": True},
]

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
