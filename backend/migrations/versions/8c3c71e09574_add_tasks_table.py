"""add tasks table

Revision ID: 8c3c71e09574
Revises: c92c8d58d39a
Create Date: 2026-10-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c3c71e09574'
down_revision: Union[str, Sequence[str], None] = 'c92c8d58d39a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


subject_enum = sa.Enum('math', 'physics', 'russian', 'informatics', name='subjectenum')


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject', subject_enum, nullable=False),
    sa.Column('topic', sa.String(length=200), nullable=False),
    sa.Column('task_number', sa.Integer(), nullable=False),
    sa.Column('difficulty', sa.String(length=50), nullable=False),
    sa.Column('part', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('source', sa.String(length=200), nullable=True),
    sa.Column('sub_topic', sa.String(length=200), nullable=True),
    sa.Column('image_url', sa.String(length=500), nullable=True),
    sa.Column('answer', sa.String(length=255), nullable=True),
    sa.Column('max_score', sa.Integer(), nullable=False),
    sa.Column('is_auto_check', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('solution_text', sa.Text(), nullable=True),
    sa.Column('solution_video_url', sa.String(length=500), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['curators.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_subject'), 'tasks', ['subject'], unique=False)
    op.create_index(op.f('ix_tasks_topic'), 'tasks', ['topic'], unique=False)
    op.create_index(op.f('ix_tasks_source'), 'tasks', ['source'], unique=False)
    op.create_index(op.f('ix_tasks_sub_topic'), 'tasks', ['sub_topic'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_tasks_sub_topic'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_source'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_topic'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_subject'), table_name='tasks')
    op.drop_table('tasks')
    subject_enum.drop(op.get_bind(), checkfirst=True)
