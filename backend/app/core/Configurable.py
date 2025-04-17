import json
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, get_type_hints
import inspect

T = TypeVar('T')


class ConfigurableMixin:
    """可配置对象的基础Mixin类"""

    @classmethod
    def get_config_fields(cls) -> List[str]:
        """获取需要包含在配置中的字段"""
        # 默认情况下，使用所有非私有属性
        return [attr for attr in dir(cls) if not attr.startswith('_') and not callable(getattr(cls, attr))]

    def to_config(self) -> Dict[str, Any]:
        """将实例转换为配置字典"""
        config = {}
        for field in self.get_config_fields():
            if hasattr(self, field):
                value = getattr(self, field)
                config[field] = self._convert_value_to_config(value)
        return config

    def _convert_value_to_config(self, value: Any) -> Any:
        """将值转换为配置格式"""
        # 处理嵌套的可配置对象
        if isinstance(value, ConfigurableMixin):
            return value.to_config()
        # 处理Pydantic BaseModel
        elif hasattr(value, '__class__') and hasattr(value.__class__, 'model_dump'):
            # 这是Pydantic的BaseModel
            return value.model_dump()
        # 处理列表中的可配置对象或BaseModel
        elif isinstance(value, list):
            return [
                self._convert_value_to_config(item) for item in value
            ]
        # 处理字典中的可配置对象或BaseModel
        elif isinstance(value, dict):
            return {
                k: self._convert_value_to_config(v) for k, v in value.items()
            }
        else:
            # 只包含可JSON序列化的值
            try:
                json.dumps(value)
                return value
            except (TypeError, OverflowError):
                # 不可序列化的值，转为字符串或忽略
                return str(value)


# 装饰器，用于标记可配置的类
def configurable(cls):
    """标记一个类为可配置的"""
    # 如果类还没有继承ConfigurableMixin，添加它
    if ConfigurableMixin not in cls.__bases__:
        cls = type(cls.__name__, (cls, ConfigurableMixin), {})
    return cls


# 可以使用配置字段注解来更精确地控制配置
class ConfigField:
    """用于标记配置字段的描述符"""

    def __init__(self, include_in_config=True, converter=None):
        self.include_in_config = include_in_config
        self.converter = converter
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name
        # 在私有属性中存储值
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name, None)

    def __set__(self, instance, value):
        if self.converter and callable(self.converter):
            value = self.converter(value)
        setattr(instance, self.private_name, value)




