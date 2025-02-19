from typing import Any, Dict, List
import torch
from transformers import AutoTokenizer, AutoModel
from .base import SemanticWatermark
import numpy as np
from hashlib import sha256

class SemStampWatermark(SemanticWatermark):
    """语义级水印SemStamp实现"""
    
    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        threshold: float = 0.8,
        min_chunk_length: int = 50
    ):
        self.threshold = threshold
        self.min_chunk_length = min_chunk_length
        
        # 加载语义编码模型
        self.tokenizer = AutoTokenizer.from_pretrained(embedding_model)
        self.model = AutoModel.from_pretrained(embedding_model)
        
        if torch.cuda.is_available():
            self.model = self.model.cuda()

    def _get_embeddings(self, text: str) -> torch.Tensor:
        """
        获取文本的语义嵌入
        """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # 使用[CLS]token的最后一层隐藏状态作为文本表示
            embeddings = outputs.last_hidden_state[:, 0, :]
        
        return embeddings

    def _chunk_text(self, text: str) -> List[str]:
        """
        将文本分块
        """
        # 简单的按句子分块，实际应用中可能需要更复杂的分块策略
        sentences = text.split('.')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < self.min_chunk_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def _generate_watermark_embedding(self, key: str, dim: int) -> torch.Tensor:
        """
        生成水印嵌入向量
        """
        seed = int(sha256(key.encode()).hexdigest(), 16) % (2**32)
        rng = np.random.RandomState(seed)
        watermark = torch.FloatTensor(rng.randn(dim))
        return watermark / torch.norm(watermark)

    def process_text(self, text: str, key: str, **kwargs) -> str:
        """
        处理文本实现语义水印，通过调整文本内容使其语义表示接近目标水印
        """
        # 在实际应用中，这里需要实现文本改写逻辑
        # 当前版本仅返回原文本，表示该方法需要在具体应用中实现
        return text

    def embed(self, text_or_logits: Any, key: str, **kwargs) -> Any:
        """
        嵌入水印
        """
        if isinstance(text_or_logits, str):
            return self.process_text(text_or_logits, key, **kwargs)
        raise ValueError("SemStamp watermark only works with text")

    def detect(self, text: str, key: str, **kwargs) -> Dict[str, Any]:
        """
        检测水印
        """
        # 文本分块
        chunks = self._chunk_text(text)
        
        # 获取每个块的嵌入
        chunk_embeddings = []
        for chunk in chunks:
            embedding = self._get_embeddings(chunk)
            chunk_embeddings.append(embedding)
        
        # 生成水印嵌入
        watermark = self._generate_watermark_embedding(
            key, 
            chunk_embeddings[0].shape[-1]
        ).to(chunk_embeddings[0].device)
        
        # 计算相似度
        similarities = []
        for embedding in chunk_embeddings:
            similarity = torch.cosine_similarity(embedding, watermark.unsqueeze(0))
            similarities.append(float(similarity))
        
        # 判断是否检测到水印
        avg_similarity = np.mean(similarities)
        is_watermarked = avg_similarity > self.threshold
        
        return {
            "detected": bool(is_watermarked),
            "confidence": float(avg_similarity),
            "details": {
                "chunk_similarities": similarities,
                "chunks": chunks,
                "threshold": self.threshold
            }
        }

    def visualize(self, text: str, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        可视化检测结果
        """
        similarities = detection_result["details"]["chunk_similarities"]
        chunks = detection_result["details"]["chunks"]
        threshold = detection_result["details"]["threshold"]
        
        return {
            "type": "heatmap",
            "data": {
                "text_chunks": chunks,
                "similarities": similarities,
                "threshold": threshold
            },
            "annotations": [
                {
                    "chunk_index": i,
                    "similarity": sim,
                    "is_watermarked": sim > threshold
                }
                for i, sim in enumerate(similarities)
            ]
        }