from hashlib import sha256
from typing import Any, Dict

import numpy as np
import torch
import torch.nn.functional as F

from .base import LogitsWatermark


class DIPWatermark(LogitsWatermark):
    """Dynamic Identity Projection (DIP) 水印实现

    本实现基于动态身份投影原理，通过将token logits投影到低维空间，
    并向目标投影方向调整，在保留文本流畅性的同时嵌入可检测的水印。
    """

    def __init__(
            self,
            projection_dim: int = 128,
            threshold: float = 0.5,
            scale: float = 1.0,
            gamma: float = 0.25  # 控制投影强度的参数
    ):
        """
        初始化DIP水印

        Args:
            projection_dim: 投影空间维度
            threshold: 水印检测阈值
            scale: 水印强度缩放因子
            gamma: 控制投影绿区比例的参数
        """
        self.projection_dim = projection_dim
        self.threshold = threshold
        self.scale = scale
        self.gamma = gamma
        self.projection_cache = {}  # 缓存投影矩阵以提高性能

    def _get_projection_matrix(self, key: str, vocab_size: int) -> torch.Tensor:
        """
        生成投影矩阵

        Args:
            key: 水印密钥
            vocab_size: 词表大小

        Returns:
            投影矩阵
        """
        # 使用缓存避免重复计算
        cache_key = f"{key}_{vocab_size}_{self.projection_dim}"
        if cache_key in self.projection_cache:
            return self.projection_cache[cache_key]

        # 使用密钥生成随机种子
        seed = int(sha256(key.encode()).hexdigest(), 16) % (2 ** 32)
        rng = np.random.RandomState(seed)

        # 生成随机投影矩阵并正规化
        matrix = rng.randn(vocab_size, self.projection_dim)
        matrix = matrix / np.sqrt(np.sum(matrix ** 2, axis=1, keepdims=True))

        # 转换为torch tensor并缓存
        result = torch.FloatTensor(matrix)
        self.projection_cache[cache_key] = result
        return result

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
        batch_size, vocab_size = logits.shape[0], logits.shape[-1]
        device = logits.device

        # 从输入ID生成上下文相关密钥
        context_key = key
        if input_ids is not None and input_ids.size(0) > 0:
            # 使用最后几个token作为上下文
            context_suffix = "_" + "_".join([str(t.item()) for t in input_ids[0, -5:]])
            context_key = key + context_suffix

        # 生成投影矩阵并移至相应设备
        proj_matrix = self._get_projection_matrix(context_key, vocab_size).to(device)

        # 对logits进行softmax并投影
        probs = F.softmax(logits, dim=-1)
        projected = torch.matmul(probs, proj_matrix)

        # 生成目标投影向量
        target_key = context_key + "_target"
        target_proj = self._get_projection_matrix(target_key, self.projection_dim).to(device)

        # 计算每个词表位置的投影距离
        token_directions = torch.matmul(proj_matrix, target_proj.T)  # [vocab_size, projection_dim]

        # 根据投影距离调整logits
        # 将距离转换为连续的加权因子
        similarity_scores = F.normalize(token_directions, dim=1)

        # 按照相似度划分绿区和红区
        sorted_indices = torch.argsort(similarity_scores, dim=1, descending=True)
        green_zone_size = int(vocab_size * self.gamma)

        # 创建调整矩阵
        adjustments = torch.zeros_like(logits)
        for i in range(batch_size):
            # 提高绿区token的概率
            green_indices = sorted_indices[i, :green_zone_size]
            adjustments[i, green_indices] = self.scale

        # 应用调整
        modified_logits = logits + adjustments
        return modified_logits

    def embed(self, logits: Any, key: str, input_ids: Any) -> Any:
        """
        嵌入水印

        Args:
            logits: 原始logits
            key: 水印密钥
            input_ids: 输入token IDs

        Returns:
            处理后的logits
        """
        return self.process_logits(logits, input_ids, key)

    def detect(self, text: str, key: str, tokenizer=None, model=None, **kwargs) -> Dict[str, Any]:
        """
        检测水印

        Args:
            text: 待检测文本
            key: 水印密钥
            tokenizer: 用于将文本转换为tokens的分词器
            model: 用于获取logits的模型

        Returns:
            检测结果
        """
        if not tokenizer or not model:
            raise ValueError("检测水印需要提供tokenizer和model")

        # 将文本转换为tokens
        tokens = tokenizer(text, return_tensors="pt").to(model.device)
        input_ids = tokens.input_ids

        # 获取模型输出的logits
        with torch.no_grad():
            outputs = model(**tokens)
            logits = outputs.logits[:, :-1, :]  # 排除最后一个位置的logits
            actual_input_ids = input_ids[:, 1:]  # 排除第一个token

        batch_size, seq_len, vocab_size = logits.shape
        device = logits.device

        # 统计绿区token的比例
        green_tokens = 0
        total_tokens = seq_len
        similarity_scores = []

        for i in range(seq_len):
            # 为每个位置生成上下文相关密钥
            if i < 5:
                context_tokens = actual_input_ids[0, :i + 1]
            else:
                context_tokens = actual_input_ids[0, i - 4:i + 1]

            context_key = key + "_" + "_".join([str(t.item()) for t in context_tokens])

            # 获取该位置的logits和实际token
            pos_logits = logits[0, i]
            pos_token = actual_input_ids[0, i].item()

            # 计算投影矩阵
            proj_matrix = self._get_projection_matrix(context_key, vocab_size).to(device)

            # 计算目标投影
            target_key = context_key + "_target"
            target_proj = self._get_projection_matrix(target_key, self.projection_dim).to(device)

            # 计算每个token的方向与目标的相似度
            token_directions = torch.matmul(proj_matrix, target_proj.T)

            # 标准化并获取排序
            similarity = F.normalize(token_directions, dim=1)
            sorted_indices = torch.argsort(similarity, dim=0, descending=True)

            # 检查实际token是否在绿区内
            green_zone_size = int(vocab_size * self.gamma)
            green_tokens_indices = sorted_indices[:green_zone_size].squeeze(-1)

            is_green = pos_token in green_tokens_indices
            if is_green:
                green_tokens += 1

            # 记录相似度得分
            token_score = float(similarity[pos_token])
            similarity_scores.append(token_score)

        # 计算z-score
        expected_green = self.gamma * total_tokens
        variance = total_tokens * self.gamma * (1 - self.gamma)
        z_score = (green_tokens - expected_green) / (np.sqrt(variance) + 1e-10)

        # 判断是否检测到水印
        is_watermarked = z_score > self.threshold

        return {
            "detected": bool(is_watermarked),
            "confidence": float(z_score),
            "details": {
                "green_tokens": green_tokens,
                "total_tokens": total_tokens,
                "green_ratio": green_tokens / total_tokens,
                "expected_ratio": self.gamma,
                "z_score": float(z_score),
                "similarity_scores": similarity_scores,
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
        z_score = detection_result["details"]["z_score"]

        # 为每个token分配颜色
        tokenized_text = []
        if "tokenizer" in detection_result:
            tokenizer = detection_result["tokenizer"]
            tokens = tokenizer.tokenize(text)
            tokenized_text = tokens[:len(similarity_scores)]  # 确保长度匹配

        # 构建可视化数据
        return {
            "type": "combined",
            "charts": [
                {
                    "type": "line_chart",
                    "data": {
                        "labels": list(range(len(similarity_scores))),
                        "datasets": [
                            {
                                "label": "相似度得分",
                                "data": similarity_scores,
                                "borderColor": "rgba(75, 192, 192, 1)",
                            },
                            {
                                "label": "阈值",
                                "data": [threshold] * len(similarity_scores),
                                "borderColor": "rgba(255, 99, 132, 1)",
                                "borderDash": [5, 5]
                            }
                        ]
                    }
                },
                {
                    "type": "text_highlight",
                    "data": {
                        "text": text,
                        "tokens": tokenized_text,
                        "highlights": similarity_scores,
                        "threshold": self.gamma,  # 使用gamma作为高亮阈值
                        "colors": {
                            "high": "rgba(75, 192, 192, 0.5)",  # 绿色
                            "low": "rgba(255, 255, 255, 0)"  # 透明
                        }
                    }
                },
                {
                    "type": "summary",
                    "data": {
                        "z_score": z_score,
                        "threshold": threshold,
                        "detected": detection_result["detected"],
                        "confidence": detection_result["confidence"]
                    }
                }
            ]
        }
