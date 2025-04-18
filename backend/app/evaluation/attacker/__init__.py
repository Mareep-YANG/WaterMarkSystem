from .LLMParaphraserAttacker import LLMParaphraserAttacker
from .SynonymSubstitutionAttacker import SynonymSubstitutionAttacker
from .TextWatermarkAttacker import TextWatermarkAttacker
from .WordDeletionAttacker import WordDeletionAttacker

# 注册可用的攻击器
ATTACKERS = {
	"LLMParaphraserAttacker": LLMParaphraserAttacker,
	"WordDeletionAttacker": WordDeletionAttacker,
	"SynonymSubstitutionAttacker": SynonymSubstitutionAttacker
}


def get_attacker(name: str, **kwargs) -> TextWatermarkAttacker:
	"""
	获取攻击器实例
	Args:
		name: 攻击器名称
		**kwargs: 攻击器参数
	Returns:
		攻击器实例
	Raises:
		ValueError: 如果攻击器不存在
	"""
	if name not in ATTACKERS:
		raise ValueError(f"Unknown attacker: {name}")
	return ATTACKERS[name](**kwargs)


__all__ = [
	"LLMParaphraserAttacker",
	"TextWatermarkAttacker",
	"WordDeletionAttacker",
	"SynonymSubstitutionAttacker",
	"ATTACKERS",
	"get_attacker"
]
