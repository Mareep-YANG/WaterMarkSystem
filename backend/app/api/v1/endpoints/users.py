from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..deps import get_current_active_user, get_db
from ....core.security import (create_access_token, create_api_key, get_password_hash, verify_password)
from ....core.settings import settings
from ....models.user import APIKey, User

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
	
	class Config:
		from_attributes = True


class APIKeyResponse(BaseModel):
	key: str
	description: str


@router.post("/register", response_model=UserResponse)
async def register(
	user_in: UserCreate,
	db: Session = Depends(get_db)
) -> Any:
	"""
	注册新用户
	"""
	# 检查用户名是否已存在
	user = db.query(User).filter(User.username == user_in.username).first()
	if user:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Username already registered"
		)
	
	# 检查邮箱是否已存在
	user = db.query(User).filter(User.email == user_in.email).first()
	if user:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Email already registered"
		)
	
	# 创建新用户
	user = User(
		username=user_in.username,
		email=user_in.email,
		hashed_password=get_password_hash(user_in.password)
	)
	db.add(user)
	db.commit()
	db.refresh(user)
	
	return user


@router.post("/login", response_model=Token)
async def login(
	db: Session = Depends(get_db),
	form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
	"""
	用户登录
	"""
	# 验证用户
	user = db.query(User).filter(User.username == form_data.username).first()
	if not user or not verify_password(form_data.password, user.hashed_password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	
	# 生成访问令牌
	access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(
		user.id, expires_delta=access_token_expires
	)
	
	return {
		"access_token": access_token,
		"token_type"  : "bearer"
	}


@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key_for_user(
	description: str,
	current_user: User = Depends(get_current_active_user),
	db: Session = Depends(get_db)
) -> Any:
	"""
	为当前用户创建新的API密钥
	"""
	key_value = create_api_key()
	api_key = APIKey(
		user_id=current_user.id,
		key_value=key_value,
		description=description
	)
	
	db.add(api_key)
	db.commit()
	
	return {
		"key"        : key_value,
		"description": description
	}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
	current_user: User = Depends(get_current_active_user),
) -> Any:
	"""
	获取当前用户信息
	"""
	return current_user
