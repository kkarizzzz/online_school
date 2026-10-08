"""Программа курса, отметки «решено» в банке, история повторений

Revision ID: 4b1ea043e173
Revises: 34a01fec8e79
Create Date: 2026-10-08 20:17:33.463986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '4b1ea043e173'
down_revision: Union[str, Sequence[str], None] = '34a01fec8e79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('curricula',
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('subject', name=op.f('pk_curricula'))
    )
    op.create_table('review_sessions',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.BigInteger(), nullable=False),
    sa.Column('mode', sa.String(length=16), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('answers', sa.Integer(), nullable=False),
    sa.Column('correct', sa.Integer(), nullable=False),
    sa.Column('best_streak', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_review_sessions_student_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('student_id', 'client_id', name=op.f('pk_review_sessions'))
    )
    op.create_index('ix_review_sessions_student_started', 'review_sessions', ['student_id', 'started_at'], unique=False)
    op.create_table('bank_marks',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_bank_marks_student_id_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_bank_marks_task_id_tasks'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('student_id', 'task_id', name=op.f('pk_bank_marks'))
    )
    op.add_column('lessons', sa.Column('summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('lessons', sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('review_questions', sa.Column('topic_label', sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('review_questions', 'topic_label')
    op.drop_column('lessons', 'content')
    op.drop_column('lessons', 'summary')
    op.drop_table('bank_marks')
    op.drop_index('ix_review_sessions_student_started', table_name='review_sessions')
    op.drop_table('review_sessions')
    op.drop_table('curricula')
