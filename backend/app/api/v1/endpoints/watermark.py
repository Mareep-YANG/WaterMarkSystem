import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..deps import get_auth_user
from ....models.llm import llm_service
from ....dbModels.user import User
from ....watermarks import get_watermark_algorithm, WATERMARK_ALGORITHMS, LogitsWatermark

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


@router.get("/algorithms", response_model=List[AlgorithmInfo])
async def list_algorithms() -> Any:
	"""
	获取所有支持的水印算法
	"""
	# 水印列表
	algorithms = []
	for name, algo_class in WATERMARK_ALGORITHMS.items(): # 遍历水印包获取水印算法
		algo = algo_class()
		algorithms.append(
			{
				"name": name,
				"description": algo.__doc__ or "No description available",
				"type": "logits" if hasattr(algo,"get_processor") else "semantic",
				"params": {
					# 这里可以添加算法支持的参数说明
					# 例如DIP的projection_dim, threshold等
					#TODO: 每个水印的参数系统，和可能的自动调参功能
				}
			}
		)
	return algorithms


@router.post("/embed", response_model=WatermarkResponse)
async def embed_watermark(
	request: WatermarkRequest,
) -> Any:
	"""
	嵌入水印
	"""
	try:
		# 获取水印算法实例
		watermark = get_watermark_algorithm(request.algorithm, **request.params) # 传入水印名和参数，获取水印算法实例
		
		if isinstance(watermark, LogitsWatermark):
			# Logits级水印
			# 添加处理器并生成文本
			logging.debug("LogitsWatermark embeding")
			watermarked_text = watermark.embed(request.text)
			metadata = {"type": "logits"}
		else:
			# 语义级水印
			watermarked_text = ""
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
) -> Any:
	"""
	检测水印
	"""
	try:
		# 获取水印算法实例
		watermark = get_watermark_algorithm(request.algorithm, **request.params)
		
		# 执行检测
		result = watermark.detect(request.text)
		
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
		visualization_data = watermark.visualize(request.text, detection_result.get("details"))
		
		return visualization_data
	
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail=str(e)
		)
