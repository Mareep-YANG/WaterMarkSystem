from typing import Any, Dict
import torch
import numpy as np
from .base import LogitsWatermark
from hashlib import sha256

class DIPWatermark(LogitsWatermark):
    """Dynamic Identity Projection (DIP) 水印实现"""
    
    def __init__(
        self,
        projection_dim: int = 128,
        threshold: float = 0.5,
        scale: float = 1.0
    ):
        self.projection_dim = projection_dim
        self.threshold = threshold
        self.scale = scale

    def _get_projection_matrix(self, key: str, vocab_size: int) -> torch.Tensor:
        """
        生成投影矩阵
        Args:
            key: 水印密钥
            vocab_size: 词表大小
        Returns:
            投影矩阵
        """
        # 使用密钥生成随机种子
        seed = int(sha256(key.encode()).hexdigest(), 16) % (2**32)
        rng = np.random.RandomState(seed)
        
        # 生成随机投影矩阵
        matrix = rng.randn(vocab_size, self.projection_dim)
        matrix = matrix / np.sqrt(np.sum(matrix**2, axis=1, keepdims=True))
        return torch.FloatTensor(matrix)

    def process_logits(
        self,
        logits: torch.FloatTensor,
        input_ids: torch.LongTensor,
        key: str,
        **kwargs
    ) -> torch.FloatTensor:
        """
        处理logits实现水印
        Args:
            logits: 原始logits [batch_size, seq_len, vocab_size]
            input_ids: 输入token IDs
            key: 水印密钥
        Returns:
            处理后的logits
        """
        batch_size, seq_len, vocab_size = logits.shape
        device = logits.device
        
        # 生成投影矩阵并移至相应设备
        proj_matrix = self._get_projection_matrix(key, vocab_size).to(device)
        
        # 对logits进行投影
        projected = torch.matmul(torch.softmax(logits, dim=-1), proj_matrix)
        
        # 生成目标投影
        target = self._get_projection_matrix(key + "_target", vocab_size).to(device)
        target = torch.matmul(torch.eye(vocab_size).to(device), target)
        
        # 计算调整量
        adjustments = torch.matmul(target - projected, proj_matrix.T)
        
        # 应用调整
        modified_logits = logits + self.scale * adjustments
        return modified_logits

    def embed(self, text_or_logits: Any, key: str, **kwargs) -> Any:
        """
        嵌入水印
        Args:
            text_or_logits: 如果是tensor则直接处理，否则视为文本
            key: 水印密钥
        Returns:
            处理后的logits或文本
        """
        if isinstance(text_or_logits, torch.Tensor):
            return self.process_logits(text_or_logits, kwargs.get('input_ids'), key)
        raise ValueError("DIP watermark only works with logits")

    def detect(self, text: str, key: str, **kwargs) -> Dict[str, Any]:
        """
        检测水印
        Args:
            text: 待检测文本
            key: 水印密钥
        Returns:
            检测结果
        """
        from ..core.llm import llm_service
        
        # 获取文本的logits分布
        logits = llm_service.get_logits(text)
        
        # 计算投影
        proj_matrix = self._get_projection_matrix(key, logits.shape[-1])
        projected = torch.matmul(torch.softmax(logits, dim=-1), proj_matrix)
        
        # 计算与目标投影的相似度
        target = self._get_projection_matrix(key + "_target", logits.shape[-1])
        target = torch.matmul(torch.eye(logits.shape[-1]), target)
        
        similarity = torch.cosine_similarity(projected, target)
        is_watermarked = torch.mean(similarity) > self.threshold
        
        return {
            "detected": bool(is_watermarked),
            "confidence": float(torch.mean(similarity)),
            "details": {
                "similarity_scores": similarity.tolist(),
                "threshold": self.threshold
            }
        }

    def visualize(self, text: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        可视化检测结果
        Args:
            text: 原始文本
            detection_result: 检测结果
        Returns:
            可视化数据
        """
        similarity_scores = detection_result["details"]["similarity_scores"]
        threshold = detection_result["details"]["threshold"]
        
        return {
            "type": "line_chart",
            "data": {
                "labels": list(range(len(similarity_scores))),
                "datasets": [
                    {
                        "label": "Similarity Scores",
                        "data": similarity_scores,
                    },
                    {
                        "label": "Threshold",
                        "data": [threshold] * len(similarity_scores),
                        "borderDash": [5, 5]
                    }
                ]
            }
        }