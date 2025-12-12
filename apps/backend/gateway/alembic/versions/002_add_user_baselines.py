"""add user_baselines table

Revision ID: 002
Revises: 001
Create Date: 2025-12-12 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_baselines table
    op.create_table(
        'user_baselines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('baseline_type', sa.String(50), nullable=False),
        sa.Column('baseline_value', postgresql.JSONB, nullable=False),
        sa.Column('session_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('established_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'baseline_type', name='uq_user_baselines_user_type')
    )
    
    # Create indexes
    op.create_index('idx_user_baselines_user_id', 'user_baselines', ['user_id'])
    op.create_index('idx_user_baselines_type', 'user_baselines', ['baseline_type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_user_baselines_type', table_name='user_baselines')
    op.drop_index('idx_user_baselines_user_id', table_name='user_baselines')
    
    # Drop table
    op.drop_table('user_baselines')

