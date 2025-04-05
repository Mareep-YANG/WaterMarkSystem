import logging
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

from ..deps import get_auth_user
from ....core import tasks
from ....dbModels.user import User
from ....watermarks import get_watermark_algorithm, LogitsWatermark, WATERMARK_ALGORITHMS

router = APIRouter()


class WatermarkRequest(BaseModel):
    text: str
    algorithm: str
    params: Dict[str, Any] = {}


class WatermarkResponse(BaseModel):
    watermarked_text: str
    metadata: Dict[str, Any]


class DetectionRequest(BaseModel):
    text: str
    algorithm: str
    params: Dict[str, Any] = {}


class DetectionResponse(BaseModel):
    detected: bool
    confidence: float


class AlgorithmInfo(BaseModel):
    name: str
    description: str
    type: str  # "logits" or "semantic"
    params: Dict[str, Any]


async def process_embed_watermark_task(task_id: str):
    with tasks.task_lock:
        task = tasks.tasks.get(task_id)
        if not task:
            return
        task["status"] = tasks.TaskStatus.PROCESSING
    
    try:
        request = WatermarkRequest(**task["request"])
        watermark = get_watermark_algorithm(request.algorithm, **request.params)
        
        # 使用线程池处理CPU密集型操作
        if isinstance(watermark, LogitsWatermark):
            watermarked_text = await run_in_threadpool(watermark.embed, request.text)
            metadata = {"type": "logits"}
        else:
            watermarked_text = ""  # 语义水印实现
            metadata = dict()
        
        with tasks.task_lock:
            tasks.tasks[task_id].update(
                {
                    "status": tasks.TaskStatus.COMPLETED,
                    "result": {
                        "watermarked_text": watermarked_text,
                        "metadata": metadata
                    },
                    "completed_at": datetime.now()
                }
            )
    
    except Exception as e:
        with tasks.task_lock:
            tasks.tasks[task_id].update(
                {
                    "status": tasks.TaskStatus.FAILED,
                    "error": str(e),
                    "completed_at": datetime.now()
                }
            )


async def process_detect_watermark_task(task_id: str):
    with tasks.task_lock:
        task = tasks.tasks.get(task_id)
        if not task:
            return
        task["status"] = tasks.TaskStatus.PROCESSING
    
    try:
        # 从任务记录中恢复请求参数
        request_data = task["request"]
        detection_request = DetectionRequest(
            text=request_data["text"],
            algorithm=request_data["algorithm"],
            params=request_data["params"]
        )
        
        # 执行检测逻辑
        watermark = get_watermark_algorithm(
            detection_request.algorithm,
            **detection_request.params
        )
        
        # 使用线程池处理同步方法
        detection_result = await run_in_threadpool(
            watermark.detect,
            detection_request.text
        )
        
        with tasks.task_lock:
            tasks.tasks[task_id].update(
                {
                    "status": tasks.TaskStatus.COMPLETED,
                    "result": {
                        "detected": detection_result.detected,
                        "confidence": detection_result.confidence
                    },
                    "completed_at": datetime.now()
                }
            )
    
    except Exception as e:
        error_msg = f"Detection failed: {str(e)}"
        logging.error(error_msg)
        with tasks.task_lock:
            tasks.tasks[task_id].update(
                {
                    "status": tasks.TaskStatus.FAILED,
                    "error": error_msg,
                    "completed_at": datetime.now()
                }
            )


@router.get("/algorithms", response_model=List[AlgorithmInfo])
async def list_algorithms() -> Any:
    """
    获取所有支持的水印算法
    """
    # 水印列表
    algorithms = []
    for name, algo_class in WATERMARK_ALGORITHMS.items():  # 遍历水印包获取水印算法
        algorithms.append(
            {
                "name": name,
                "description": algo_class.__doc__ or "No description available",
                "type": "logits" if hasattr(algo_class, "get_processor") else "semantic",
                "params": {
                    # 这里可以添加算法支持的参数说明
                    # 例如DIP的projection_dim, threshold等
                    "key": "秘钥"
                    # TODO: 每个水印的参数系统，和可能的自动调参功能
                }
            }
        )
    return algorithms


@router.post("/embed", response_model=tasks.TaskResponse)
async def embed_watermark(
    request: WatermarkRequest,
    background_tasks: BackgroundTasks,
) -> Any:
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
    
    background_tasks.add_task(process_embed_watermark_task, task_id)
    
    return {
        "task_id": task_id,
        "status": tasks.TaskStatus.PENDING,
        "created_at": created_at
    }


@router.post("/detect", response_model=tasks.TaskResponse)
async def detect_watermark(
    request: DetectionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_auth_user),  # 保持鉴权逻辑
) -> Any:
    task_id = str(uuid4())
    created_at = datetime.now()
    
    with tasks.task_lock:
        tasks.tasks[task_id] = {
            "status": tasks.TaskStatus.PENDING,
            "created_at": created_at,
            "request": {
                **request.model_dump(),
                "user_id": current_user.id  # 记录发起用户
            },
            "result": None,
            "error": None,
            "completed_at": None
        }
    
    background_tasks.add_task(process_detect_watermark_task, task_id)
    
    return {
        "task_id": task_id,
        "status": tasks.TaskStatus.PENDING,
        "created_at": created_at
    }


@router.post("/visualize")
async def visualize_watermark(
    request: DetectionRequest,
    current_user: User = Depends(get_auth_user)
) -> Any:
    """
    可视化水印检测结果
    """
    try:
        # 获取水印算法实例
        watermark = get_watermark_algorithm(request.algorithm, **request.params)
        
        # 生成可视化数据
        visualization_data = watermark.visualize(request.text)
        
        return visualization_data
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
