from typing import Optional

import torch
from transformers import (
	AutoModelForCausalLM,
	AutoTokenizer,
	LogitsProcessor,
	LogitsProcessorList,
)
from fastapi.concurrency import run_in_threadpool

from app.core.config import cfg


class LLMService:
	"""LLM服务核心类"""
	_instance = None
	
	def __new__(cls):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
		return cls._instance
	
	def __init__(self):
		if not hasattr(self, 'initialized'):
			self.model = None
			self.tokenizer = None
			self.processors = LogitsProcessorList()
			self.initialized = True
			self.is_active = False  # 添加is_active属性，默认为False
			# 获取可用设备
			if torch.cuda.is_available():
				self.device = "cuda"
			#		elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
			#			self.device = "mps" 某些算法的计算过程不允许使用MPS
			else:
				self.device = "cpu"
	
	def get_model(self):
		"""返回现在模型信息"""
		if not self.model or not self.tokenizer:
			return {
				"status": "not_loaded",
				"message": "模型尚未加载",
				"is_active": False
			}
		
		model_info = {
			"status": "loaded",
			"vocab_size": len(self.tokenizer),  # 获取词汇表大小
			"model_type": self.model.config.model_type if hasattr(
				self.model.config, 'model_type'
			) else "unknown",
			"device": self.device,
			"model_name": self.model.config.name_or_path if hasattr(
				self.model.config, 'name_or_path'
			) else "unknown",
			"is_active": self.is_active
		}
		
		return model_info
	
	async def load_model(self, model_name: Optional[str] = None):
		"""加载模型"""
		# 先清空当前模型
		if self.model is not None:
			# 确保模型从GPU内存中释放
			if self.device == "cuda":
				try:
					# 先将模型移至CPU
					self.model = self.model.to("cpu")
					# 清空CUDA缓存
					torch.cuda.empty_cache()
				except Exception as e:
					print(f"清空GPU内存时出错: {str(e)}")
		
		# 重置模型状态
		self.model = None
		self.tokenizer = None
		self.is_active = False
		
		# 加载新模型
		model_name = model_name or cfg.DEFAULT_MODEL
		
		try:
			# 使用run_in_threadpool异步加载模型
			self.model = await run_in_threadpool(
				AutoModelForCausalLM.from_pretrained,
				model_name,
				cache_dir=cfg.MODEL_CACHE_DIR
			)
			self.model = self.model.to(self.device)
			
			self.tokenizer = await run_in_threadpool(
				AutoTokenizer.from_pretrained,
				model_name,
				cache_dir=cfg.MODEL_CACHE_DIR
			)
			
			self.is_active = True  # 模型加载成功后设置is_active为True
		except Exception as e:
			# 加载失败时确保状态一致
			self.model = None
			self.tokenizer = None
			self.is_active = False
			raise e
			
		return self
	
	def add_processor(self, processor: LogitsProcessor):
		"""添加logits处理器"""
		self.processors.append(processor)
	
	def clear_processors(self):
		"""清空所有处理器"""
		self.processors = LogitsProcessorList()
	
	async def generate(
		self,
		prompt: str,
		max_length: int = 100,
		temperature: float = 0.7,
		top_p: float = 0.9,
		**kwargs
	) -> str:
		"""生成文本"""
		if not self.model or not self.tokenizer:
			raise RuntimeError("Model not loaded. Call load_model() first.")
		
		inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=True).to(
			self.device
		)
		
		generation_config = {
			"max_length": max_length,
			"temperature": temperature,
			"top_p": top_p,
			"do_sample": True,
			**kwargs
		}
		outputs = self.model.generate(**inputs, **generation_config)
		return self.tokenizer.decode(
			outputs[0],
			skip_special_tokens=True
		)


# 全局LLM服务实例
llm_service = LLMService()
