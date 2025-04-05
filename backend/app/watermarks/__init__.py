from .base import LogitsWatermark, SemanticWatermark, WatermarkBase
from .dip import DIPWatermark
# 定义各算法的类型
WATERMARK_TYPES = {
    "dip": "logits",
    # "semstamp": "semantic",
}
# 注册可用的水印算法
WATERMARK_ALGORITHMS = {
	"dip": DIPWatermark,
	# "semstamp": SemStampWatermark,
}


def get_watermark_algorithm(name: str, **kwargs) -> WatermarkBase:
	"""
	获取水印算法实例
	Args:
		name: 算法名称
		**kwargs: 算法参数
	Returns:
		水印算法实例œ
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
	"get_watermark_algorithm",
	"WATERMARK_ALGORITHMS"
]
