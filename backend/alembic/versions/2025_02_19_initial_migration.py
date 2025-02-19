"""Initial migration

Revision ID: 2025_02_19
Create Date: 2025-02-19 22:26:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025_02_19'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_value', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create watermark_records table
    op.create_table(
        'watermark_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('algorithm_name', sa.String(50), nullable=False),
        sa.Column('text_hash', sa.String(64), nullable=False),
        sa.Column('params', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])
    op.create_index('ix_api_keys_key_value', 'api_keys', ['key_value'])
    op.create_index('ix_watermark_records_user_id', 'watermark_records', ['user_id'])
    op.create_index('ix_watermark_records_algorithm_name', 'watermark_records', ['algorithm_name'])

def downgrade():
    # Drop indexes
    op.drop_index('ix_watermark_records_algorithm_name')
    op.drop_index('ix_watermark_records_user_id')
    op.drop_index('ix_api_keys_key_value')
    op.drop_index('ix_api_keys_user_id')
    op.drop_index('ix_users_email')
    op.drop_index('ix_users_username')

    # Drop tables
    op.drop_table('watermark_records')
    op.drop_table('api_keys')
    op.drop_table('users')