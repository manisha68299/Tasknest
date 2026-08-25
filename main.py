from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

app = FastAPI(title="Task API", version="1.0")

tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build a CRUD API", "done": False},
    {"id": 3, "title": "Write documentation", "done": True},
]


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


class TaskCreate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None


@app.get("/")
def root():
    """Return API name, version, and available endpoints."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    """List all tasks in memory."""
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """Get a single task by id."""
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.post("/tasks", status_code=201)
def create_task(body: TaskCreate):
    """Create a new task with an auto-assigned id."""
    if body.title is None or not str(body.title).strip():
        raise HTTPException(status_code=400, detail="title is required and must not be empty")
    new_id = max((t["id"] for t in tasks), default=0) + 1
    task = {"id": new_id, "title": str(body.title).strip(), "done": bool(body.done)}
    tasks.append(task)
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    """Update an existing task's title and/or done status."""
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if body.title is not None:
        if not str(body.title).strip():
            raise HTTPException(status_code=400, detail="title must not be empty")
        task["title"] = str(body.title).strip()
    if body.done is not None:
        task["done"] = body.done
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    """Delete a task by id."""
    task = find_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    tasks.remove(task)
    return Response(status_code=204)
