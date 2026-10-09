"""Запросы к банку заданий и сборка заданий для ответа API"""
from dataclasses import dataclass, field

from sqlalchemy import Select, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.enums import FileKind, Subject
from app.db.models import BankMarkModel, StudentTaskStatusModel, TaskModel, TopicModel
from app.schemas.task_schemas import FileOut, TaskPublic, TaskReveal
from app.services.errors import NotFoundError
from app.services.storage import public_url, resolve_links


def tasks_with_details() -> Select:
    """Задания вместе с файлами, источниками и общим текстом — всё, что нужно to_public"""
    return select(TaskModel).options(
        selectinload(TaskModel.files), selectinload(TaskModel.sources), selectinload(TaskModel.shared_text),
    )


def active_tasks(subject: Subject | None = None) -> Select:
    query = tasks_with_details().where(TaskModel.is_active)
    return query.where(TaskModel.subject == subject) if subject else query


def in_topic(topic_id: int):
    """Задания темы и её подтем"""
    subtree = select(TopicModel.id).where(or_(TopicModel.id == topic_id, TopicModel.parent_id == topic_id))
    return TaskModel.topic_id.in_(subtree)


def in_topics(topic_ids: list[int]):
    """Задания любой из тем и их подтем"""
    subtree = select(TopicModel.id).where(or_(TopicModel.id.in_(topic_ids), TopicModel.parent_id.in_(topic_ids)))
    return TaskModel.topic_id.in_(subtree)


async def get_active_task(session: AsyncSession, task_id: int, subject: Subject | None = None) -> TaskModel:
    task = (await session.execute(active_tasks(subject).where(TaskModel.id == task_id))).scalar_one_or_none()
    if task is None:
        raise NotFoundError('Задание не найдено')
    return task


async def random_task(
        session: AsyncSession,
        base: Select,
        exclude: list[int],
) -> TaskModel | None:
    """Случайное задание: сначала то, чего ещё не было в ленте; когда всё показано — по кругу"""
    async def pick(query: Select) -> TaskModel | None:
        return (await session.execute(query.order_by(func.random()).limit(1))).scalar_one_or_none()

    if exclude and (task := await pick(base.where(TaskModel.id.not_in(exclude)))):
        return task
    return await pick(base)


async def topics_map(session: AsyncSession, subjects: set[Subject]) -> dict[int, TopicModel]:
    if not subjects:
        return {}
    rows = await session.execute(select(TopicModel).where(TopicModel.subject.in_(subjects)))
    return {t.id: t for t in rows.scalars()}


def root_topic(topic: TopicModel | None, topics: dict[int, TopicModel]) -> TopicModel | None:
    return topics.get(topic.parent_id, topic) if topic and topic.parent_id else topic


async def to_public(session: AsyncSession, tasks: list[TaskModel]) -> list[TaskPublic]:
    """Задания для ученика. Файлы, источники и общий текст должны быть загружены (active_tasks)"""
    topics = await topics_map(session, {t.subject for t in tasks})
    topic_ids = {t.topic_id for t in tasks if t.topic_id}
    sizes = dict((await session.execute(
        select(TaskModel.topic_id, func.count())
        .where(TaskModel.is_active, TaskModel.topic_id.in_(topic_ids))
        .group_by(TaskModel.topic_id)
    )).all()) if topic_ids else {}

    result = []
    for task in tasks:
        topic = topics.get(task.topic_id)
        root = root_topic(topic, topics)
        result.append(TaskPublic(
            id=task.id,
            task_number=task.task_number,
            part=task.part,
            difficulty=task.difficulty,
            max_score=task.max_score,
            answer_type=task.answer_type,
            topic_id=root.id if root else None,
            topic=root.name if root else None,
            subtopic=topic.name if topic and topic is not root else None,
            sources=[s.name for s in task.sources],
            shared_text=resolve_links(task.shared_text.content) if task.shared_text else None,
            condition=resolve_links(task.condition),
            attachments=[
                FileOut(filename=f.filename, url=public_url(f.storage_key))
                for f in task.files if f.kind == FileKind.attachment
            ],
            similar_count=max(sizes.get(task.topic_id, 0) - 1, 0),
        ))
    return result


def reveal(task: TaskModel) -> TaskReveal:
    return TaskReveal(
        correct_answer=task.answer.get('display') or ', '.join(task.answer.get('accepted', [])),
        solution=resolve_links(task.solution),
        solution_video_url=task.solution_video_url,
        grade_criteria=resolve_links(task.grade_criteria),
    )


@dataclass
class TopicProgress:
    """Тема верхнего уровня: сколько активных заданий в ней и подтемах и сколько решил ученик"""
    topic: TopicModel
    subtopics: list[str] = field(default_factory=list)
    task_count: int = 0
    solved_count: int = 0


def solved_condition(student_id: int, with_marks: bool = False):
    """Задание решено учеником: засчитанный ответ на полный балл, а в банке — ещё и своя отметка"""
    solved = exists().where(
        StudentTaskStatusModel.task_id == TaskModel.id,
        StudentTaskStatusModel.student_id == student_id,
        StudentTaskStatusModel.is_solved,
    )
    if not with_marks:
        return solved
    marked = exists().where(BankMarkModel.task_id == TaskModel.id, BankMarkModel.student_id == student_id)
    return or_(solved, marked)


async def topic_progress(
        session: AsyncSession, subject: Subject, student_id: int, with_marks: bool = False,
) -> list[TopicProgress]:
    """По порядку: номер ЕГЭ, позиция темы. Темы без активных заданий не попадают"""
    topics = await topics_map(session, {subject})
    rows = (await session.execute(
        select(TaskModel.topic_id, func.count(), func.count().filter(solved_condition(student_id, with_marks)))
        .where(TaskModel.is_active, TaskModel.subject == subject, TaskModel.topic_id.is_not(None))
        .group_by(TaskModel.topic_id)
    )).all()

    by_root: dict[int, TopicProgress] = {}
    for topic_id, task_count, solved_count in rows:
        topic = topics[topic_id]
        root = root_topic(topic, topics)
        item = by_root.setdefault(root.id, TopicProgress(topic=root))
        item.task_count += task_count
        item.solved_count += solved_count
        if topic is not root and topic.name not in item.subtopics:
            item.subtopics.append(topic.name)
    return sorted(by_root.values(), key=lambda p: (p.topic.task_number, p.topic.position, p.topic.id))
