from datetime import datetime, timezone
from .base import TaskStorage

import logging
logger = logging.getLogger(__name__)

class InMemoryTaskStorage(TaskStorage):
    def __init__(self):
        self.store = {}

    async def create_task(self, task_id: str, task_name: str, start_time: datetime, input_params: dict, clone_of: str=None):
        logger.info(f"Background Task task_id: {task_id}, task_name: {task_name}")
        self.store[task_id] = {
            "task_name": task_name,
            "status": "started",
            "start_time": start_time,
            "input_params": input_params,
            "clone_of": clone_of,
            "progress_logs": [],
            "error": None
        }

    async def update_task_status(self, task_id: str, status: str, end_time=None, error=None):
        logger.info(f"Updating Background Task task_id: {task_id}")
        if task_id in self.store:
            self.store[task_id]["status"] = status
            if end_time:
                self.store[task_id]["end_time"] = end_time
            if error:
                self.store[task_id]["error"] = error

    async def log_task_progress(self, task_id: str, message: str):
        logger.info(f"Logged Background Task task_id: {task_id}")
        if task_id in self.store:
            log_entry = {
                "timestamp": datetime.now(timezone.utc),
                "message": message,
            }
            self.store[task_id]["progress_logs"].append(log_entry)

    async def fetch_task(self, task_id: str):
        return self.store.get(task_id)
    
    async def fetch_tasks(self):
        return [{"task_id": k, "task_details": v } for k, v in self.store.items()]

