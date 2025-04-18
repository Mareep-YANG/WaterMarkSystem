from typing import Optional

from fastapi import (
	Depends,
	FastAPI,
	HTTPException,
	Security,
	status
)
from fastapi.security import (
	APIKeyHeader,
	OAuth2PasswordBearer
)
from jose import jwt, JWTError
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import DoesNotExist

from app.core import cfg, TORTOISE_ORM
from app.dbModels.user import APIKey, User

oauth2_scheme = OAuth2PasswordBearer(
	tokenUrl=f"{cfg.API_ENDPOINT}/auth/login"
)
api_key_header = APIKeyHeader(
	name="X-API-Key",
	auto_error=False
)


async def get_current_user(
	token: str = Depends(oauth2_scheme)
) -> User:
	"""
	获取当前用户
	"""
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)
	try:
		payload = jwt.decode(
			token, cfg.JWT_SECRET_KEY,
			algorithms=[cfg.ALGORITHM]
		)
		user_id: str = payload.get("sub")
		if user_id is None:
			raise credentials_exception
	except JWTError:
		raise credentials_exception
	
	try:
		user = await User.get(id=user_id)
	except DoesNotExist:
		raise credentials_exception
	return user


async def validate_api_key(
	api_key: Optional[str] = Security(api_key_header)
) -> Optional[User]:
	"""
	验证API密钥
	"""
	if not api_key:
		return None
	
	try:
		api_key_record = await APIKey.get(
			key_value=api_key,
			is_active=True
		)
		user = await User.get(id=api_key_record.user_id)
		if not user.is_active:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid API key"
			)
	except DoesNotExist:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid API key"
		)
	
	return user


async def get_auth_user(
	current_user: Optional[User] = Depends(get_current_user),
	api_key_user: Optional[User] = Depends(validate_api_key)
) -> User:
	"""
	获取认证用户（支持JWT或API密钥）
	"""
	if current_user:
		return current_user
	if api_key_user:
		return api_key_user
	raise HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Authentication required"
	)


def get_current_active_user(
	current_user: User = Depends(get_auth_user)
):
	if not current_user.is_active:
		raise HTTPException(
			status_code=400,
			detail="Inactive user"
		)
	return current_user


def init_db(app: FastAPI):
	register_tortoise(
		app=app,
		config=TORTOISE_ORM,
		# generate_schemas=True,  # 若db为空，自动创建表（生产环境勿开）
		add_exception_handlers=True  # 生产环境勿开，会泄露调试信息
	)
