from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext

from .settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
	"""生成JWT访问令牌"""
	if expires_delta:
		expire = datetime.now(timezone.utc) + expires_delta
	else:
		expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	
	to_encode = {"exp": expire, "sub": str(subject)}
	encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
	return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
	"""验证密码"""
	return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
	"""生成密码哈希"""
	return pwd_context.hash(password)


def create_api_key() -> str:
	"""生成API密钥"""
	import secrets
	return secrets.token_urlsafe(32)


def verify_api_key(api_key: str, stored_key: str) -> bool:
	"""验证API密钥"""
	import secrets
	return secrets.compare_digest(api_key, stored_key)
