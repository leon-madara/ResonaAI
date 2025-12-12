"""add session_deviations table

Revision ID: 003
Revises: 002
Create Date: 2025-12-12 14:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create session_deviations table
    op.create_table(
        'session_deviations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deviation_type', sa.String(50), nullable=False),
        sa.Column('baseline_value', postgresql.JSONB, nullable=True),
        sa.Column('current_value', postgresql.JSONB, nullable=True),
        sa.Column('deviation_score', sa.Float(), nullable=False),
        sa.Column('detected_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['conversations.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_session_deviations_user_id', 'session_deviations', ['user_id'])
    op.create_index('idx_session_deviations_session_id', 'session_deviations', ['session_id'])
    op.create_index('idx_session_deviations_score', 'session_deviations', ['deviation_score'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_session_deviations_score', table_name='session_deviations')
    op.drop_index('idx_session_deviations_session_id', table_name='session_deviations')
    op.drop_index('idx_session_deviations_user_id', table_name='session_deviations')
    
    # Drop table
    op.drop_table('session_deviations')

