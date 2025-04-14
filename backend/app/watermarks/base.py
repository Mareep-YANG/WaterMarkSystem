import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

import torch
from transformers import LogitsProcessor

from app.core.Configurable import configurable, ConfigField
from app.models.GenerationConfig import GenerationConfig
from app.models.llm import llm_service


@configurable
class WatermarkBase(ABC):
	"""水印算法基类"""
	max_length= ConfigField()
	min_length= ConfigField()
	temperature= ConfigField()
	top_p= ConfigField()
	top_k= ConfigField()
	do_sample= ConfigField()
	num_beams= ConfigField()
	num_return_sequences= ConfigField()
	repetition_penalty= ConfigField()
	length_penalty= ConfigField()
	no_repeat_ngram_size= ConfigField()
	def __init__(self, max_length:int = None, min_length:int = None, temperature:float = 1.0,
				 top_p:float = 1.0, top_k:int = 50, do_sample:bool = True, num_beams:int = 1,
				 num_return_sequences:int = 1, repetition_penalty:float = 1.0,
				 length_penalty:float = 1.0, no_repeat_ngram_size:int = 0):
		"""
		初始化水印算法
		"""
		self.max_length = max_length
		self.min_length = min_length
		self.temperature = temperature
		self.top_p = top_p
		self.top_k = top_k
		self.do_sample = do_sample
		self.num_beams = num_beams
		self.num_return_sequences = num_return_sequences
		self.repetition_penalty = repetition_penalty
		self.length_penalty = length_penalty
		self.no_repeat_ngram_size = no_repeat_ngram_size
		self.generation_config = GenerationConfig(
			max_length=self.max_length,
			min_length=self.min_length,
			temperature=self.temperature,
			top_p=self.top_p,
			top_k=self.top_k,
			do_sample=self.do_sample,
			num_beams=self.num_beams,
			num_return_sequences=self.num_return_sequences,
			repetition_penalty=self.repetition_penalty,
			length_penalty=self.length_penalty,
			no_repeat_ngram_size=self.no_repeat_ngram_size,
			logits_processor=llm_service.processors,
		)

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
	def visualize(self, text: str) -> Dict[str, Any]:
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
