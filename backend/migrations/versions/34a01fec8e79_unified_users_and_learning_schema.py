"""Единая таблица пользователей и схема обучения

Кураторы и психологи удалены. Ученики и родители переезжают в users (id учеников
сохраняются — выданные токены остаются рабочими), связь родитель–ребёнок — в parent_students.
Таблица tasks пересоздаётся по схеме банка из concepts/tasks_page (на момент миграции она пуста).
Добавлены наборы заданий, назначения, попытки, ответы, статистика, уроки, повторение,
достижения и уведомления. Перечисления — VARCHAR + CHECK вместо нативных ENUM.

Revision ID: 34a01fec8e79
Revises: 8c3c71e09574
Create Date: 2026-10-08 18:23:10.285563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '34a01fec8e79'
down_revision: Union[str, Sequence[str], None] = '8c3c71e09574'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Профильная математика: (номер, часть, первичные баллы, заголовок)
MATH_NUMBERS = [
    (1, 1, 1, 'Планиметрия'),
    (2, 1, 1, 'Векторы'),
    (3, 1, 1, 'Стереометрия'),
    (4, 1, 1, 'Простая теория вероятностей'),
    (5, 1, 1, 'Сложная теория вероятностей'),
    (6, 1, 1, 'Простейшие уравнения'),
    (7, 1, 1, 'Вычисления и преобразования'),
    (8, 1, 1, 'Производная и первообразная'),
    (9, 1, 1, 'Задачи с прикладным содержанием'),
    (10, 1, 1, 'Текстовые задачи'),
    (11, 1, 1, 'Графики функций'),
    (12, 1, 1, 'Наибольшее и наименьшее значение функций'),
    (13, 2, 2, 'Уравнения'),
    (14, 2, 3, 'Стереометрия'),
    (15, 2, 2, 'Неравенства'),
    (16, 2, 2, 'Финансовая математика'),
    (17, 2, 3, 'Планиметрия'),
    (18, 2, 4, 'Задачи с параметром'),
    (19, 2, 4, 'Числа и их свойства'),
]

# Шкала ЕГЭ-2025 по профильной математике, индекс — первичный балл (как в concepts/variants_page)
MATH_SCALE_2025 = [0, 6, 11, 17, 22, 27, 34, 40, 46, 52, 58, 64, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94,
                   95, 96, 97, 98, 99, 100, 100, 100]

# Коды совпадают с frontend/src/entities/achievement/model/constants.ts
ACHIEVEMENTS = [
    ('param_guru', 'Гуру параметров', '10 верных задач с параметрами'),
    ('streak_7', 'Огонь недели', 'Серия из 7 дней подряд'),
    ('sniper', 'Снайпер', '50 задач без ошибок'),
    ('marathon', 'Марафонец', '100 часов на платформе'),
    ('pioneer', 'Первопроходец', 'Пройден вводный модуль'),
    ('perfect_score', 'Стобалльник', 'Пробник на 100 баллов'),
]


def _create_new_schema() -> None:
    op.create_table('achievements',
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=300), nullable=False),
    sa.PrimaryKeyConstraint('code', name=op.f('pk_achievements'))
    )
    op.create_table('exam_numbers',
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('part', sa.Integer(), nullable=False),
    sa.Column('max_score', sa.Integer(), nullable=False),
    sa.Column('answer_type', sa.Enum('short', 'digits_set', 'sequence', 'detailed', name='answer_type', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('subject', 'number', name=op.f('pk_exam_numbers'))
    )
    op.create_table('groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_groups'))
    )
    op.create_table('lessons',
    sa.Column('id', sa.String(length=20), nullable=False),
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('topic_code', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_lessons'))
    )
    op.create_index(op.f('ix_lessons_topic_code'), 'lessons', ['topic_code'], unique=False)
    op.create_table('score_scales',
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('primary_score', sa.Integer(), nullable=False),
    sa.Column('secondary_score', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('subject', 'year', 'primary_score', name=op.f('pk_score_scales'))
    )
    op.create_table('shared_texts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_shared_texts'))
    )
    op.create_table('sources',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_sources')),
    sa.UniqueConstraint('name', name=op.f('uq_sources_name'))
    )
    op.create_table('topics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('task_number', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('position', sa.Integer(), server_default='0', nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['topics.id'], name=op.f('fk_topics_parent_id_topics'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_topics'))
    )
    op.create_index(op.f('ix_topics_parent_id'), 'topics', ['parent_id'], unique=False)
    op.create_index('ix_topics_subject_number', 'topics', ['subject', 'task_number'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role', sa.Enum('student', 'parent', 'teacher', 'admin', name='user_role', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('telegram_chat_id', sa.BigInteger(), nullable=True),
    sa.Column('image_url', sa.String(length=500), nullable=True),
    sa.Column('timezone', sa.String(length=64), server_default='Europe/Moscow', nullable=False),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    op.create_table('group_members',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], name=op.f('fk_group_members_group_id_groups'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_group_members_student_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('group_id', 'student_id', name=op.f('pk_group_members'))
    )
    op.create_index(op.f('ix_group_members_student_id'), 'group_members', ['student_id'], unique=False)
    op.create_table('lesson_progress',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('lesson_id', sa.String(length=20), nullable=False),
    sa.Column('status', sa.Enum('in_progress', 'done', name='lesson_status', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('percent', sa.Integer(), nullable=False),
    sa.Column('step', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], name=op.f('fk_lesson_progress_lesson_id_lessons'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_lesson_progress_student_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('student_id', 'lesson_id', name=op.f('pk_lesson_progress'))
    )
    op.create_table('notification_settings',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('homework_assigned', 'homework_due_soon', 'homework_overdue', 'homework_submitted', 'attempt_graded', 'achievement_unlocked', 'system', name='notification_type', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('channel', sa.Enum('telegram', 'sms', 'email', name='notification_channel', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_notification_settings_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'type', 'channel', name=op.f('pk_notification_settings'))
    )
    op.create_table('notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('homework_assigned', 'homework_due_soon', 'homework_overdue', 'homework_submitted', 'attempt_graded', 'achievement_unlocked', 'system', name='notification_type', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('dedup_key', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_notifications_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notifications')),
    sa.UniqueConstraint('user_id', 'dedup_key', name=op.f('uq_notifications_user_id_dedup_key'))
    )
    op.create_index('ix_notifications_unread', 'notifications', ['user_id'], unique=False, postgresql_where=sa.text('read_at IS NULL'))
    op.create_index('ix_notifications_user_created', 'notifications', ['user_id', 'created_at'], unique=False)
    op.create_table('parent_students',
    sa.Column('parent_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['parent_id'], ['users.id'], name=op.f('fk_parent_students_parent_id_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_parent_students_student_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('parent_id', 'student_id', name=op.f('pk_parent_students'))
    )
    op.create_index(op.f('ix_parent_students_student_id'), 'parent_students', ['student_id'], unique=False)
    op.create_table('review_questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('kind', sa.Enum('theory', 'calc', name='review_question_kind', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('options', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('explanation', sa.Text(), nullable=True),
    sa.Column('topic_id', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], name=op.f('fk_review_questions_topic_id_topics'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_review_questions'))
    )
    op.create_table('student_achievements',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('unlocked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['code'], ['achievements.code'], name=op.f('fk_student_achievements_code_achievements'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_student_achievements_student_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('student_id', 'code', name=op.f('pk_student_achievements'))
    )
    op.create_table('student_daily_activity',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('day', sa.Date(), nullable=False),
    sa.Column('answered', sa.Integer(), nullable=False),
    sa.Column('correct', sa.Integer(), nullable=False),
    sa.Column('seconds', sa.Integer(), nullable=False),
    sa.Column('lessons_done', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_student_daily_activity_student_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('student_id', 'day', name=op.f('pk_student_daily_activity'))
    )
    op.create_table('student_profiles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('grade', sa.Integer(), nullable=True),
    sa.Column('exam_year', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_student_profiles_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', name=op.f('pk_student_profiles'))
    )
    op.create_table('student_subjects',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('target_score', sa.Integer(), nullable=True),
    sa.Column('access_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_student_subjects_student_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('student_id', 'subject', name=op.f('pk_student_subjects'))
    )
    op.create_table('student_topic_stats',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('topic_id', sa.Integer(), nullable=False),
    sa.Column('answered', sa.Integer(), nullable=False),
    sa.Column('correct', sa.Integer(), nullable=False),
    sa.Column('tasks_solved', sa.Integer(), nullable=False),
    sa.Column('last_answer_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_student_topic_stats_student_id_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], name=op.f('fk_student_topic_stats_topic_id_topics'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('student_id', 'topic_id', name=op.f('pk_student_topic_stats'))
    )
    op.create_table('task_sets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('kind', sa.Enum('homework', 'variant', 'drill', 'lesson_practice', name='task_set_kind', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('publisher', sa.String(length=100), nullable=True),
    sa.Column('difficulty', sa.Integer(), nullable=True),
    sa.Column('time_limit_sec', sa.Integer(), nullable=True),
    sa.Column('is_public', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('is_standard', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('lesson_id', sa.String(length=20), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('difficulty BETWEEN 1 AND 4', name=op.f('ck_task_sets_difficulty')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_task_sets_created_by_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], name=op.f('fk_task_sets_lesson_id_lessons'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_task_sets'))
    )
    op.create_index('ix_task_sets_catalog', 'task_sets', ['subject', 'kind'], unique=False, postgresql_where=sa.text('is_public AND archived_at IS NULL'))
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.Enum('math', 'physics', 'russian', 'informatics', name='subject', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('task_number', sa.Integer(), nullable=False),
    sa.Column('part', sa.Integer(), nullable=False),
    sa.Column('difficulty', sa.Integer(), nullable=False),
    sa.Column('topic_id', sa.Integer(), nullable=True),
    sa.Column('shared_text_id', sa.Integer(), nullable=True),
    sa.Column('condition', sa.Text(), nullable=False),
    sa.Column('answer_type', sa.Enum('short', 'digits_set', 'sequence', 'detailed', name='answer_type', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('answer', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('max_score', sa.Integer(), nullable=False),
    sa.Column('solution', sa.Text(), nullable=True),
    sa.Column('solution_video_url', sa.String(length=500), nullable=True),
    sa.Column('grade_criteria', sa.Text(), nullable=True),
    sa.Column('external_source', sa.String(length=50), nullable=True),
    sa.Column('external_id', sa.String(length=100), nullable=True),
    sa.Column('raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('difficulty BETWEEN 1 AND 4', name=op.f('ck_tasks_difficulty')),
    sa.CheckConstraint('max_score > 0', name=op.f('ck_tasks_max_score')),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], name=op.f('fk_tasks_created_by_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['shared_text_id'], ['shared_texts.id'], name=op.f('fk_tasks_shared_text_id_shared_texts'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], name=op.f('fk_tasks_topic_id_topics'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_tasks')),
    sa.UniqueConstraint('external_source', 'external_id', name=op.f('uq_tasks_external_source_external_id'))
    )
    op.create_index('ix_tasks_subject_number', 'tasks', ['subject', 'task_number'], unique=False)
    op.create_index(op.f('ix_tasks_topic_id'), 'tasks', ['topic_id'], unique=False)
    op.create_table('assignments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('set_id', sa.Integer(), nullable=False),
    sa.Column('assigned_by', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('deadline_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], name=op.f('fk_assignments_assigned_by_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], name=op.f('fk_assignments_group_id_groups'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['set_id'], ['task_sets.id'], name=op.f('fk_assignments_set_id_task_sets'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_assignments'))
    )
    op.create_index(op.f('ix_assignments_set_id'), 'assignments', ['set_id'], unique=False)
    op.create_table('notification_deliveries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('notification_id', sa.Integer(), nullable=False),
    sa.Column('channel', sa.Enum('telegram', 'sms', 'email', name='notification_channel', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('status', sa.Enum('pending', 'sent', 'failed', name='delivery_status', native_enum=False, create_constraint=True, length=32), server_default='pending', nullable=False),
    sa.Column('tries', sa.Integer(), server_default='0', nullable=False),
    sa.Column('last_error', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['notification_id'], ['notifications.id'], name=op.f('fk_notification_deliveries_notification_id_notifications'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_notification_deliveries')),
    sa.UniqueConstraint('notification_id', 'channel', name=op.f('uq_notification_deliveries_notification_id_channel'))
    )
    op.create_index('ix_notification_deliveries_pending', 'notification_deliveries', ['created_at'], unique=False, postgresql_where=sa.text("status = 'pending'"))
    op.create_table('review_cards',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('due_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('interval_days', sa.Float(), nullable=False),
    sa.Column('ease', sa.Float(), nullable=False),
    sa.Column('reps', sa.Integer(), nullable=False),
    sa.Column('lapses', sa.Integer(), nullable=False),
    sa.Column('last_reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['review_questions.id'], name=op.f('fk_review_cards_question_id_review_questions'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_review_cards_student_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('student_id', 'question_id', name=op.f('pk_review_cards'))
    )
    op.create_index('ix_review_cards_due', 'review_cards', ['student_id', 'due_at'], unique=False)
    op.create_table('student_task_status',
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('tries', sa.Integer(), nullable=False),
    sa.Column('best_score', sa.Integer(), nullable=False),
    sa.Column('is_solved', sa.Boolean(), nullable=False),
    sa.Column('first_solved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_answer_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_student_task_status_student_id_users'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_student_task_status_task_id_tasks'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('student_id', 'task_id', name=op.f('pk_student_task_status'))
    )
    op.create_index(op.f('ix_student_task_status_task_id'), 'student_task_status', ['task_id'], unique=False)
    op.create_table('task_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('kind', sa.Enum('image', 'attachment', name='file_kind', native_enum=False, create_constraint=True, length=32), nullable=False),
    sa.Column('storage_key', sa.String(length=500), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_task_files_task_id_tasks'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_task_files'))
    )
    op.create_index(op.f('ix_task_files_task_id'), 'task_files', ['task_id'], unique=False)
    op.create_table('task_set_items',
    sa.Column('set_id', sa.Integer(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('max_score', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['set_id'], ['task_sets.id'], name=op.f('fk_task_set_items_set_id_task_sets'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_task_set_items_task_id_tasks'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('set_id', 'position', name=op.f('pk_task_set_items')),
    sa.UniqueConstraint('set_id', 'task_id', name=op.f('uq_task_set_items_set_id_task_id'))
    )
    op.create_index(op.f('ix_task_set_items_task_id'), 'task_set_items', ['task_id'], unique=False)
    op.create_table('task_set_stats',
    sa.Column('set_id', sa.Integer(), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=False),
    sa.Column('finished_students', sa.Integer(), nullable=False),
    sa.Column('avg_percent', sa.Float(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['set_id'], ['task_sets.id'], name=op.f('fk_task_set_stats_set_id_task_sets'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('set_id', name=op.f('pk_task_set_stats'))
    )
    op.create_table('task_sources',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['sources.id'], name=op.f('fk_task_sources_source_id_sources'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_task_sources_task_id_tasks'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('task_id', 'source_id', name=op.f('pk_task_sources'))
    )
    op.create_index(op.f('ix_task_sources_source_id'), 'task_sources', ['source_id'], unique=False)
    op.create_table('task_stats',
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('answered', sa.Integer(), nullable=False),
    sa.Column('correct', sa.Integer(), nullable=False),
    sa.Column('solved_students', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_task_stats_task_id_tasks'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('task_id', name=op.f('pk_task_stats'))
    )
    op.create_table('student_assignments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('assignment_id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('deadline_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], name=op.f('fk_student_assignments_assignment_id_assignments'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_student_assignments_student_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_student_assignments')),
    sa.UniqueConstraint('assignment_id', 'student_id', name=op.f('uq_student_assignments_assignment_id_student_id'))
    )
    op.create_index('ix_student_assignments_pending', 'student_assignments', ['deadline_at'], unique=False, postgresql_where=sa.text('submitted_at IS NULL'))
    op.create_index(op.f('ix_student_assignments_student_id'), 'student_assignments', ['student_id'], unique=False)
    op.create_table('attempts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('set_id', sa.Integer(), nullable=False),
    sa.Column('student_assignment_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('in_progress', 'checking', 'graded', 'abandoned', name='attempt_status', native_enum=False, create_constraint=True, length=32), server_default='in_progress', nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('time_spent_sec', sa.Integer(), server_default='0', nullable=False),
    sa.Column('current_position', sa.Integer(), server_default='0', nullable=False),
    sa.Column('primary_score', sa.Integer(), nullable=True),
    sa.Column('secondary_score', sa.Integer(), nullable=True),
    sa.Column('max_score', sa.Integer(), nullable=True),
    sa.Column('is_late', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('is_rated', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.ForeignKeyConstraint(['set_id'], ['task_sets.id'], name=op.f('fk_attempts_set_id_task_sets'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['student_assignment_id'], ['student_assignments.id'], name=op.f('fk_attempts_student_assignment_id_student_assignments'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_attempts_student_id_users'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_attempts'))
    )
    op.create_index('ix_attempts_expires', 'attempts', ['expires_at'], unique=False, postgresql_where=sa.text("status = 'in_progress'"))
    op.create_index(op.f('ix_attempts_set_id'), 'attempts', ['set_id'], unique=False)
    op.create_index('ix_attempts_student_started', 'attempts', ['student_id', 'started_at'], unique=False)
    op.create_index('uq_attempts_in_progress', 'attempts', ['student_id', 'set_id'], unique=True, postgresql_where=sa.text("status = 'in_progress'"))
    op.create_index('uq_attempts_student_assignment', 'attempts', ['student_assignment_id'], unique=True, postgresql_where=sa.text("student_assignment_id IS NOT NULL AND status <> 'abandoned'"))
    op.create_table('answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('attempt_id', sa.Integer(), nullable=True),
    sa.Column('answer_raw', sa.Text(), nullable=False),
    sa.Column('max_score', sa.Integer(), nullable=False),
    sa.Column('is_correct', sa.Boolean(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('needs_review', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('checked_by', sa.Integer(), nullable=True),
    sa.Column('checked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reviewer_comment', sa.Text(), nullable=True),
    sa.Column('time_spent_sec', sa.Integer(), nullable=True),
    sa.Column('answered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('score IS NULL OR score BETWEEN 0 AND max_score', name=op.f('ck_answers_score')),
    sa.ForeignKeyConstraint(['attempt_id'], ['attempts.id'], name=op.f('fk_answers_attempt_id_attempts'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['checked_by'], ['users.id'], name=op.f('fk_answers_checked_by_users'), ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], name=op.f('fk_answers_student_id_users'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name=op.f('fk_answers_task_id_tasks'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_answers')),
    sa.UniqueConstraint('attempt_id', 'task_id', name=op.f('uq_answers_attempt_id_task_id'))
    )
    op.create_index('ix_answers_review_queue', 'answers', ['answered_at'], unique=False, postgresql_where=sa.text('needs_review'))
    op.create_index('ix_answers_student_task', 'answers', ['student_id', 'task_id'], unique=False)
    op.create_index(op.f('ix_answers_task_id'), 'answers', ['task_id'], unique=False)
    op.create_table('answer_files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('answer_id', sa.Integer(), nullable=False),
    sa.Column('storage_key', sa.String(length=500), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['answer_id'], ['answers.id'], name=op.f('fk_answer_files_answer_id_answers'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_answer_files'))
    )
    op.create_index(op.f('ix_answer_files_answer_id'), 'answer_files', ['answer_id'], unique=False)


def _drop_new_schema() -> None:
    op.drop_index(op.f('ix_answer_files_answer_id'), table_name='answer_files')
    op.drop_table('answer_files')
    op.drop_index(op.f('ix_answers_task_id'), table_name='answers')
    op.drop_index('ix_answers_student_task', table_name='answers')
    op.drop_index('ix_answers_review_queue', table_name='answers', postgresql_where=sa.text('needs_review'))
    op.drop_table('answers')
    op.drop_index('uq_attempts_student_assignment', table_name='attempts', postgresql_where=sa.text("student_assignment_id IS NOT NULL AND status <> 'abandoned'"))
    op.drop_index('uq_attempts_in_progress', table_name='attempts', postgresql_where=sa.text("status = 'in_progress'"))
    op.drop_index('ix_attempts_student_started', table_name='attempts')
    op.drop_index(op.f('ix_attempts_set_id'), table_name='attempts')
    op.drop_index('ix_attempts_expires', table_name='attempts', postgresql_where=sa.text("status = 'in_progress'"))
    op.drop_table('attempts')
    op.drop_index(op.f('ix_student_assignments_student_id'), table_name='student_assignments')
    op.drop_index('ix_student_assignments_pending', table_name='student_assignments', postgresql_where=sa.text('submitted_at IS NULL'))
    op.drop_table('student_assignments')
    op.drop_table('task_stats')
    op.drop_index(op.f('ix_task_sources_source_id'), table_name='task_sources')
    op.drop_table('task_sources')
    op.drop_table('task_set_stats')
    op.drop_index(op.f('ix_task_set_items_task_id'), table_name='task_set_items')
    op.drop_table('task_set_items')
    op.drop_index(op.f('ix_task_files_task_id'), table_name='task_files')
    op.drop_table('task_files')
    op.drop_index(op.f('ix_student_task_status_task_id'), table_name='student_task_status')
    op.drop_table('student_task_status')
    op.drop_index('ix_review_cards_due', table_name='review_cards')
    op.drop_table('review_cards')
    op.drop_index('ix_notification_deliveries_pending', table_name='notification_deliveries', postgresql_where=sa.text("status = 'pending'"))
    op.drop_table('notification_deliveries')
    op.drop_index(op.f('ix_assignments_set_id'), table_name='assignments')
    op.drop_table('assignments')
    op.drop_index(op.f('ix_tasks_topic_id'), table_name='tasks')
    op.drop_index('ix_tasks_subject_number', table_name='tasks')
    op.drop_table('tasks')
    op.drop_index('ix_task_sets_catalog', table_name='task_sets', postgresql_where=sa.text('is_public AND archived_at IS NULL'))
    op.drop_table('task_sets')
    op.drop_table('student_topic_stats')
    op.drop_table('student_subjects')
    op.drop_table('student_profiles')
    op.drop_table('student_daily_activity')
    op.drop_table('student_achievements')
    op.drop_table('review_questions')
    op.drop_index(op.f('ix_parent_students_student_id'), table_name='parent_students')
    op.drop_table('parent_students')
    op.drop_index('ix_notifications_user_created', table_name='notifications')
    op.drop_index('ix_notifications_unread', table_name='notifications', postgresql_where=sa.text('read_at IS NULL'))
    op.drop_table('notifications')
    op.drop_table('notification_settings')
    op.drop_table('lesson_progress')
    op.drop_index(op.f('ix_group_members_student_id'), table_name='group_members')
    op.drop_table('group_members')
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_table('users')
    op.drop_index('ix_topics_subject_number', table_name='topics')
    op.drop_index(op.f('ix_topics_parent_id'), table_name='topics')
    op.drop_table('topics')
    op.drop_table('sources')
    op.drop_table('shared_texts')
    op.drop_table('score_scales')
    op.drop_index(op.f('ix_lessons_topic_code'), table_name='lessons')
    op.drop_table('lessons')
    op.drop_table('groups')
    op.drop_table('exam_numbers')
    op.drop_table('achievements')


def _seed_reference_data() -> None:
    exam_numbers = sa.table(
        'exam_numbers',
        sa.column('subject'), sa.column('number'), sa.column('part'),
        sa.column('max_score'), sa.column('answer_type'), sa.column('title'),
    )
    op.bulk_insert(exam_numbers, [
        {'subject': 'math', 'number': n, 'part': part, 'max_score': score,
         'answer_type': 'short' if part == 1 else 'detailed', 'title': title}
        for n, part, score, title in MATH_NUMBERS
    ])

    score_scales = sa.table(
        'score_scales', sa.column('subject'), sa.column('year'), sa.column('primary_score'), sa.column('secondary_score'),
    )
    op.bulk_insert(score_scales, [
        {'subject': 'math', 'year': 2025, 'primary_score': p, 'secondary_score': s}
        for p, s in enumerate(MATH_SCALE_2025)
    ])

    achievements = sa.table('achievements', sa.column('code'), sa.column('title'), sa.column('description'))
    op.bulk_insert(achievements, [{'code': c, 'title': t, 'description': d} for c, t, d in ACHIEVEMENTS])


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    if bind.execute(sa.text('SELECT count(*) FROM tasks')).scalar():
        raise RuntimeError('В tasks есть данные: старая схема заданий автоматически не переносится — '
                           'очистите таблицу или допишите перенос в эту миграцию')

    op.drop_table('tasks')
    postgresql.ENUM(name='subjectenum').drop(bind, checkfirst=True)

    _create_new_schema()

    # Ученики — с прежними id, чтобы выданные токены продолжали работать
    op.execute("""
        INSERT INTO users (id, role, first_name, last_name, phone_number, image_url, created_at)
        SELECT id, 'student', first_name, last_name, phone_number, image_url, created_at FROM students
    """)
    op.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), coalesce(max(id), 0) + 1, false) FROM users")
    # Родители — с новыми id. Если номер уже занят учеником, родитель не переносится
    op.execute("""
        INSERT INTO users (role, first_name, last_name, phone_number, created_at)
        SELECT 'parent', first_name, last_name, phone_number, created_at FROM parents
        ON CONFLICT (phone_number) DO NOTHING
    """)
    op.execute('INSERT INTO student_profiles (user_id) SELECT id FROM students')
    op.execute("""
        INSERT INTO parent_students (parent_id, student_id)
        SELECT u.id, s.id
        FROM students s
        JOIN parents p ON p.id = s.parent_id
        JOIN users u ON u.phone_number = p.phone_number AND u.role = 'parent'
    """)

    op.drop_table('students')
    op.drop_table('parents')
    op.drop_table('curators')
    op.drop_table('psychologists')

    _seed_reference_data()


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table('curators',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('middle_name', sa.String(length=100), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('tg_username', sa.String(length=100), nullable=False),
    sa.Column('university', sa.String(length=500), nullable=False),
    sa.Column('direction', sa.String(length=500), nullable=False),
    sa.Column('course_number', sa.Integer(), nullable=False),
    sa.Column('math_score', sa.Integer(), nullable=False),
    sa.Column('russ_score', sa.Integer(), nullable=False),
    sa.Column('phys_score', sa.Integer(), nullable=True),
    sa.Column('inf_score', sa.Integer(), nullable=True),
    sa.Column('student_ticket', sa.Integer(), nullable=True),
    sa.Column('role', sa.String(length=50), server_default=sa.text("'curator'"), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='curators_pkey')
    )
    op.create_index('ix_curators_phone_number', 'curators', ['phone_number'], unique=True)
    op.create_table('psychologists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=False),
    sa.Column('middle_name', sa.String(length=100), nullable=False),
    sa.Column('profession', sa.String(length=100), nullable=False),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('tg_username', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('education', sa.String(length=100), nullable=False),
    sa.Column('exp_number_years', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='psychologists_pkey')
    )
    op.create_index('ix_psychologists_phone_number', 'psychologists', ['phone_number'], unique=True)
    op.create_table('parents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name='parents_pkey')
    )
    op.create_index('ix_parents_phone_number', 'parents', ['phone_number'], unique=True)
    op.create_table('students',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('phone_number', sa.String(length=20), nullable=False),
    sa.Column('curator_id', sa.Integer(), nullable=True),
    sa.Column('psychologist_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['curator_id'], ['curators.id'], name='students_curator_id_fkey'),
    sa.ForeignKeyConstraint(['parent_id'], ['parents.id'], name='students_parent_id_fkey'),
    sa.ForeignKeyConstraint(['psychologist_id'], ['psychologists.id'], name='students_psychologist_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='students_pkey')
    )
    op.create_index('ix_students_phone_number', 'students', ['phone_number'], unique=True)

    # Обратный перенос. Преподаватели и админы теряются — в старой схеме для них нет таблиц
    op.execute("""
        INSERT INTO parents (first_name, last_name, phone_number, created_at)
        SELECT first_name, last_name, phone_number, created_at FROM users WHERE role = 'parent'
    """)
    op.execute("""
        INSERT INTO students (id, first_name, last_name, phone_number, image_url, created_at, parent_id)
        SELECT u.id, u.first_name, u.last_name, u.phone_number, u.image_url, u.created_at,
               (SELECT p.id
                FROM parent_students ps
                JOIN users pu ON pu.id = ps.parent_id
                JOIN parents p ON p.phone_number = pu.phone_number
                WHERE ps.student_id = u.id
                ORDER BY p.id LIMIT 1)
        FROM users u WHERE u.role = 'student'
    """)
    op.execute("SELECT setval(pg_get_serial_sequence('students', 'id'), coalesce(max(id), 0) + 1, false) FROM students")

    _drop_new_schema()

    subject_enum = postgresql.ENUM('math', 'physics', 'russian', 'informatics', name='subjectenum')
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
    sa.ForeignKeyConstraint(['creator_id'], ['curators.id'], name='tasks_creator_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='tasks_pkey')
    )
    op.create_index('ix_tasks_subject', 'tasks', ['subject'], unique=False)
    op.create_index('ix_tasks_topic', 'tasks', ['topic'], unique=False)
    op.create_index('ix_tasks_source', 'tasks', ['source'], unique=False)
    op.create_index('ix_tasks_sub_topic', 'tasks', ['sub_topic'], unique=False)
