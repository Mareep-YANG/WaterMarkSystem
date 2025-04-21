from typing import Dict, Any
import psutil
import torch
import platform
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()

class SystemInfo(BaseModel):
    system_type: str
    torch_device: str
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    gpu_memory_usage: float

def get_system_info() -> Dict[str, Any]:
    # 获取系统类型
    system_type = platform.system()
    
    # 获取PyTorch设备信息
    if torch.cuda.is_available():
        torch_device = f"CUDA ({torch.cuda.get_device_name(0)})"
    else:
        torch_device = "CPU"
    
    # 获取CPU使用率
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # 获取内存使用率
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    
    # 获取GPU使用率和显存使用率
    gpu_usage = 0.0
    gpu_memory_usage = 0.0
    
    if torch.cuda.is_available():
        gpu_usage = torch.cuda.utilization()
        gpu_memory = torch.cuda.memory_allocated(0) / torch.cuda.max_memory_allocated(0) * 100
        gpu_memory_usage = float(gpu_memory)
    
    return {
        "system_type": system_type,
        "torch_device": torch_device,
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "gpu_usage": gpu_usage,
        "gpu_memory_usage": gpu_memory_usage
    }

@router.get("/system/overview", response_model=SystemInfo)
async def get_system_overview():
    """获取系统概览信息"""
    return get_system_info() 