from tortoise import fields
from tortoise.models import Model


class HuggingfaceModel(Model):
    """Huggingface模型信息表"""
    id = fields.IntField(pk=True)
    model_name = fields.CharField(max_length=255, unique=True, description="模型名称")
    description = fields.TextField(null=True, description="模型描述")
    is_loaded = fields.BooleanField(default=False, description="模型是否已加载")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "huggingface_models"

    def __str__(self):
        return self.model_name
