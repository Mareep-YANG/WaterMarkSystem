from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from datasets import load_from_disk
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.core import tasks
from app.dbModels import Dataset
from app.evaluation.attacker import ATTACKERS, get_attacker
from app.evaluation.detectability import evaluation_detectability
from app.evaluation.quality import evaluation_quality
from app.evaluation.robustness import evaluation_robustness
from app.watermarks import get_watermark_algorithm

router = APIRouter()


class EvaluationRequest(BaseModel):
	algorithm: str
	metrics: List[str]
	watermark_params: Dict[str, Any] = {}
	params: Dict[str, Any] = {}
	attack_params: Dict[str, Any] = {}
	dataset_id: str


class EvaluationResponse(BaseModel):
	metrics: List[Any]


class AttackResponse(BaseModel):
	attacked_text: str
	success_rate: float
	details: Dict[str, Any]


async def process_evaluate_watermark_task(task_id: str):
	with tasks.task_lock:
		task = tasks.tasks.get(task_id)
		if not task:
			return
		task["status"] = tasks.TaskStatus.PROCESSING
	
	try:
		request_data = task["request"]
		# 执行原有评估逻辑
		metrics_results = []
		dataset_record = await Dataset.get(id=request_data["dataset_id"])
		dataset = load_from_disk(dataset_record.storage_path)
		watermark = get_watermark_algorithm(
			request_data["algorithm"],
			**request_data["watermark_params"]
		)
		# 获取水印算法实例
		# 计算每个请求的指标
		for metric_name in request_data["metrics"]:
			if metric_name == "robustness":
				# 鲁棒性评估
				metrics_results.append(
					{"type": "robustness",
					 "content": evaluation_robustness(
						 watermark=watermark,
						 dataset=dataset,
						 attacker=get_attacker(request_data["params"]["attack_name"], **request_data["attack_params"]),
					 )
					 }
				)
			elif metric_name == "quality":
				# 文本质量评估
				metrics_results.append(
					{"type": "quality",
					 "content": evaluation_quality(
						 watermark=watermark,
						 dataset=dataset,
						 metrics=request_data["params"]["quality_metrics"]
					 )
					 }
				)

			elif metric_name == "detectability":
				# 可检测性评估
				metrics_results.append(
					{"type": "detectability",
					 "content": evaluation_detectability(
						 watermark=watermark,
						 dataset=dataset,
					 )
					 }
				)
		
		with tasks.task_lock:
			tasks.tasks[task_id].update(
				{
					"status": tasks.TaskStatus.COMPLETED,
					"result": {"metrics": metrics_results},
					"completed_at": datetime.now()
				}
			)
	
	except Exception as e:
		error_msg = f"Evaluation failed: {str(e)}"
		with tasks.task_lock:
			tasks.tasks[task_id].update(
				{
					"status": tasks.TaskStatus.FAILED,
					"error": error_msg,
					"completed_at": datetime.now()
				}
			)


@router.post("/metrics", response_model=tasks.TaskResponse)
async def evaluate_watermark(
	request: EvaluationRequest,
	background_tasks: BackgroundTasks
) -> Any:
	"""
	评估水印算法性能
	"""
	task_id = str(uuid4())
	created_at = datetime.now()
	
	with tasks.task_lock:
		tasks.tasks[task_id] = {
			"status": tasks.TaskStatus.PENDING,
			"created_at": created_at,
			"request": request.model_dump(),
			"result": None,
			"error": None,
			"completed_at": None
		}
	
	background_tasks.add_task(process_evaluate_watermark_task, task_id)
	
	return {
		"task_id": task_id,
		"status": tasks.TaskStatus.PENDING,
		"created_at": created_at
	}


@router.post("/attackers")
async def list_attackers() -> Any:
    """
    获取所有支持的攻击算法
    """
    attackers_results = []
    for name, attacker_class in ATTACKERS.items():
        attacker = attacker_class()
        attackers_results.append(
            {
                "name": name,
                "description": attacker.__doc__ or "No description available",
                "params":  attacker.to_config()
            }
        )
    return attackers_results
