import os
import uuid
from datetime import datetime
from typing import Optional

from datasets import Dataset as HFDataset
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from app.core import tasks
from app.dataset.dataset import import_hf_dataset, process_uploaded_dataset
from app.dbModels.dataset import Dataset, DatasetPydantic

router = APIRouter()


async def process_upload_dataset_task(task_id: str):
	with tasks.task_lock:
		task = tasks.tasks.get(task_id)
		if not task:
			return
		task["status"] = tasks.TaskStatus.PROCESSING
	
	try:
		request_data = task["request"]
		# 执行原有处理逻辑
		await process_uploaded_dataset(
			request_data["file_path"],
			uuid.UUID(request_data["dataset_id"]),
			request_data["format_type"]
		)
		
		# 更新数据集状态
		dataset = await Dataset.get(id=request_data["dataset_id"])
		dataset.status = "completed"
		await dataset.save()
		
		with tasks.task_lock:
			tasks.tasks[task_id].update(
				{
					"status": tasks.TaskStatus.COMPLETED,
					"result": {"message": "Dataset processed"},
					"completed_at": datetime.now()
				}
			)
	
	except Exception as e:
		error_msg = f"Dataset upload failed: {str(e)}"
		with tasks.task_lock:
			tasks.tasks[task_id].update(
				{
					"status": tasks.TaskStatus.FAILED,
					"error": error_msg,
					"completed_at": datetime.now()
				}
			)


async def process_import_from_hf_task(task_id: str):
	with tasks.task_lock:
		task = tasks.tasks.get(task_id)
		if not task:
			return
		task["status"] = tasks.TaskStatus.PROCESSING
	
	try:
		request_data = task["request"]
		# 执行原有导入逻辑
		await import_hf_dataset(
			uuid.UUID(request_data["dataset_id"]),
			request_data["dataset_name"],
			request_data["subset"],
			request_data["split"]
		)
		
		# 更新数据集状态
		dataset = await Dataset.get(id=request_data["dataset_id"])
		dataset.status = "completed"
		await dataset.save()
		
		with tasks.task_lock:
			tasks.tasks[task_id].update(
				{
					"status": tasks.TaskStatus.COMPLETED,
					"result": {"message": "HF dataset imported"},
					"completed_at": datetime.now()
				}
			)
	
	except Exception as e:
		error_msg = f"HF import failed: {str(e)}"
		with tasks.task_lock:
			tasks.tasks[task_id].update(
				{
					"status": tasks.TaskStatus.FAILED,
					"error": error_msg,
					"completed_at": datetime.now()
				}
			)


@router.post("/datasets/upload", response_model=tasks.TaskResponse)
async def upload_dataset(
	background_tasks: BackgroundTasks,
	file: UploadFile = File(...),
	dataset_name: str = Form(...),
	description: Optional[str] = Form(None),
	format_type: str = Form("auto")
):
	"""
	上传数据集
	"""
	task_id = str(uuid.uuid4())
	created_at = datetime.now()
	
	# 保存文件
	file_path = f"temp/{task_id}_{file.filename}"
	os.makedirs(os.path.dirname(file_path), exist_ok=True)
	with open(file_path, "wb") as f:
		content = await file.read()
		f.write(content)
	
	# 创建数据集记录
	dataset_id = uuid.uuid4()
	dataset = await Dataset.create(
		id=dataset_id,
		name=dataset_name,
		description=description,
		source="uploaded",
		storage_path=f"datasets/{dataset_id}",
		status="processing"
	)
	
	# 记录任务信息
	with tasks.task_lock:
		tasks.tasks[task_id] = {
			"status": tasks.TaskStatus.PENDING,
			"created_at": created_at,
			"request": {
				"file_path": file_path,
				"dataset_id": str(dataset_id),
				"format_type": format_type
			},
			"result": None,
			"error": None,
			"completed_at": None
		}
	
	# 在后台处理数据集
	background_tasks.add_task(process_upload_dataset_task, str(task_id))
	
	return {
		"task_id": task_id,
		"status": tasks.TaskStatus.PENDING,
		"created_at": created_at
	}


@router.post("/datasets/from_huggingface", response_model=tasks.TaskResponse)
async def import_from_huggingface(
	background_tasks: BackgroundTasks,
	dataset_name: str,
	subset: Optional[str] = None,
	split: Optional[str] = None,
	description: Optional[str] = None
):
	"""
	从HF导入数据集
	"""
	task_id = str(uuid.uuid4())
	created_at = datetime.now()
	
	# 创建数据集记录
	dataset_id = uuid.uuid4()
	dataset = await Dataset.create(
		id=dataset_id,
		name=dataset_name.split("/")[-1],
		description=description,
		source="huggingface_hub",
		hf_dataset_name=dataset_name,
		subset=subset,
		storage_path=f"datasets/{dataset_id}",
		status="processing"
	)
	
	# 记录任务信息
	with tasks.task_lock:
		tasks.tasks[task_id] = {
			"status": tasks.TaskStatus.PENDING,
			"created_at": created_at,
			"request": {
				"dataset_id": str(dataset_id),
				"dataset_name": dataset_name,
				"subset": subset,
				"split": split
			},
			"result": None,
			"error": None,
			"completed_at": None
		}
	
	# 在后台处理数据集
	background_tasks.add_task(process_import_from_hf_task, task_id)
	
	return {
		"task_id": task_id,
		"status": tasks.TaskStatus.PENDING,
		"created_at": created_at
	}


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: uuid.UUID):
	"""
	获取数据集信息
	"""
	dataset = await Dataset.get_or_none(id=dataset_id)
	if not dataset:
		raise HTTPException(status_code=404, detail="Dataset not found")
	
	return await DatasetPydantic.from_tortoise_orm(dataset)


@router.get("/datasets/{dataset_id}/preview")
async def preview_dataset(dataset_id: uuid.UUID, n_samples: int = 10):
	"""预览数据集"""
	dataset = await Dataset.get_or_none(id=dataset_id)
	if not dataset:
		raise HTTPException(status_code=404, detail="Dataset not found")
	
	if dataset.status != "completed":
		raise HTTPException(
			status_code=400, detail=f"Dataset is {dataset.status}, not ready for preview"
		)
	
	try:
		hf_dataset = HFDataset.load_from_disk(dataset.storage_path)
		samples = hf_dataset.select(range(min(n_samples, len(hf_dataset))))
		
		# 转换为记录列表格式
		samples_dict = samples.to_dict()
		records = []
		
		for i in range(len(next(iter(samples_dict.values())))):
			record = {}
			for key, values in samples_dict.items():
				if i < len(values):
					record[key] = values[i]
			records.append(record)
		
		# 添加数据集元信息
		result = {
			"samples": records,
			"total_count": len(hf_dataset),
			"columns": list(samples_dict.keys()),
			"dataset_info": {
				"name": dataset.name,
				"description": dataset.description,
				"path": dataset.storage_path,
			}
		}
		
		return result
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error loading dataset: {str(e)}")


@router.get("/datasets")
async def list_datasets():
	"""
	列出当前所有数据集
	"""
	datasets_queryset = Dataset.all()
	return await DatasetPydantic.from_queryset(datasets_queryset)


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: uuid.UUID):
	"""
	删除指定数据集
	"""
	dataset = await Dataset.get_or_none(id=dataset_id)
	if not dataset:
		raise HTTPException(status_code=404, detail="Dataset not found")
	
	# 删除数据集文件
	if os.path.exists(dataset.storage_path):
		import shutil
		shutil.rmtree(dataset.storage_path)
	
	# 删除数据库记录
	await dataset.delete()
	
	return {"message": "Dataset deleted successfully"}
