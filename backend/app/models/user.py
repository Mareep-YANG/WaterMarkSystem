from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from ..database.base import Base


class User(Base):
	__tablename__ = "users"
	
	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
	username = Column(String, unique=True, index=True, nullable=False)
	email = Column(String, unique=True, index=True, nullable=False)
	hashed_password = Column(String, nullable=False)
	is_active = Column(Boolean, default=True)
	created_at = Column(DateTime, default=datetime.now(timezone.utc))
	updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class APIKey(Base):
	__tablename__ = "api_keys"
	
	id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
	user_id = Column(UUID(as_uuid=True), nullable=False)
	key_value = Column(String, unique=True, nullable=False)
	description = Column(String, nullable=True)
	created_at = Column(DateTime, default=datetime.now(timezone.utc))
	expires_at = Column(DateTime, nullable=True)
	is_active = Column(Boolean, default=True)
