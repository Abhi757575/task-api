from fastapi import FastAPI


app = FastAPI(
    title="My FastAPI Application",
    description="This is a simple Crud application for managing tasks.",
    version="1.0.0",
)

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

