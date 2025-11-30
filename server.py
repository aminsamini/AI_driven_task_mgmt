from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from starlette.middleware.sessions import SessionMiddleware
from database.models import User
from tools import auth
from tools.task_tools import get_all_tasks, update_task_status
from agents.task_agents import TaskCreationWorkflow
import uvicorn
import os
import config
from database import init_db

import logging

# Setup environment
config.setup_environment()
init_db()

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="some-random-secret-key")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    position: Optional[str] = None
    job_description: Optional[str] = None

class TaskRequest(BaseModel):
    description: str

class TaskStatusUpdate(BaseModel):
    status: str

@app.post("/api/login")
async def login(request: Request, login_data: LoginRequest):
    user = auth.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    request.session["user_id"] = user.id
    request.session["user_email"] = user.email
    request.session["user_name"] = f"{user.first_name} {user.last_name}"
    
    return {"message": "Login successful", "user": {"name": f"{user.first_name} {user.last_name}", "email": user.email}}

@app.post("/api/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}

@app.post("/api/register")
async def register(request: Request, register_data: RegisterRequest):
    try:
        user = auth.create_user(
            register_data.first_name,
            register_data.last_name,
            register_data.email,
            register_data.password,
            register_data.position,
            register_data.job_description
        )
        request.session["user_id"] = user.id
        request.session["user_email"] = user.email
        request.session["user_name"] = f"{user.first_name} {user.last_name}"
        return {"message": "Registration successful", "user": {"name": f"{user.first_name} {user.last_name}", "email": user.email}}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/me")
async def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"id": user_id, "name": request.session.get("user_name"), "email": request.session.get("user_email")}

@app.post("/api/tasks")
async def create_task(request: Request, task_data: TaskRequest):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    print(f"Creating task for user {user_id}: {task_data.description}")
    try:
        workflow = TaskCreationWorkflow(user_id)
        result = await workflow.run(task_data.description)
        print(f"Task creation result: {result}")
        return {"message": result}
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        print(f"Error creating task: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/tasks")
async def list_tasks(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    tasks = get_all_tasks()
    return tasks

@app.patch("/api/tasks/{task_id}/status")
async def update_status(task_id: int, status_update: TaskStatusUpdate, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    success, message = update_task_status(task_id, status_update.status)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}

@app.get("/")
async def read_root():
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
