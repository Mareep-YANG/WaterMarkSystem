from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
	return """
        ALTER TABLE `api_keys` ALTER COLUMN `created_at` SET DEFAULT '2025-03-30 14:47:29.432912+00:00';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
	return """
        ALTER TABLE `api_keys` ALTER COLUMN `created_at` SET DEFAULT '2025-03-30 14:41:29.400299+00:00';"""
