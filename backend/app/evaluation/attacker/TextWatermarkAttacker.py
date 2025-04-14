from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple

from app.core.Configurable import configurable


@configurable
class TextWatermarkAttacker(ABC):
    """
    大模型水印文本攻击处理器基类

    用于对含有水印的LLM生成文本进行攻击，
    尝试在保持语义和可读性的前提下移除或降低水印的可检测性。
    """

    @abstractmethod
    def attack(self, text: str, **kwargs) -> str:
        """
        对文本进行水印攻击处理

        Args:
            text: 输入的带水印文本
            **kwargs: 额外参数

        Returns:
            处理后的文本
        """
        pass

    def batch_attack(self, texts: List[str], **kwargs) -> List[str]:
        """
        批量处理文本

        Args:
            texts: 输入文本列表
            **kwargs: 额外参数

        Returns:
            处理后的文本列表
        """
        return [self.attack(text, **kwargs) for text in texts]


    def get_config(self) -> Dict[str, Any]:
        """返回当前配置"""
        return self.config

    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置参数"""
        self.config.update(config)
