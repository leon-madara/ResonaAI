"""add interface_evolution_log table

Revision ID: 007
Revises: 006
Create Date: 2025-12-12 14:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create interface_evolution_log table
    op.create_table(
        'interface_evolution_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('changes', postgresql.JSONB, nullable=False),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_interface_evolution_user_id', 'interface_evolution_log', ['user_id'])
    op.create_index('idx_interface_evolution_version', 'interface_evolution_log', ['version'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_interface_evolution_version', table_name='interface_evolution_log')
    op.drop_index('idx_interface_evolution_user_id', table_name='interface_evolution_log')
    
    # Drop table
    op.drop_table('interface_evolution_log')

