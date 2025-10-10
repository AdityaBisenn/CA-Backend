"""add_ram_cognitive_tables

Revision ID: b4b6fafe88d5
Revises: 7fae4977ee93
Create Date: 2025-10-10 23:55:24.987737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4b6fafe88d5'
down_revision: Union[str, Sequence[str], None] = '7fae4977ee93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to add RAM cognitive framework tables."""
    
    # Create heuristic_memory table
    op.create_table('heuristic_memory',
        sa.Column('heuristic_id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('idea', sa.Text(), nullable=False),
        sa.Column('function_name', sa.String(), nullable=False),
        sa.Column('success_score', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('context_meta', sa.JSON(), nullable=True),
        sa.Column('pattern_hash', sa.String(), nullable=False),
        sa.Column('usage_count', sa.Numeric(precision=10, scale=0), nullable=True),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('heuristic_id')
    )
    
    # Create indexes for heuristic_memory
    op.create_index('idx_heuristic_company_score', 'heuristic_memory', ['company_id', 'success_score'])
    op.create_index('idx_heuristic_hash', 'heuristic_memory', ['pattern_hash'])
    op.create_index('idx_heuristic_function', 'heuristic_memory', ['function_name'])
    
    # Create reflection_log table
    op.create_table('reflection_log',
        sa.Column('reflection_id', sa.String(), nullable=False),
        sa.Column('company_id', sa.String(), nullable=False),
        sa.Column('reflection_type', sa.String(), nullable=False),
        sa.Column('trigger_event', sa.String(), nullable=False),
        sa.Column('performance_metrics', sa.JSON(), nullable=True),
        sa.Column('analysis_results', sa.JSON(), nullable=True),
        sa.Column('improvement_strategies', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('meta_insights', sa.Text(), nullable=True),
        sa.Column('action_items', sa.JSON(), nullable=True),
        sa.Column('is_implemented', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('reflection_id')
    )
    
    # Create indexes for reflection_log
    op.create_index('idx_reflection_company_type', 'reflection_log', ['company_id', 'reflection_type'])
    op.create_index('idx_reflection_date', 'reflection_log', ['created_at'])
    op.create_index('idx_reflection_confidence', 'reflection_log', ['confidence_score'])


def downgrade() -> None:
    """Downgrade schema to remove RAM cognitive framework tables."""
    # Drop indexes first
    op.drop_index('idx_reflection_confidence', table_name='reflection_log')
    op.drop_index('idx_reflection_date', table_name='reflection_log')
    op.drop_index('idx_reflection_company_type', table_name='reflection_log')
    op.drop_index('idx_heuristic_function', table_name='heuristic_memory')
    op.drop_index('idx_heuristic_hash', table_name='heuristic_memory')
    op.drop_index('idx_heuristic_company_score', table_name='heuristic_memory')
    
    # Drop tables
    op.drop_table('reflection_log')
    op.drop_table('heuristic_memory')
