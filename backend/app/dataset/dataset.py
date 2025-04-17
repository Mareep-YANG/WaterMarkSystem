import os
import uuid
from typing import Optional

from datasets import Dataset as HFDataset, load_dataset

from app.dbModels.dataset import Dataset


async def process_uploaded_dataset(file_path: str, dataset_id: uuid.UUID, format_type: str):
	"""处理上传的数据集文件"""
	try:
		# 获取数据集记录
		dataset = await Dataset.get(id=dataset_id)
		
		# 转换为HF Dataset格式
		if format_type == "auto":
			# 根据文件扩展名自动检测格式
			file_ext = os.path.splitext(file_path)[1].lower()
			if file_ext == ".csv":
				hf_dataset = HFDataset.from_csv(file_path)
			elif file_ext == ".json":
				hf_dataset = HFDataset.from_json(file_path)
			elif file_ext in [".txt", ".text"]:
				with open(file_path, "r") as f:
					texts = [line.strip() for line in f]
				hf_dataset = HFDataset.from_dict({"text": texts})
			else:
				raise ValueError(f"Unsupported file extension: {file_ext}")
		elif format_type == "csv":
			hf_dataset = HFDataset.from_csv(file_path)
		elif format_type == "json":
			hf_dataset = HFDataset.from_json(file_path)
		elif format_type == "text":
			with open(file_path, "r") as f:
				texts = [line.strip() for line in f]
			hf_dataset = HFDataset.from_dict({"text": texts})
		else:
			raise ValueError(f"Unsupported format: {format_type}")
		
		# 创建存储目录
		os.makedirs(dataset.storage_path, exist_ok=True)
		
		# 保存到磁盘
		hf_dataset.save_to_disk(dataset.storage_path)
		
		# 更新数据集信息
		features = {k: str(v) for k, v in hf_dataset.features.items()}
		await dataset.update_from_dict(
			{
				"features": features,
				"num_rows": len(hf_dataset),
				"status": "completed"
			}
		)
		await dataset.save()
	
	except Exception as e:
		# 更新状态为失败
		if dataset:
			await dataset.update_from_dict(
				{
					"status": "failed"
				}
			)
			await dataset.save()
		
		# 记录错误
		print(f"Error processing dataset {dataset_id}: {str(e)}")
	
	finally:
		# 清理临时文件
		if os.path.exists(file_path):
			os.remove(file_path)


async def import_hf_dataset(
	dataset_id: uuid.UUID, dataset_name: str, subset: Optional[str], split: Optional[str]
):
	"""从Hugging Face Hub导入数据集"""
	try:
		# 获取数据集记录
		dataset = await Dataset.get(id=dataset_id)
		
		# 从Hugging Face导入
		try:
			if subset:
				hf_dataset = load_dataset(dataset_name, subset, split=split)
			else:
				hf_dataset = load_dataset(dataset_name, split=split)
		except Exception as e:
			raise ValueError(f"Error loading dataset from HF Hub: {str(e)}")
		
		# 处理DatasetDict情况
		if not isinstance(hf_dataset, HFDataset):
			# 如果是DatasetDict，保存所有split信息
			splits_info = {k: len(v) for k, v in hf_dataset.items()}
			
			# 为简单起见，我们可以选择第一个split或合并所有split
			# 这里选择第一个split
			first_split = next(iter(hf_dataset.keys()))
			hf_dataset = hf_dataset[first_split]
			
			await dataset.update_from_dict(
				{
					"splits": splits_info
				}
			)
		
		# 创建存储目录
		os.makedirs(dataset.storage_path, exist_ok=True)
		
		# 保存到磁盘
		hf_dataset.save_to_disk(dataset.storage_path)
		
		# 更新数据集信息
		features = {k: str(v) for k, v in hf_dataset.features.items()}
		await dataset.update_from_dict(
			{
				"features": features,
				"num_rows": len(hf_dataset),
				"status": "completed"
			}
		)
		await dataset.save()
	
	except Exception as e:
		# 更新状态为失败
		if dataset:
			await dataset.update_from_dict(
				{
					"status": "failed"
				}
			)
			await dataset.save()
		
		# 记录错误
		print(f"Error importing dataset {dataset_id}: {str(e)}")
