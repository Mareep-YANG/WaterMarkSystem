from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_auth_user, get_db
from app.models.user import User
from app.watermarks import get_watermark_algorithm
from pydantic import BaseModel

router = APIRouter()

class EvaluationRequest(BaseModel):
    original_text: str
    watermarked_text: str
    algorithm: str
    key: str
    metrics: List[str]
    params: Dict[str, Any] = {}

class AttackRequest(BaseModel):
    text: str
    algorithm: str
    key: str
    attack_type: str
    attack_params: Dict[str, Any] = {}

class EvaluationResponse(BaseModel):
    metrics: Dict[str, float]
    details: Dict[str, Any]

class AttackResponse(BaseModel):
    attacked_text: str
    success_rate: float
    details: Dict[str, Any]

@router.post("/metrics", response_model=EvaluationResponse)
async def evaluate_watermark(
    request: EvaluationRequest,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    评估水印算法性能
    """
    try:
        watermark = get_watermark_algorithm(request.algorithm, **request.params)
        metrics_results = {}
        details = {}

        # 计算每个请求的指标
        for metric_name in request.metrics:
            if metric_name == "robustness":
                # 鲁棒性评估
                detection_before = watermark.detect(request.watermarked_text, request.key)
                # 模拟一些文本变换
                transformed_texts = [
                    request.watermarked_text.lower(),  # 转小写
                    " ".join(request.watermarked_text.split()),  # 空格标准化
                    request.watermarked_text[:len(request.watermarked_text)//2]  # 截断
                ]
                detections_after = [
                    watermark.detect(text, request.key)["detected"]
                    for text in transformed_texts
                ]
                robustness_score = sum(detections_after) / len(detections_after)
                metrics_results["robustness"] = robustness_score
                details["robustness"] = {
                    "transformations": len(transformed_texts),
                    "successful_detections": sum(detections_after)
                }
                
            elif metric_name == "quality":
                # 文本质量评估
                from nltk.translate.bleu_score import sentence_bleu
                bleu_score = sentence_bleu(
                    [request.original_text.split()],
                    request.watermarked_text.split()
                )
                metrics_results["quality"] = bleu_score
                details["quality"] = {
                    "bleu_score": bleu_score
                }
                
            elif metric_name == "security":
                # 安全性评估
                detection_result = watermark.detect(request.watermarked_text, request.key)
                wrong_key_detection = watermark.detect(
                    request.watermarked_text,
                    request.key + "_wrong"
                )
                security_score = float(detection_result["detected"]) - \
                               float(wrong_key_detection["detected"])
                metrics_results["security"] = max(0, security_score)
                details["security"] = {
                    "true_positive": detection_result["detected"],
                    "false_positive": wrong_key_detection["detected"]
                }

        return {
            "metrics": metrics_results,
            "details": details
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/attack", response_model=AttackResponse)
async def attack_watermark(
    request: AttackRequest,
    current_user: User = Depends(get_auth_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    对水印文本进行攻击测试
    """
    try:
        watermark = get_watermark_algorithm(request.algorithm)
        
        # 获取原始检测结果
        original_detection = watermark.detect(request.text, request.key)
        
        attacked_text = request.text
        if request.attack_type == "text":
            # 文本层面攻击（例如同义词替换）
            # 这里需要实现具体的攻击逻辑
            words = attacked_text.split()
            # 示例：随机删除一些词
            import random
            attacked_text = " ".join(
                word for word in words 
                if random.random() > 0.1
            )
            
        elif request.attack_type == "semantic":
            # 语义层面攻击（例如改写）
            # 这里需要实现具体的攻击逻辑
            pass
            
        elif request.attack_type == "logits":
            # Logits层面攻击
            # 这里需要实现具体的攻击逻辑
            pass
        
        # 获取攻击后的检测结果
        attacked_detection = watermark.detect(attacked_text, request.key)
        
        # 计算攻击成功率
        success_rate = 1.0 if not attacked_detection["detected"] else 0.0
        
        return {
            "attacked_text": attacked_text,
            "success_rate": success_rate,
            "details": {
                "original_detection": original_detection,
                "attacked_detection": attacked_detection,
                "attack_type": request.attack_type
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )