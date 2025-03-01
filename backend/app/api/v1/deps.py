from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from ...core.settings import settings
from ...database.base import get_db
from ...models.user import APIKey, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
	db: Session = Depends(get_db),
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
			token,
			settings.SECRET_KEY,
			algorithms=[settings.ALGORITHM]
		)
		user_id: str = payload.get("sub")
		if user_id is None:
			raise credentials_exception
	except JWTError:
		raise credentials_exception
	
	user = db.query(User).filter(User.id == user_id).first()
	if user is None:
		raise credentials_exception
	return user


async def get_current_active_user(
	current_user: User = Depends(get_current_user),
) -> User:
	"""
	获取当前活跃用户
	"""
	if not current_user.is_active:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Inactive user"
		)
	return current_user


async def validate_api_key(
	db: Session = Depends(get_db),
	api_key: Optional[str] = Security(api_key_header)
) -> Optional[User]:
	"""
	验证API密钥
	"""
	if not api_key:
		return None
	
	api_key_record = db.query(APIKey).filter(
		APIKey.key_value == api_key,
		APIKey.is_active == True
	).first()
	
	if not api_key_record:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid API key"
		)
	
	user = db.query(User).filter(User.id == api_key_record.user_id).first()
	if not user or not user.is_active:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid API key"
		)
	
	return user


async def get_auth_user(
	current_user: Optional[User] = Security(get_current_active_user, scopes=[]),
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
