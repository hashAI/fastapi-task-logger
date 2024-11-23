
from functools import wraps
from uuid import uuid4
from datetime import datetime, timezone

from .storage_backend.base import TaskStorage


TASK_REGISTRY = {}

def register_task(task_func):
    """Register a task in the global task registry."""
    TASK_REGISTRY[task_func.__name__] = task_func

def get_task(task_name):
    """Retrieve a task function by its name."""
    return TASK_REGISTRY.get(task_name)

class FastAPITaskLogger:
    def __init__(self, storage: TaskStorage, task_id: str):
        self.storage = storage
        self.task_id = task_id

    async def add_log(self, message: str):
        """Log progress for a task."""
        await self.storage.log_task_progress(self.task_id, message)

    async def update_status(self, status: str, end_time=None, error=None):
        """Update the status of the task."""
        await self.storage.update_task_status(self.task_id, status, end_time, error)


def log_task_status(storage):
    """Decorator to log the status of a task."""

    def decorator(func):
        register_task(func)  # Automatically register the task

        @wraps(func)
        async def wrapper(*args, clone_of=None, task_id=None, **kwargs):
            task_id = task_id or str(uuid4())
            task_name = func.__name__
            start_time = datetime.now(timezone.utc)

            # Extract input parameters (excluding `add_log` and `clone_of`)
            input_params = {
                "args": args,
                "kwargs": {k: v for k, v in kwargs.items() if k not in ["add_log", "clone_of"]},
            }

            # Initialize task in storage
            await storage.create_task(
                task_id=task_id,
                task_name=task_name,
                start_time=start_time,
                input_params=input_params,
                clone_of=clone_of,  # Track the parent task if provided
            )

            # Inject FastAPITaskLogger
            fastapi_task_logger = FastAPITaskLogger(storage, task_id)
            kwargs["add_log"] = fastapi_task_logger.add_log

            try:
                # Execute the task
                result = await func(*args, **kwargs)

                # Mark as completed
                await fastapi_task_logger.update_status(
                    status="completed", end_time=datetime.now(timezone.utc)
                )
                return result
            except Exception as e:
                # Mark as failed
                await fastapi_task_logger.update_status(
                    status="failed", end_time=datetime.now(timezone.utc), error=str(e)
                )
                raise  # Re-raise the exception for external handling

        return wrapper

    return decorator
