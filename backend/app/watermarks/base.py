import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

import torch
from transformers import LogitsProcessor


class WatermarkBase(ABC):
	"""水印算法基类"""
	
	@abstractmethod
	def embed(self, logits: Any, key: str,input_ids: Any) -> Any:
		"""
		嵌入水印
		Args:
			logits: 文本或logits
			key: 水印密钥
			input_ids: token
		Returns:
			包含处理后的logits
		"""
		pass
	
	@abstractmethod
	def detect(self, text: str, key: str, **kwargs) -> Dict[str, Any]:
		"""
		检测水印,模型和分词器从从llmservice
		Args:
			text: 待检测文本
			key: 水印密钥
			**kwargs: 其他参数
		Returns:
			检测结果，包含是否检测到水印、置信度等信息
		"""
		pass
	
	@abstractmethod
	def visualize(self, text: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
		"""
		可视化检测结果
		Args:
			text: 原始文本
			detection_result: 检测结果
		Returns:
			可视化数据
		"""
		pass


class WatermarkLogitsProcessor(LogitsProcessor):
	"""水印处理器基类"""
	
	def __init__(self, watermark: WatermarkBase, key: str):
		self.watermark = watermark
		self.key = key
	
	def __call__(
		self,
		input_ids: torch.LongTensor,
		scores: torch.FloatTensor
	) -> torch.FloatTensor:
		"""
		处理token logits
		Args:
			input_ids: 输入token IDs
			scores: token的logits分数
			**kwargs: 其他参数
		Returns:
			处理后的logits分数
		"""
		return self.watermark.embed(
			scores, self.key,
			input_ids=input_ids,
		)


class LogitsWatermark(WatermarkBase):
	"""Logits级水印基类"""

	@abstractmethod
	def get_processor(self, key: str) -> 'WatermarkLogitsProcessor':
		"""
		获取对应的LogitsProcessor实现
		Args:
			key: 水印密钥
		Returns:
			LogitsProcessor实例
		"""
		return WatermarkLogitsProcessor(self, key)


class SemanticWatermark(WatermarkBase):
	"""语义级水印基类"""
	
	@abstractmethod
	def process_text(self, text: str, key: str, **kwargs) -> str:
		"""
		处理文本实现水印
		Args:
			text: 原始文本
			key: 水印密钥
			**kwargs: 其他参数
		Returns:
			处理后的文本
		"""
		pass
