"""
Учебное содержимое из app/scripts/content/*.json — бывшие заглушки фронтенда:
банк заданий 1–19, программа курса, конспекты, содержимое уроков, вопросы повторения,
а ещё демо-ДЗ и варианты, собранные из заданий банка.

    python -m app.scripts.import_content

Каждая часть импортируется один раз: если её данные уже есть, она пропускается.
"""
import asyncio
import json
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

from sqlalchemy import exists, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import engine, new_session
from app.db.enums import AnswerType, ReviewQuestionKind, Subject, TaskSetKind, UserRole
from app.db.models import (
    CurriculumModel, ExamNumberModel, LessonModel, ReviewQuestionModel, SourceModel, TaskModel, TaskSetModel,
    TopicModel, UserModel,
)
from app.services.assignments import assign_set
from app.services.task_sets import create_task_set, replace_items

CONTENT = Path(__file__).parent / 'content'
BANK_SOURCE = 'frontend_bank'
LEVELS = {'base': 1, 'medium': 2, 'hard': 3, 'coffin': 4}
EXAM_SECONDS = (3 * 60 + 55) * 60


def load(name: str):
    return json.loads((CONTENT / name).read_text(encoding='utf-8'))


def to_markdown(text: str) -> str:
    """В заглушке перенос строки — одиночный \\n, в Markdown для этого нужен пустой абзац"""
    return text.replace('\n', '\n\n')


async def import_bank(session: AsyncSession) -> None:
    if (await session.execute(select(exists().where(TaskModel.external_source == BANK_SOURCE)))).scalar_one():
        print('банк: уже импортирован')
        return
    source = (await session.execute(select(SourceModel).where(SourceModel.name == 'Банк школы'))).scalar_one_or_none()
    if source is None:
        source = SourceModel(name='Банк школы')
        session.add(source)

    count = 0
    for number in load('bank.json'):
        for position, topic_data in enumerate(number['topics']):
            topic = TopicModel(subject=Subject.math, task_number=number['number'], name=topic_data['name'],
                               position=100 + position)  # после тем из демо-нарешки
            session.add(topic)
            await session.flush()
            for t in topic_data['tasks']:
                task = TaskModel(
                    subject=Subject.math, task_number=number['number'], part=1 if number['number'] <= 12 else 2,
                    difficulty=LEVELS[t['level']], topic_id=topic.id, condition=to_markdown(t['condition']),
                    answer_type=AnswerType.short, answer={'accepted': [str(t['answer'])], 'display': t['display']},
                    solution=to_markdown(t['solution']), external_source=BANK_SOURCE, external_id=t['code'],
                    sources=[source],
                )
                session.add(task)
                await session.flush()
                task.created_at = datetime.combine(date.fromisoformat(t['date']), time(12), timezone.utc)
                count += 1
    print(f'банк: {count} заданий')


async def import_curriculum(session: AsyncSession) -> None:
    curriculum = load('curriculum.json')
    summaries = load('summaries.json')
    contents = load('lesson_content.json')
    await session.execute(
        pg_insert(CurriculumModel).values(subject=Subject.math, data=curriculum)
        .on_conflict_do_update(index_elements=['subject'], set_={'data': curriculum, 'updated_at': func.now()})
    )
    position = 0
    for topic in curriculum['topics']:
        for lesson in topic['lessons']:
            values = dict(
                id=lesson['id'], subject=Subject.math, topic_code=topic['id'], name=lesson['name'], position=position,
                summary=summaries.get(lesson['id']), content=contents.get(lesson['id']),
            )
            await session.execute(
                pg_insert(LessonModel).values(**values)
                .on_conflict_do_update(index_elements=['id'], set_={k: v for k, v in values.items() if k != 'id'})
            )
            position += 1
    print(f'программа: {position} уроков, конспектов {len(summaries)}, наполненных уроков {len(contents)}')


async def import_review(session: AsyncSession) -> None:
    if (await session.execute(select(exists().where(ReviewQuestionModel.subject == Subject.math)))).scalar_one():
        print('повторение: уже импортировано')
        return
    questions = load('review_questions.json')
    session.add_all(
        ReviewQuestionModel(
            subject=Subject.math, kind=ReviewQuestionKind(q['kind']), question=q['q'], options=q['options'],
            explanation=q['explain'], topic_label=q['topic'],
        )
        for q in questions
    )
    print(f'повторение: {len(questions)} вопросов')


async def _bank_tasks(session: AsyncSession) -> dict[int, list[int]]:
    """Номер ЕГЭ → id заданий банка по порядку"""
    rows = (await session.execute(
        select(TaskModel.task_number, TaskModel.id)
        .where(TaskModel.external_source == BANK_SOURCE, TaskModel.is_active)
        .order_by(TaskModel.task_number, TaskModel.id)
    )).all()
    result: dict[int, list[int]] = {}
    for number, task_id in rows:
        result.setdefault(number, []).append(task_id)
    return result


async def import_sets(session: AsyncSession) -> None:
    """Демо-ДЗ (как были в заглушке фронтенда) и каталог вариантов"""
    if (await session.execute(select(exists().where(TaskSetModel.publisher == 'ФИПИ')))).scalar_one():
        print('наборы: уже созданы')
        return
    bank = await _bank_tasks(session)
    used: dict[int, int] = {}

    def take(number: int) -> int:
        tasks = bank[number]
        i = used.get(number, 0)
        used[number] = i + 1
        return tasks[i % len(tasks)]

    now = datetime.now(timezone.utc)
    students = (await session.execute(
        select(UserModel.id).where(UserModel.role == UserRole.student, UserModel.is_active)
    )).scalars().all()
    # Сроки как в заглушке: несколько текущих и одно просроченное
    offsets = [12, 5, 7, 10, 1, -3]
    for hw, days in zip(load('homework.json'), offsets):
        numbers = hw['numbers']
        task_ids = sorted({take(numbers[i % len(numbers)]) for i in range(hw['tasks'])})
        task_set = await create_task_set(
            session, TaskSetKind.homework, Subject.math, hw['title'], task_ids, description=hw['topic'],
        )
        deadline = (now + timedelta(days=days)).replace(hour=20, minute=59, second=0, microsecond=0)
        if students:
            await assign_set(session, task_set.id, None, deadline_at=deadline, student_ids=list(students))

    scores = dict((await session.execute(
        select(ExamNumberModel.number, ExamNumberModel.max_score).where(ExamNumberModel.subject == Subject.math)
    )).all())
    for title, publisher, difficulty, age in [
        ('Пробный вариант ЕГЭ №14', 'СтатГрад', 3, 2),
        ('Тренировочный вариант №09', 'Авторский', 2, 20),
        ('Досрочный ЕГЭ 2024', 'ФИПИ', 3, 160),
    ]:
        task_ids = [take(n) for n in range(1, 20)]
        task_set = await create_task_set(
            session, TaskSetKind.variant, Subject.math, title, task_ids,
            description='Полный вариант: 19 заданий, как на ЕГЭ', publisher=publisher, difficulty=difficulty,
            time_limit_sec=EXAM_SECONDS, is_public=True, is_standard=True, published_at=now - timedelta(days=age),
        )
        # Баллы — как на экзамене: №13 — 2, №18 — 4 и т.д.
        await replace_items(session, task_set.id, [(t, scores[n]) for n, t in zip(range(1, 20), task_ids)])

    for title, numbers, count, difficulty in [
        ('Вариант по стереометрии', [3, 14], 8, 3),
        ('Отработка: производная и графики', [7, 8, 11], 9, 2),
        ('Отработка: текстовые задачи', [9, 10], 8, 1),
    ]:
        await create_task_set(
            session, TaskSetKind.drill, Subject.math, title,
            sorted({take(numbers[i % len(numbers)]) for i in range(count)}),
            publisher='Авторский', difficulty=difficulty, is_public=True, published_at=now - timedelta(days=count),
        )
    print(f'наборы: 6 ДЗ (назначены ученикам: {len(students)}), 3 варианта, 3 отработки')


async def run() -> None:
    async with new_session() as session:
        await import_bank(session)
        await import_curriculum(session)
        await import_review(session)
        await session.flush()
        await import_sets(session)
        await session.commit()


async def main() -> None:
    await run()
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
