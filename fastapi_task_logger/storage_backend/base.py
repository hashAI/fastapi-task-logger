from abc import ABC, abstractmethod
import datetime

class TaskStorage(ABC):
    @abstractmethod
    async def create_task(self, task_id: str, task_name: str, start_time: datetime, input_params: dict):
        """Create a new task record."""
        pass

    @abstractmethod
    async def update_task_status(self, task_id: str, status: str, end_time=None, error=None):
        """Update the status of an existing task."""
        pass

    @abstractmethod
    async def log_task_progress(self, task_id: str, message: str):
        """Log progress for a task."""
        pass

    @abstractmethod
    async def fetch_task(self, task_id: str):
        """Fetch task details by ID."""
        pass

    @abstractmethod
    async def fetch_tasks(self):
        """Fetch tasks."""
        pass