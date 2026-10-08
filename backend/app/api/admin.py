"""Кабинет преподавателя: проверка второй части, наборы, назначения, группы"""
from datetime import datetime, timezone

from fastapi import APIRouter, Query, status
from sqlalchemy import delete, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.dependencies import StaffDep
from app.db.database import SessionDep
from app.db.enums import AttemptStatus, Subject, TaskSetKind, UserRole
from app.db.models import (
    AnswerFileModel, AnswerModel, AssignmentModel, AttemptModel, GroupMemberModel, GroupModel, ParentStudentModel,
    StudentAssignmentModel, TaskModel, TaskSetItemModel, TaskSetModel, UserModel,
)
from app.repositories.tasks import in_topic, reveal, tasks_with_details, to_public
from app.schemas.admin_schemas import (
    AssignmentCreate, AssignmentOut, AssignmentStudentProgress, DeadlineUpdate, GradeRequest, GroupCreate,
    GroupMembersUpdate, GroupOut, ParentLinkCreate, ReviewItem, StaffTaskOut, TaskSetCreate, TaskSetItemsUpdate,
    TaskSetOut, TaskSetUpdate,
)
from app.schemas.task_schemas import FileOut
from app.schemas.user_schemas import UserOut
from app.services import assignments as assignments_service
from app.services import attempts as attempts_service
from app.services import task_sets as task_sets_service
from app.services.errors import NotFoundError, ServiceError
from app.services.storage import public_url

router = APIRouter(prefix='/admin', tags=['Преподаватель'])


# --------------------------------- задания ----------------------------------

@router.get('/tasks', response_model=list[StaffTaskOut], summary='Поиск заданий для наборов')
async def search_tasks(
        session: SessionDep,
        staff: StaffDep,
        subject: Subject = Subject.math,
        task_number: int | None = None,
        topic_id: int | None = None,
        q: str | None = Query(default=None, description='Подстрока в условии'),
        include_inactive: bool = False,
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
):
    query = tasks_with_details().where(TaskModel.subject == subject)
    if not include_inactive:
        query = query.where(TaskModel.is_active)
    if task_number is not None:
        query = query.where(TaskModel.task_number == task_number)
    if topic_id is not None:
        query = query.where(in_topic(topic_id))
    if q:
        query = query.where(TaskModel.condition.ilike(f'%{q}%'))
    tasks = (await session.execute(query.order_by(TaskModel.task_number, TaskModel.id).limit(limit).offset(offset))).scalars().all()
    public = await to_public(session, list(tasks))
    return [StaffTaskOut(task=p, reveal=reveal(t), is_active=t.is_active) for t, p in zip(tasks, public)]


# ------------------------------ проверка ответов ------------------------------

@router.get('/review-queue', response_model=list[ReviewItem], summary='Ответы, которые ждут проверки')
async def review_queue(
        session: SessionDep,
        staff: StaffDep,
        subject: Subject | None = None,
        limit: int = Query(default=20, ge=1, le=100),
):
    """Старые сверху. Ответы незаконченных попыток сюда не попадают — needs_review ставится при сдаче"""
    query = (
        select(AnswerModel, UserModel, TaskSetModel.title)
        .join(UserModel, UserModel.id == AnswerModel.student_id)
        .join(TaskModel, TaskModel.id == AnswerModel.task_id)
        .outerjoin(AttemptModel, AttemptModel.id == AnswerModel.attempt_id)
        .outerjoin(TaskSetModel, TaskSetModel.id == AttemptModel.set_id)
        .where(AnswerModel.needs_review)
        .order_by(AnswerModel.answered_at)
        .limit(limit)
    )
    if subject is not None:
        query = query.where(TaskModel.subject == subject)
    rows = (await session.execute(query)).all()
    if not rows:
        return []

    tasks = {t.id: t for t in (await session.execute(
        tasks_with_details().where(TaskModel.id.in_({a.task_id for a, _, _ in rows}))
    )).scalars().all()}
    public = {p.id: p for p in await to_public(session, list(tasks.values()))}
    files: dict[int, list[FileOut]] = {}
    for f in (await session.execute(
        select(AnswerFileModel).where(AnswerFileModel.answer_id.in_([a.id for a, _, _ in rows])).order_by(AnswerFileModel.id)
    )).scalars():
        files.setdefault(f.answer_id, []).append(FileOut(filename=f.filename, url=public_url(f.storage_key)))

    return [
        ReviewItem(
            answer_id=a.id, student=UserOut.from_user(student), task=public[a.task_id], reveal=reveal(tasks[a.task_id]),
            answer=a.answer_raw, files=files.get(a.id, []), max_score=a.max_score, answered_at=a.answered_at,
            attempt_id=a.attempt_id, set_title=title,
        )
        for a, student, title in rows
    ]


@router.post('/answers/{answer_id}/grade', status_code=status.HTTP_204_NO_CONTENT, summary='Оценить ответ')
async def grade(answer_id: int, data: GradeRequest, session: SessionDep, staff: StaffDep):
    """Можно и перепроверить уже оценённый ответ — статистика пересчитается"""
    answer = await session.get(AnswerModel, answer_id)
    if answer is None:
        raise NotFoundError('Ответ не найден')
    if answer.attempt_id is not None:
        attempt = await session.get(AttemptModel, answer.attempt_id)
        if attempt.status == AttemptStatus.in_progress:
            raise ServiceError('Попытка ещё не сдана')
    await attempts_service.grade_answer(session, answer, data.score, staff.id, data.comment)
    await session.commit()


# --------------------------------- наборы -----------------------------------

async def _set_out(session, task_set: TaskSetModel) -> TaskSetOut:
    task_ids = (await session.execute(
        select(TaskSetItemModel.task_id).where(TaskSetItemModel.set_id == task_set.id).order_by(TaskSetItemModel.position)
    )).scalars().all()
    return TaskSetOut(
        id=task_set.id, kind=task_set.kind, subject=task_set.subject, title=task_set.title,
        description=task_set.description, publisher=task_set.publisher, difficulty=task_set.difficulty,
        time_limit_sec=task_set.time_limit_sec, is_public=task_set.is_public, is_standard=task_set.is_standard,
        task_ids=list(task_ids), created_at=task_set.created_at, published_at=task_set.published_at,
        archived_at=task_set.archived_at, has_attempts=await task_sets_service.has_attempts(session, task_set.id),
    )


async def _get_set(session, set_id: int) -> TaskSetModel:
    task_set = await session.get(TaskSetModel, set_id)
    if task_set is None:
        raise NotFoundError('Набор не найден')
    return task_set


@router.get('/task-sets', response_model=list[TaskSetOut], summary='Наборы')
async def list_sets(
        session: SessionDep,
        staff: StaffDep,
        subject: Subject | None = None,
        kind: TaskSetKind | None = None,
        archived: bool = False,
):
    query = select(TaskSetModel).where(
        TaskSetModel.archived_at.is_not(None) if archived else TaskSetModel.archived_at.is_(None)
    )
    if subject is not None:
        query = query.where(TaskSetModel.subject == subject)
    if kind is not None:
        query = query.where(TaskSetModel.kind == kind)
    sets = (await session.execute(query.order_by(TaskSetModel.created_at.desc()))).scalars().all()
    return [await _set_out(session, s) for s in sets]


@router.post('/task-sets', response_model=TaskSetOut, status_code=status.HTTP_201_CREATED, summary='Создать набор')
async def create_set(data: TaskSetCreate, session: SessionDep, staff: StaffDep):
    fields = data.model_dump(exclude={'kind', 'subject', 'title', 'task_ids'})
    if data.is_public:
        fields['published_at'] = datetime.now(timezone.utc)
    task_set = await task_sets_service.create_task_set(
        session, data.kind, data.subject, data.title, data.task_ids, created_by=staff.id, **fields,
    )
    await session.commit()
    return await _set_out(session, task_set)


@router.patch('/task-sets/{set_id}', response_model=TaskSetOut, summary='Изменить свойства, опубликовать, архивировать')
async def update_set(set_id: int, data: TaskSetUpdate, session: SessionDep, staff: StaffDep):
    task_set = await _get_set(session, set_id)
    changes = data.model_dump(exclude_unset=True)
    archived = changes.pop('archived', None)
    if 'time_limit_sec' in changes and await task_sets_service.has_attempts(session, set_id):
        raise ServiceError('Время нельзя менять, пока по набору есть попытки: создайте копию')
    for name, value in changes.items():
        setattr(task_set, name, value)
    if data.is_public and task_set.published_at is None:
        task_set.published_at = datetime.now(timezone.utc)
    if archived is not None:
        task_set.archived_at = datetime.now(timezone.utc) if archived else None
    await session.commit()
    return await _set_out(session, task_set)


@router.put('/task-sets/{set_id}/items', response_model=TaskSetOut, summary='Новый состав набора')
async def replace_items(set_id: int, data: TaskSetItemsUpdate, session: SessionDep, staff: StaffDep):
    task_set = await task_sets_service.replace_items(session, set_id, [(i.task_id, i.max_score) for i in data.items])
    await session.commit()
    return await _set_out(session, task_set)


@router.post('/task-sets/{set_id}/copy', response_model=TaskSetOut, status_code=status.HTTP_201_CREATED,
             summary='Копия набора — чтобы править набор с попытками')
async def copy_set(set_id: int, session: SessionDep, staff: StaffDep):
    copy = await task_sets_service.copy_task_set(session, set_id, created_by=staff.id)
    await session.commit()
    return await _set_out(session, copy)


# -------------------------------- назначения --------------------------------

async def _assignment_out(session, assignment: AssignmentModel) -> AssignmentOut:
    task_set = await session.get(TaskSetModel, assignment.set_id)
    rows = (await session.execute(
        select(StudentAssignmentModel, UserModel)
        .join(UserModel, UserModel.id == StudentAssignmentModel.student_id)
        .where(StudentAssignmentModel.assignment_id == assignment.id)
        .order_by(UserModel.last_name, UserModel.first_name)
    )).all()
    attempts = {a.student_assignment_id: a for a in (await session.execute(
        select(AttemptModel).where(
            AttemptModel.student_assignment_id.in_([sa.id for sa, _ in rows]),
            AttemptModel.status != AttemptStatus.abandoned,
        )
    )).scalars()}
    now = datetime.now(timezone.utc)
    students = []
    for sa, student in rows:
        attempt = attempts.get(sa.id)
        submitted = attempt is not None and attempt.submitted_at is not None
        students.append(AssignmentStudentProgress(
            student_assignment_id=sa.id, student=UserOut.from_user(student), deadline_at=sa.deadline_at,
            status=assignments_service.homework_status(sa, now),
            attempt_status=attempt.status if attempt else None,
            primary_score=attempt.primary_score if submitted else None,
            max_score=attempt.max_score if attempt else None,
            submitted_at=sa.submitted_at, is_late=attempt.is_late if attempt else False,
        ))
    return AssignmentOut(
        id=assignment.id, set_id=task_set.id, set_title=task_set.title, group_id=assignment.group_id,
        deadline_at=assignment.deadline_at, note=assignment.note, created_at=assignment.created_at, students=students,
    )


@router.post('/assignments', response_model=AssignmentOut, status_code=status.HTTP_201_CREATED, summary='Задать ДЗ')
async def create_assignment(data: AssignmentCreate, session: SessionDep, staff: StaffDep):
    assignment = await assignments_service.assign_set(
        session, data.set_id, staff.id, deadline_at=data.deadline_at, group_id=data.group_id,
        student_ids=data.student_ids, note=data.note,
    )
    await session.commit()
    return await _assignment_out(session, assignment)


@router.get('/assignments', response_model=list[AssignmentOut], summary='Назначенные ДЗ с прогрессом учеников')
async def list_assignments(
        session: SessionDep,
        staff: StaffDep,
        set_id: int | None = None,
        group_id: int | None = None,
        limit: int = Query(default=20, ge=1, le=100),
):
    query = select(AssignmentModel).order_by(AssignmentModel.created_at.desc()).limit(limit)
    if set_id is not None:
        query = query.where(AssignmentModel.set_id == set_id)
    if group_id is not None:
        query = query.where(AssignmentModel.group_id == group_id)
    return [await _assignment_out(session, a) for a in (await session.execute(query)).scalars().all()]


@router.patch('/student-assignments/{student_assignment_id}', status_code=status.HTTP_204_NO_CONTENT,
              summary='Продлить срок одному ученику')
async def extend_deadline(student_assignment_id: int, data: DeadlineUpdate, session: SessionDep, staff: StaffDep):
    await assignments_service.extend_deadline(session, student_assignment_id, data.deadline_at)
    await session.commit()


# ---------------------------------- группы ----------------------------------

async def _group_out(session, group: GroupModel) -> GroupOut:
    ids = (await session.execute(
        select(GroupMemberModel.student_id).where(GroupMemberModel.group_id == group.id).order_by(GroupMemberModel.student_id)
    )).scalars().all()
    return GroupOut(id=group.id, name=group.name, subject=group.subject, student_ids=list(ids))


@router.get('/groups', response_model=list[GroupOut], summary='Группы')
async def list_groups(session: SessionDep, staff: StaffDep):
    groups = (await session.execute(
        select(GroupModel).where(GroupModel.archived_at.is_(None)).order_by(GroupModel.name)
    )).scalars().all()
    return [await _group_out(session, g) for g in groups]


@router.post('/groups', response_model=GroupOut, status_code=status.HTTP_201_CREATED, summary='Создать группу')
async def create_group(data: GroupCreate, session: SessionDep, staff: StaffDep):
    group = GroupModel(name=data.name, subject=data.subject)
    session.add(group)
    await session.commit()
    return await _group_out(session, group)


@router.put('/groups/{group_id}/members', response_model=GroupOut, summary='Состав группы')
async def set_members(group_id: int, data: GroupMembersUpdate, session: SessionDep, staff: StaffDep):
    group = await session.get(GroupModel, group_id)
    if group is None:
        raise NotFoundError('Группа не найдена')
    students = set((await session.execute(
        select(UserModel.id).where(UserModel.id.in_(data.student_ids), UserModel.role == UserRole.student)
    )).scalars().all())
    if missing := sorted(set(data.student_ids) - students):
        raise ServiceError(f'Это не ученики: {missing}')
    await session.execute(delete(GroupMemberModel).where(GroupMemberModel.group_id == group_id))
    session.add_all(GroupMemberModel(group_id=group_id, student_id=s) for s in sorted(students))
    await session.commit()
    return await _group_out(session, group)


# -------------------------------- пользователи -------------------------------

@router.get('/students', response_model=list[UserOut], summary='Поиск учеников')
async def search_students(
        session: SessionDep,
        staff: StaffDep,
        q: str | None = Query(default=None, description='Имя, фамилия или телефон'),
        limit: int = Query(default=50, ge=1, le=200),
):
    query = select(UserModel).where(UserModel.role == UserRole.student, UserModel.is_active)
    if q:
        pattern = f'%{q}%'
        query = query.where(or_(
            UserModel.first_name.ilike(pattern), UserModel.last_name.ilike(pattern), UserModel.phone_number.ilike(pattern),
        ))
    rows = (await session.execute(query.order_by(UserModel.last_name, UserModel.first_name).limit(limit))).scalars()
    return [UserOut.from_user(u) for u in rows]


@router.post('/parent-links', status_code=status.HTTP_204_NO_CONTENT, summary='Привязать родителя к ученику')
async def link_parent(data: ParentLinkCreate, session: SessionDep, staff: StaffDep):
    parent = await session.get(UserModel, data.parent_id)
    student = await session.get(UserModel, data.student_id)
    if parent is None or parent.role != UserRole.parent:
        raise NotFoundError('Родитель не найден')
    if student is None or student.role != UserRole.student:
        raise NotFoundError('Ученик не найден')
    await session.execute(
        pg_insert(ParentStudentModel).values(parent_id=parent.id, student_id=student.id).on_conflict_do_nothing()
    )
    await session.commit()


@router.delete('/parent-links/{parent_id}/{student_id}', status_code=status.HTTP_204_NO_CONTENT,
               summary='Отвязать родителя')
async def unlink_parent(parent_id: int, student_id: int, session: SessionDep, staff: StaffDep):
    await session.execute(delete(ParentStudentModel).where(
        ParentStudentModel.parent_id == parent_id, ParentStudentModel.student_id == student_id,
    ))
    await session.commit()
