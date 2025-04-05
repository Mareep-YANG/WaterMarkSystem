from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Dataset(models.Model):
	id = fields.UUIDField(pk=True)
	name = fields.CharField(max_length=255, null=False)
	description = fields.TextField(null=True)
	created_at = fields.DatetimeField(auto_now_add=True)
	updated_at = fields.DatetimeField(auto_now=True)
	source = fields.CharField(max_length=50)  # "uploaded", "huggingface_hub"
	hf_dataset_name = fields.CharField(max_length=255, null=True)
	subset = fields.CharField(max_length=100, null=True)
	features = fields.JSONField(default=dict)  # 特征结构
	num_rows = fields.IntField(default=0)
	splits = fields.JSONField(default=dict)  # 包含的splits信息
	storage_path = fields.CharField(max_length=500, null=True)
	status = fields.CharField(
		max_length=20, default="pending"
	)  # pending, processing, completed, failed
	
	class Meta:
		table = "datasets"


DatasetPydantic = pydantic_model_creator(Dataset, name="Dataset")
DatasetInPydantic = pydantic_model_creator(
	Dataset, name="DatasetIn", exclude_readonly=True
)
