from datetime import timedelta
from typing import Any
import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm as OAuth2Form
from pydantic import BaseModel, EmailStr
from tortoise.transactions import in_transaction

from ..deps import get_current_active_user
from app.core import cfg
from app.core.security import (
	create_access_token,
	create_api_key,
	get_password_hash,
	verify_password
)
from app.dbModels.user import APIKey, User

router = APIRouter()


class Token(BaseModel):
	access_token: str
	token_type: str


class UserCreate(BaseModel):
	username: str
	email: EmailStr
	password: str


class UserResponse(BaseModel):
	username: str
	email: str
	is_active: bool
	avatar: str | None = None
	
	class Config:
		from_attributes = True


class APIKeyResponse(BaseModel):
	key: str
	description: str


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate):
	async with in_transaction() as conn:
		user = await User.filter(username=user_in.username).first()
		if user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Username already registered",
			)
		
		user = await User.filter(email=user_in.email).first()
		if user:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail="Email already registered",
			)
		
		user = User(
			username=user_in.username,
			email=user_in.email,
			hashed_password=get_password_hash(user_in.password),
		)
		await user.save(using_db=conn)
		
		return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2Form = Depends()) -> Any:
	"""
	用户登录
	"""
	# 验证用户
	user = await User.filter(username=form_data.username).first()
	if not user or not verify_password(form_data.password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	
	# 生成访问令牌
	access_token_expires = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(user.id, expires_delta=access_token_expires)
	
	return {"access_token": access_token, "token_type": "bearer"}


@router.post("/api_key", response_model=APIKeyResponse)
async def set_api_key(
	description: str, current_user: User = Depends(get_current_active_user)
) -> Any:
	"""
	为（当前）用户创建新的API密钥
	"""
	key_value = create_api_key()
	api_key = APIKey(
		user_id=current_user.id,
		key_value=key_value,
		description=description
	)
	
	await api_key.save()
	
	return {"key": key_value, "description": description}


@router.get("/info", response_model=UserResponse)
async def get_info(current_user: User = Depends(get_current_active_user)) -> Any:
	"""
	获取当前用户信息
	"""
	return current_user


@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
	file: UploadFile = File(...),
	current_user: User = Depends(get_current_active_user)
):
	if not file.content_type.startswith('image/'):
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="File must be an image"
		)
	
	# 创建上传目录
	upload_dir = os.path.join(cfg.UPLOAD_DIR, "avatars")
	os.makedirs(upload_dir, exist_ok=True)
	
	# 生成文件名
	file_extension = os.path.splitext(file.filename)[1]
	filename = f"{current_user.id}{file_extension}"
	file_path = os.path.join(upload_dir, filename)
	
	# 保存文件
	try:
		contents = await file.read()
		with open(file_path, "wb") as f:
			f.write(contents)
	except Exception as e:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Could not upload file: {str(e)}"
		)
	
	# 更新用户头像路径
	avatar_url = f"/static/avatars/{filename}"
	current_user.avatar = avatar_url
	await current_user.save()
	
	return current_user
