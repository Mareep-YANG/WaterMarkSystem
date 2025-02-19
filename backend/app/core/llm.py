from typing import List, Optional
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    LogitsProcessor,
    LogitsProcessorList,
)
from app.core.config import settings

class LLMService:
    """LLM服务核心类"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = None
            self.tokenizer = None
            self.processors = LogitsProcessorList()
            self.initialized = True

    def load_model(self, model_name: Optional[str] = None):
        """加载模型"""
        model_name = model_name or settings.DEFAULT_MODEL_PATH
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=settings.MODEL_CACHE_DIR
        ).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=settings.MODEL_CACHE_DIR
        )
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

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        generation_config = {
            "max_length": max_length,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": True,
            "logits_processor": self.processors if self.processors else None,
            **kwargs
        }

        outputs = self.model.generate(**inputs, **generation_config)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    async def get_logits(self, text: str) -> torch.Tensor:
        """获取文本的logits分布"""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.logits

# 全局LLM服务实例
llm_service = LLMService()