from .base import WatermarkBase, LogitsWatermark, SemanticWatermark
from .dip import DIPWatermark
from .semstamp import SemStampWatermark

# 注册可用的水印算法
WATERMARK_ALGORITHMS = {
    "dip": DIPWatermark,
    "semstamp": SemStampWatermark,
}

def get_watermark_algorithm(name: str, **kwargs) -> WatermarkBase:
    """
    获取水印算法实例
    Args:
        name: 算法名称
        **kwargs: 算法参数
    Returns:
        水印算法实例
    Raises:
        ValueError: 如果算法不存在
    """
    if name not in WATERMARK_ALGORITHMS:
        raise ValueError(f"Unknown watermark algorithm: {name}")
    return WATERMARK_ALGORITHMS[name](**kwargs)

__all__ = [
    "WatermarkBase",
    "LogitsWatermark",
    "SemanticWatermark",
    "DIPWatermark",
    "SemStampWatermark",
    "get_watermark_algorithm",
]