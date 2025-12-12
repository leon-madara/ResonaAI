"""add user_interfaces table

Revision ID: 004
Revises: 003
Create Date: 2025-12-12 14:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_interfaces table
    op.create_table(
        'user_interfaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interface_config', postgresql.JSONB, nullable=False),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('active', sa.Boolean(), server_default='true', nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_user_interfaces_user_id', 'user_interfaces', ['user_id'])
    op.create_index('idx_user_interfaces_active', 'user_interfaces', ['active'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_user_interfaces_active', table_name='user_interfaces')
    op.drop_index('idx_user_interfaces_user_id', table_name='user_interfaces')
    
    # Drop table
    op.drop_table('user_interfaces')

