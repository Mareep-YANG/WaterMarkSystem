from datetime import datetime, timezone
from uuid import uuid4

from tortoise import fields
from tortoise.models import Model


class User(Model):
	id = fields.IntField(pk=True)
	username = fields.CharField(max_length=50, unique=True)
	email = fields.CharField(max_length=255, unique=True)
	hashed_password = fields.CharField(max_length=255)
	is_active = fields.BooleanField(default=True)
	avatar = fields.CharField(max_length=255, null=True)
	
	class Meta:
		table = "users"


class APIKey(Model):
	id = fields.UUIDField(pk=True, default=uuid4)
	user_id = fields.UUIDField(null=False)
	key_value = fields.CharField(max_length=255, unique=True, null=False)
	description = fields.CharField(max_length=255, null=True)
	created_at = fields.DatetimeField(default=datetime.now(timezone.utc))
	expires_at = fields.DatetimeField(null=True)
	is_active = fields.BooleanField(default=True)
	
	class Meta:
		table = "api_keys"
