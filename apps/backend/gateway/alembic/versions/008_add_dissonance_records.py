"""add dissonance_records table

Revision ID: 008
Revises: 007
Create Date: 2025-12-12 14:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dissonance_records table
    op.create_table(
        'dissonance_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transcript', sa.Text(), nullable=True),
        sa.Column('stated_emotion', sa.String(50), nullable=True),
        sa.Column('actual_emotion', sa.String(50), nullable=True),
        sa.Column('dissonance_score', sa.Float(), nullable=False),
        sa.Column('interpretation', sa.String(100), nullable=True),
        sa.Column('risk_level', sa.String(20), nullable=True),
        sa.Column('detected_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['conversations.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_dissonance_records_user_id', 'dissonance_records', ['user_id'])
    op.create_index('idx_dissonance_records_score', 'dissonance_records', ['dissonance_score'])
    op.create_index('idx_dissonance_records_risk', 'dissonance_records', ['risk_level'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_dissonance_records_risk', table_name='dissonance_records')
    op.drop_index('idx_dissonance_records_score', table_name='dissonance_records')
    op.drop_index('idx_dissonance_records_user_id', table_name='dissonance_records')
    
    # Drop table
    op.drop_table('dissonance_records')

