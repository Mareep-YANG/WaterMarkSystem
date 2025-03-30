import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

import torch
from transformers import LogitsProcessor


class WatermarkBase(ABC):
	"""水印算法基类"""
	
	@abstractmethod
	def embed(self, prompt: Any) -> str:
		"""
		嵌入水印
		Args:
			prompt: 输入文本提示
			key: 水印密钥
		Returns:
			包含处理后的文本
		"""
		pass
	
	@abstractmethod
	def detect(self, text: str,  **kwargs) -> Dict[str, Any]:
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




class LogitsWatermark(WatermarkBase):
	"""Logits级水印基类"""

	@abstractmethod
	def get_processor(self, key: str) -> LogitsProcessor:
		"""
		获取对应的LogitsProcessor实现
		Args:
			key: 水印密钥
		Returns:
			LogitsProcessor实例
		"""


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
