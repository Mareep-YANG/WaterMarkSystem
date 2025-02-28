from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..deps import get_auth_user, get_db
from ...core.llm import llm_service
from ...models.user import User
from ...watermarks import get_watermark_algorithm, WATERMARK_ALGORITHMS

router = APIRouter()


class WatermarkRequest(BaseModel):
	text: str
	algorithm: str
	key: str
	params: Dict[str, Any] = {}


class WatermarkResponse(BaseModel):
	watermarked_text: str
	metadata: Dict[str, Any]


class DetectionRequest(BaseModel):
	text: str
	algorithm: str
	key: str
	params: Dict[str, Any] = {}


class DetectionResponse(BaseModel):
	detected: bool
	confidence: float
	details: Dict[str, Any]


class AlgorithmInfo(BaseModel):
	name: str
	description: str
	type: str  # "logits" or "semantic"
	params: Dict[str, Any]


@router.get("/algorithms", response_model=List[AlgorithmInfo])
async def list_algorithms() -> Any:
	"""
	获取所有支持的水印算法
	"""
	algorithms = []
	for name, algo_class in WATERMARK_ALGORITHMS.items():
		algo = algo_class()
		algorithms.append({
			"name": name,
			"description": algo.__doc__ or "No description available",
			"type": "logits" if hasattr(algo, "process_logits") else "semantic",
			"params": {
				# 这里可以添加算法支持的参数说明
				# 例如DIP的projection_dim, threshold等
			}
		})
	return algorithms


@router.post("/embed", response_model=WatermarkResponse)
async def embed_watermark(
		request: WatermarkRequest,
		current_user: User = Depends(get_auth_user),
		db: Session = Depends(get_db)
) -> Any:
	"""
	嵌入水印
	"""
	try:
		# 获取水印算法实例
		watermark = get_watermark_algorithm(request.algorithm, **request.params)
		
		if hasattr(watermark, "process_logits"):
			# Logits级水印
			# 添加处理器并生成文本
			llm_service.clear_processors()
			llm_service.add_processor(watermark.get_processor(request.key))
			watermarked_text = await llm_service.generate(request.text)
			metadata = {"type": "logits"}
		else:
			# 语义级水印
			watermarked_text = watermark.embed(request.text, request.key)
			metadata = {"type": "semantic"}
		
		return {
			"watermarked_text": watermarked_text,
			"metadata": metadata
		}
	
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(e)
		)


@router.post("/detect", response_model=DetectionResponse)
async def detect_watermark(
		request: DetectionRequest,
		current_user: User = Depends(get_auth_user),
		db: Session = Depends(get_db)
) -> Any:
	"""
	检测水印
	"""
	try:
		# 获取水印算法实例
		watermark = get_watermark_algorithm(request.algorithm, **request.params)
		
		# 执行检测
		result = watermark.detect(request.text, request.key)
		
		return result
	
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(e)
		)


@router.post("/visualize")
async def visualize_watermark(
		request: DetectionRequest,
		current_user: User = Depends(get_auth_user),
		db: Session = Depends(get_db)
) -> Any:
	"""
	可视化水印检测结果
	"""
	try:
		# 获取水印算法实例
		watermark = get_watermark_algorithm(request.algorithm, **request.params)
		
		# 先执行检测
		detection_result = watermark.detect(request.text, request.key)
		
		# 生成可视化数据
		visualization_data = watermark.visualize(request.text, detection_result)
		
		return visualization_data
	
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(e)
		)
