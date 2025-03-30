from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any


class GenerationConfig(BaseModel):
    """用于 Transformers 文本生成的配置参数"""
    max_length: Optional[int] = Field(default=None, description="生成文本的最大长度")
    min_length: Optional[int] = Field(default=None, description="生成文本的最小长度")

    temperature: Optional[float] = Field(default=1.0, description="生成文本的温度参数，控制随机性，越高越随机")
    top_p: Optional[float] = Field(default=1.0, description="nucleus sampling的概率阈值")
    top_k: Optional[int] = Field(default=50, description="top-k sampling的k值")

    do_sample: bool = Field(default=True, description="是否使用采样，False时使用贪婪解码")
    num_beams: Optional[int] = Field(default=1, description="束搜索的束数")
    num_return_sequences: Optional[int] = Field(default=1, description="返回的生成序列数量")
    logits_processor: Any
    repetition_penalty: Optional[float] = Field(default=1.0, description="重复惩罚因子")
    length_penalty: Optional[float] = Field(default=1.0, description="长度惩罚因子")
    no_repeat_ngram_size: Optional[int] = Field(default=0, description="不允许重复的n-gram大小")

    extra_params: Dict[str, Any] = Field(default_factory=dict, description="额外的生成参数")
    @classmethod
    def check_positive_float(cls, v, info):
        if v is not None and v <= 0:
            param_name = info.field_name
            raise ValueError(f"{param_name} 必须大于 0")
        return v

    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典，用于传递给 transformers 模型"""
        # 获取所有非None字段
        base_dict = {k: v for k, v in self.model_dump().items()
                     if k != 'extra_params' and v is not None}

        # 合并额外参数
        return {**base_dict, **self.extra_params}

    def __call__(self, **kwargs) -> Dict[str, Any]:
        """允许通过函数调用方式更新参数并获取配置字典"""
        # 更新额外参数
        for k, v in kwargs.items():
            if hasattr(self, k) and k != 'extra_params':
                setattr(self, k, v)
            else:
                self.extra_params[k] = v

        return self.to_dict()
