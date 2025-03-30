from typing import Any, Dict, List

from datasets import load_from_disk
from fastapi import (
    APIRouter, Depends,
    HTTPException, status
)
from pydantic import BaseModel

from ..deps import get_auth_user
from ....dbModels import Dataset
from ....dbModels.user import User
from ....evaluation.attacker import ATTACKERS, get_attacker
from ....evaluation.detectability import evaluation_detectability
from ....evaluation.quality import evaluation_quality
from ....evaluation.robustness import evaluation_robustness
from ....watermarks import get_watermark_algorithm

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


@router.post("/metrics", response_model=EvaluationResponse)
async def evaluate_watermark(
        request: EvaluationRequest,
) -> Any:
    """
    评估水印算法性能
    """
    try:
        metrics_results = []
        # 获取数据集
        dataset_record = await Dataset.get(id=request.dataset_id)
        if not dataset_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        dataset = load_from_disk(dataset_record.storage_path)
        # 获取水印算法实例
        watermark = get_watermark_algorithm(request.algorithm, **request.watermark_params)  # 传入水印名和参数，获取水印算法实例
        # 计算每个请求的指标
        for metric_name in request.metrics:
            if metric_name == "robustness":
                # 鲁棒性评估
                metrics_results.append(
                    {"type": "robustness",
                     "content": evaluation_robustness(
                         watermark=watermark,
                         dataset=dataset,
                         attacker=get_attacker(request.params["attack_name"], **request.attack_params),
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
                         metrics=request.params["quality_metrics"]
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

        return {"metrics": metrics_results}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/attackers")
async def list_attackers() -> Any:
    """
    获取所有支持的攻击算法
    """
    attackers_results = []
    for name, attacker_class in ATTACKERS.items():
        attackers_results.append(
            {
                "name": name,
                "description": attacker_class.__doc__ or "No description available",
                "params": {
                    # 这里可以添加攻击器支持的参数说明
                }
            }
        )
    return attackers_results
