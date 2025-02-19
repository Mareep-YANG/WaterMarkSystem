# 文本水印系统技术设计

## 1. 核心模块设计

### 1.1 LLM服务
```python
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    LogitsProcessor,
    LogitsProcessorList
)
import torch

class LLMService:
    """LLM服务核心类"""
    
    def __init__(self, model_name: str, device: str = "cuda"):
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.processors = LogitsProcessorList()
        self.device = device

    def add_processor(self, processor: LogitsProcessor):
        """添加logits处理器"""
        self.processors.append(processor)

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            logits_processor=self.processors,
            **kwargs
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    async def get_logits(self, text: str) -> torch.Tensor:
        """获取文本的logits分布"""
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.logits
```

## 2. 水印算法设计

### 2.1 基础接口
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import torch

class WatermarkBase(ABC):
    """水印算法基类"""
    
    @abstractmethod
    def embed(self, text_or_logits: Any, key: str, **kwargs) -> Any:
        """嵌入水印"""
        pass
    
    @abstractmethod
    def detect(self, text: str, key: str, **kwargs) -> Dict[str, Any]:
        """检测水印"""
        pass
    
    @abstractmethod
    def visualize(self, text: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """可视化检测结果"""
        pass

    def get_processor(self, key: str) -> LogitsProcessor:
        """获取对应的LogitsProcessor"""
        return WatermarkLogitsProcessor(self, key)
```

### 2.2 LogitsProcessor实现
```python
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
        """处理token logits"""
        return self.watermark.process_logits(scores, input_ids, self.key)
```

### 2.3 具体算法实现示例

#### 2.3.1 DIP (Dynamic Identity Projection)
```python
class DIPWatermark(WatermarkBase):
    """DIP水印算法实现"""
    
    def __init__(self, projection_dim: int = 128, threshold: float = 0.5):
        self.projection_dim = projection_dim
        self.threshold = threshold
        
    def process_logits(
        self,
        scores: torch.FloatTensor,
        input_ids: torch.LongTensor,
        key: str
    ) -> torch.FloatTensor:
        """处理logits实现水印嵌入"""
        # 实现DIP算法的logits处理逻辑
        return scores  # 处理后的logits

    def detect(
        self,
        text: str,
        key: str,
        **kwargs
    ) -> Dict[str, Any]:
        """检测水印"""
        # 实现DIP算法的水印检测逻辑
        return {
            "detected": True,
            "confidence": 0.95,
            "details": {}
        }
```

#### 2.3.2 SemStamp (Semantic Stamping)
```python
class SemStampWatermark(WatermarkBase):
    """语义水印算法实现"""
    
    def process_logits(
        self,
        scores: torch.FloatTensor,
        input_ids: torch.LongTensor,
        key: str
    ) -> torch.FloatTensor:
        """处理logits实现语义水印"""
        # 实现语义水印的logits处理逻辑
        return scores

    def detect(
        self,
        text: str,
        key: str,
        **kwargs
    ) -> Dict[str, Any]:
        """检测语义水印"""
        # 实现语义水印的检测逻辑
        return {
            "detected": True,
            "confidence": 0.90,
            "semantic_markers": []
        }
```

## 3. 评估模块设计

### 3.1 评估指标
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class EvaluationMetric(ABC):
    """评估指标基类"""
    
    @abstractmethod
    def calculate(self, original_text: str, watermarked_text: str) -> float:
        """计算评估指标"""
        pass

class RobustnessMetric(EvaluationMetric):
    """鲁棒性评估"""
    
    def calculate(self, original_text: str, watermarked_text: str) -> float:
        # 实现鲁棒性评估逻辑
        pass

class QualityMetric(EvaluationMetric):
    """文本质量评估"""
    
    def calculate(self, original_text: str, watermarked_text: str) -> float:
        # 实现文本质量评估逻辑
        pass
```

### 3.2 攻击方法
```python
class WatermarkAttack(ABC):
    """水印攻击基类"""
    
    @abstractmethod
    def attack(self, text: str, **kwargs) -> str:
        """执行攻击"""
        pass

class TextAttack(WatermarkAttack):
    """文本层面攻击"""
    
    def attack(self, text: str, **kwargs) -> str:
        # 实现文本攻击逻辑
        pass

class LogitsAttack(WatermarkAttack):
    """Logits层面攻击"""
    
    def attack(self, text: str, **kwargs) -> str:
        # 实现logits攻击逻辑
        pass
```

## 4. API接口设计

### 4.1 水印相关接口
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class WatermarkRequest(BaseModel):
    text: str
    algorithm: str
    key: str
    params: Dict[str, Any] = {}

class WatermarkResponse(BaseModel):
    watermarked_text: str
    metadata: Dict[str, Any]

@app.post("/api/watermark/embed")
async def embed_watermark(request: WatermarkRequest):
    """嵌入水印"""
    try:
        watermark = get_watermark_algorithm(request.algorithm)
        result = await watermark.embed(request.text, request.key, **request.params)
        return WatermarkResponse(
            watermarked_text=result["text"],
            metadata=result["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/watermark/detect")
async def detect_watermark(request: WatermarkRequest):
    """检测水印"""
    try:
        watermark = get_watermark_algorithm(request.algorithm)
        result = await watermark.detect(request.text, request.key)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## 5. 安全性考虑

### 5.1 密钥管理
- 使用安全的密钥生成机制
- 密钥加密存储
- 定期密钥轮换

### 5.2 API安全
- 请求限流
- 输入验证和清洗
- 错误处理和日志记录

### 5.3 模型安全
- 模型访问控制
- 推理结果过滤
- 防止模型滥用

## 6. 性能优化

### 6.1 模型优化
- 模型量化
- 批处理优化
- 缓存管理

### 6.2 并发处理
- 异步处理
- 队列管理
- 资源限制