from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.models.llm import llm_service
from app.dbModels import HuggingfaceModel

router = APIRouter()


class HuggingfaceModelCreate(BaseModel):
    model_name: str = Field(..., description="模型名称")
    description: Optional[str] = Field(None, description="模型描述")


class HuggingfaceModelUpdate(BaseModel):
    model_name: Optional[str] = None
    description: Optional[str] = None


class HuggingfaceModelResponse(BaseModel):
    id: int
    model_name: str
    description: Optional[str] = None
    is_loaded: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TextGenerationRequest(BaseModel):
    prompt: str
    max_length: int = 100
    temperature: float = 0.7
    top_p: float = 0.9


@router.post("/add_model", response_model=HuggingfaceModelResponse)
async def create_model(model_data: HuggingfaceModelCreate):
    """添加新的Huggingface模型到列表"""
    existing = await HuggingfaceModel.filter(model_name=model_data.model_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="模型已存在")

    model = await HuggingfaceModel.create(**model_data.dict())
    return model


@router.get("/models", response_model=List[HuggingfaceModelResponse])
async def get_models():
    """获取所有模型列表"""
    return await HuggingfaceModel.all()


@router.get("/{model_id}", response_model=HuggingfaceModelResponse)
async def get_model(model_id: int):
    """获取指定ID的模型信息"""
    model = await HuggingfaceModel.filter(id=model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")
    return model


@router.put("/{model_id}", response_model=HuggingfaceModelResponse)
async def update_model(model_id: int, model_data: HuggingfaceModelUpdate):
    """更新模型信息"""
    model = await HuggingfaceModel.filter(id=model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    update_data = {k: v for k, v in model_data.dict().items() if v is not None}
    await model.update_from_dict(update_data).save()
    return await HuggingfaceModel.get(id=model_id)


@router.delete("/{model_id}")
async def delete_model(model_id: int):
    """删除指定模型"""
    deleted_count = await HuggingfaceModel.filter(id=model_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="模型不存在")
    return {"message": "模型已成功删除"}


@router.post("/{model_id}/load")
async def load_model(model_id: int, background_tasks: BackgroundTasks):
    """加载指定模型到内存"""
    model = await HuggingfaceModel.filter(id=model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    async def _load_model():
        await llm_service.load_model(model.model_name)
        model.is_loaded = True
        await model.save()

    background_tasks.add_task(_load_model)
    return {"message": f"正在加载模型: {model.model_name}"}


@router.post("/{model_id}/generate")
async def generate_text(model_id: int, request: TextGenerationRequest):
    """使用指定模型生成文本"""
    model = await HuggingfaceModel.filter(id=model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="模型不存在")

    # 如果模型未加载，先加载模型
    if not model.is_loaded:
        try:
            await llm_service.load_model(model.model_name)
            model.is_loaded = True
            await model.save()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")

    try:
        generated_text = await llm_service.generate(
            prompt=request.prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p
        )
        return {"generated_text": generated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文本生成失败: {str(e)}")