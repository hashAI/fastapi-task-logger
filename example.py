import asyncio

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi_task_logger import InMemoryTaskStorage, log_task_status, get_task

# Initialize FastAPI app and InMemoryTaskStorage
app = FastAPI()
storage = InMemoryTaskStorage()

# Define a task
@log_task_status(storage)
async def example_task(param: int, add_log):
    await add_log("Task started")
    total_steps = 5
    for step in range(1, total_steps + 1):
        # Simulate work
        await asyncio.sleep(5)
        await add_log(f"Step {step}/{total_steps} completed")
    if int(param) < 100:
        raise ValueError("Param value should be greater than 100")
    await add_log("Task successfully completed")
    return {"message": "Task completed successfully"}

# Endpoint to start a task
@app.post("/tasks")
async def run_task(param: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(example_task, param)
    return {"message": "Task has been scheduled"}

# Endpoint to fetch task details
@app.get("/tasks")
async def get_task_details():
    return await storage.fetch_tasks()

# Endpoint to fetch task details
@app.get("/tasks/{task_id}")
async def get_task_details(task_id: str):
    task_details = await storage.fetch_task(task_id)
    if not task_details:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_details

# Endpoint to restart a task
@app.post("/tasks/{task_id}/rerun")
async def restart_task(task_id: str, background_tasks: BackgroundTasks):
    task_details = await storage.fetch_task(task_id)
    if not task_details:
        raise HTTPException(status_code=404, detail="Task not found")

    # Ensure task is restartable
    if task_details["status"] not in ["failed", "completed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Task is currently {task_details['status']} and cannot be restarted",
        )

    # Retrieve the task function and input parameters
    task_func = get_task(task_details["task_name"])
    if not task_func:
        raise HTTPException(status_code=404, detail="Task function not found")

    input_params = task_details["input_params"]
    background_tasks.add_task(log_task_status(storage)(task_func), *input_params["args"], **input_params["kwargs"], clone_of=task_id)
    return {"message": f"Task {task_id} has been restarted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",  # Path to your app instance
        host="127.0.0.1",  # Bind to localhost
        port=8000,  # Port to listen on
        log_level="info",  # Log level (debug, info, warning, error, critical)
        reload=True,  # Automatically reload on code changes
    )