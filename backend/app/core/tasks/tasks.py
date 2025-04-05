from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


class TaskStatus(str, Enum):
	PENDING = "pending"  # 排队
	PROCESSING = "processing"  # 处理中
	COMPLETED = "completed"  # 完成
	FAILED = "failed"  # 失败


class TaskResponse(BaseModel):
	task_id: str
	status: TaskStatus
	result: Optional[Dict] = None
	error: Optional[str] = None
	created_at: datetime
	completed_at: Optional[datetime] = None


# 内存任务存储结构
tasks: Dict[str, Dict] = {}
task_lock = Lock()

router = APIRouter(
	tags=["tasks"]
)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
	with task_lock:
		task = tasks.get(task_id)
	
	if not task:
		raise HTTPException(status_code=404, detail="Task not found")
	
	return {
		"task_id": task_id,
		"status": task["status"],
		"result": task["result"],
		"error": task["error"],
		"created_at": task["created_at"],
		"completed_at": task["completed_at"]
	}
