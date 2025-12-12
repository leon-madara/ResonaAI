"""add risk_assessments table

Revision ID: 005
Revises: 004
Create Date: 2025-12-12 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create risk_assessments table
    op.create_table(
        'risk_assessments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('risk_level', sa.String(20), nullable=False),
        sa.Column('risk_factors', postgresql.JSONB, nullable=True),
        sa.Column('dissonance_contribution', sa.Float(), nullable=True),
        sa.Column('baseline_deviation_contribution', sa.Float(), nullable=True),
        sa.Column('pattern_contribution', sa.Float(), nullable=True),
        sa.Column('assessed_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('action_taken', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.CheckConstraint("risk_level IN ('low', 'medium', 'high', 'critical')", name='ck_risk_assessments_level')
    )
    
    # Create indexes
    op.create_index('idx_risk_assessments_user_id', 'risk_assessments', ['user_id'])
    op.create_index('idx_risk_assessments_level', 'risk_assessments', ['risk_level'])
    op.create_index('idx_risk_assessments_score', 'risk_assessments', ['risk_score'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_risk_assessments_score', table_name='risk_assessments')
    op.drop_index('idx_risk_assessments_level', table_name='risk_assessments')
    op.drop_index('idx_risk_assessments_user_id', table_name='risk_assessments')
    
    # Drop table
    op.drop_table('risk_assessments')

