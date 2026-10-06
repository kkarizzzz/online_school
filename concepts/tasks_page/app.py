"""
Концепт страницы «Нарешка»: бесконечная лента заданий по выбранной теме или «торнадо» по всем темам.
FastAPI + SQLite, без связи с основным проектом.

Запуск (из корня репозитория):
    backend/.venv/Scripts/python -m uvicorn app:app --app-dir concepts/tasks_page --port 8100
и открыть http://localhost:8100
"""
import random
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from checker import check_answer
from db import BASE_DIR, DB_PATH, STORAGE_DIR, engine
from models import AnswerType, Attempt, FileKind, SubjectEnum, Task, Topic


# Концепт работает только с математикой; схема и API при этом не привязаны к предмету
SUBJECT = SubjectEnum.math

FONTS_DIR = BASE_DIR.parent.parent / 'frontend' / 'public' / 'fonts'
LOGO_PATH = BASE_DIR.parent.parent / 'frontend' / 'src' / 'shared' / 'assets' / 'icons' / 'logo.svg'


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not DB_PATH.exists():
        from seed import seed
        seed()
    yield


app = FastAPI(title='Концепт: нарешка по математике', lifespan=lifespan)


def get_session():
    with Session(engine) as session:
        yield session


def storage_url(key: str) -> str:
    # На проде здесь будет публичный или подписанный URL из S3
    return f'/storage/{key}'


def resolve_storage_links(markdown: str | None) -> str | None:
    """storage://figures/x.svg -> /storage/figures/x.svg"""
    return markdown.replace('storage://', '/storage/') if markdown else markdown


# ------------------------------- схемы ответа -------------------------------

class FileOut(BaseModel):
    filename: str
    url: str


class TaskPublic(BaseModel):
    """То, что видит ученик ДО ответа: без answer, solution и критериев"""
    id: int
    task_number: int
    part: int
    difficulty: int
    max_score: int
    answer_type: AnswerType
    topic_id: int | None  # тема верхнего уровня («Уравнения»), по ней идёт лента
    topic: str | None
    subtopic: str | None
    sources: list[str]
    shared_text: str | None
    condition: str
    attachments: list[FileOut]
    similar_count: int  # сколько ещё заданий из той же подтемы


class TopicOut(BaseModel):
    id: int
    task_number: int
    name: str
    subtopics: list[str]
    task_count: int
    solved_count: int


class TopicsOut(BaseModel):
    topics: list[TopicOut]
    last_topic_id: int | None  # тема последней попытки — её предлагаем продолжить


class SubmitRequest(BaseModel):
    answer: str


class SubmitResult(BaseModel):
    is_correct: bool | None  # None — нужна проверка куратором
    score: int | None
    max_score: int
    correct_answer: str
    solution: str | None
    grade_criteria: str | None


# --------------------------------- запросы ----------------------------------

def active_tasks():
    return (
        select(Task)
        .where(Task.is_active, Task.subject == SUBJECT)
        .options(selectinload(Task.files), selectinload(Task.sources), selectinload(Task.shared_text))
        .order_by(Task.task_number, Task.id)
    )


def root_topic(topic: Topic | None) -> Topic | None:
    return topic.parent if topic and topic.parent else topic


def pick_random(candidates: list[Task], exclude: list[int]) -> Task:
    """Сначала то, чего ещё не было в ленте; когда всё показано — по кругу"""
    fresh = [t for t in candidates if t.id not in exclude]
    return random.choice(fresh or candidates)


def get_task_or_404(session: Session, task_id: int) -> Task:
    task = session.get(Task, task_id)
    if not task or not task.is_active or task.subject != SUBJECT:
        raise HTTPException(status_code=404, detail='Задание не найдено')
    return task


def to_public(session: Session, task: Task) -> TaskPublic:
    topic = task.topic
    root = root_topic(topic)
    similar = session.scalars(
        select(Task.id).where(Task.is_active, Task.topic_id == task.topic_id, Task.id != task.id)
    ).all() if task.topic_id else []

    return TaskPublic(
        id=task.id,
        task_number=task.task_number,
        part=task.part,
        difficulty=task.difficulty,
        max_score=task.max_score,
        answer_type=task.answer_type,
        topic_id=root.id if root else None,
        topic=topic.parent.name if topic and topic.parent else (topic.name if topic else None),
        subtopic=topic.name if topic and topic.parent else None,
        sources=[s.name for s in task.sources],
        shared_text=task.shared_text.content if task.shared_text else None,
        condition=resolve_storage_links(task.condition),
        attachments=[
            FileOut(filename=f.filename, url=storage_url(f.storage_key))
            for f in task.files if f.kind == FileKind.attachment
        ],
        similar_count=len(similar),
    )


# --------------------------------- эндпоинты --------------------------------

@app.get('/api/topics', response_model=TopicsOut, summary='Темы для выбора и последняя тема ученика')
def list_topics(session: Session = Depends(get_session)):
    tasks = session.scalars(active_tasks()).all()
    solved_ids = set(session.scalars(select(Attempt.task_id).where(Attempt.is_correct)).all())
    
    topics: dict[int, TopicOut] = {}
    for task in tasks:
        root = root_topic(task.topic)
        if root is None:
            continue
        item = topics.setdefault(root.id, TopicOut(
            id=root.id, task_number=root.task_number, name=root.name,
            subtopics=[], task_count=0, solved_count=0,
        ))
        item.task_count += 1
        item.solved_count += task.id in solved_ids
        if task.topic is not root and task.topic.name not in item.subtopics:
            item.subtopics.append(task.topic.name)
    
    # В основном проекте — последняя попытка текущего ученика (WHERE student_id = :me)
    last = session.scalars(select(Attempt).order_by(Attempt.id.desc()).limit(1)).first()
    last_root = root_topic(session.get(Task, last.task_id).topic) if last else None
    
    return TopicsOut(
        topics=sorted(topics.values(), key=lambda t: (t.task_number, t.id)),
        last_topic_id=last_root.id if last_root else None,
    )


@app.get('/api/tasks/random', response_model=TaskPublic, summary='Следующее задание ленты')
def random_task(
        topic_id: int | None = Query(default=None, description='Тема; без неё — торнадо по всем темам'),
        exclude: list[int] = Query(default=[], description='Задания, уже показанные в ленте'),
        current_id: int | None = Query(default=None, description='Текущее задание — его не повторяем'),
        session: Session = Depends(get_session),
):
    query = active_tasks()
    if topic_id is not None:
        query = query.join(Task.topic).where(or_(Topic.id == topic_id, Topic.parent_id == topic_id))
    if current_id is not None:
        query = query.where(Task.id != current_id)
    
    candidates = session.scalars(query).all()
    if not candidates:
        raise HTTPException(status_code=404, detail='В этой теме нет заданий')
    return to_public(session, pick_random(candidates, exclude))


@app.get('/api/tasks/{task_id}', response_model=TaskPublic)
def get_task(task_id: int, session: Session = Depends(get_session)):
    return to_public(session, get_task_or_404(session, task_id))


@app.get('/api/tasks/{task_id}/similar', response_model=TaskPublic, summary='Похожее задание')
def similar_task(
        task_id: int,
        exclude: list[int] = Query(default=[], description='Задания, уже показанные в ленте'),
        session: Session = Depends(get_session),
):
    """Случайное задание из той же подтемы, кроме текущего"""
    task = get_task_or_404(session, task_id)
    candidates = session.scalars(
        active_tasks().where(Task.topic_id == task.topic_id, Task.id != task.id)
    ).all()
    if not candidates:
        raise HTTPException(status_code=404, detail='Похожих заданий нет')

    return to_public(session, pick_random(candidates, exclude))


@app.post('/api/tasks/{task_id}/submit', response_model=SubmitResult)
def submit_answer(task_id: int, data: SubmitRequest, session: Session = Depends(get_session)):
    task = get_task_or_404(session, task_id)

    is_correct = check_answer(task, data.answer)
    score = None if is_correct is None else (task.max_score if is_correct else 0)

    session.add(Attempt(task_id=task.id, answer=data.answer, is_correct=is_correct, score=score))
    session.commit()

    return SubmitResult(
        is_correct=is_correct,
        score=score,
        max_score=task.max_score,
        correct_answer=task.answer.get('display', ''),
        solution=resolve_storage_links(task.solution),
        grade_criteria=task.grade_criteria,
    )


STORAGE_DIR.mkdir(exist_ok=True)
app.mount('/storage', StaticFiles(directory=STORAGE_DIR), name='storage')
if FONTS_DIR.exists():
    app.mount('/fonts', StaticFiles(directory=FONTS_DIR), name='fonts')


@app.get('/logo.svg', include_in_schema=False)
def logo():
    # Логотип берём прямо из основного фронта, чтобы не дублировать файл
    return FileResponse(LOGO_PATH, media_type='image/svg+xml')


app.mount('/', StaticFiles(directory=BASE_DIR / 'static', html=True), name='static')
