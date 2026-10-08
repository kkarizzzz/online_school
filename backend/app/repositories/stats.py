"""Сводная статистика ученика для кабинета ученика и родителя"""
from datetime import date, timedelta

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import AttemptStatus, Subject, UserRole
from app.db.models import (
    AchievementModel, AttemptModel, StudentAchievementModel, StudentAssignmentModel, StudentDailyActivityModel,
    StudentTaskStatusModel, StudentTopicStatsModel, TaskModel, TaskSetModel, UserModel,
)
from app.repositories.tasks import root_topic, topic_progress, topics_map
from app.schemas.stats_schemas import (
    AchievementOut, DayActivity, HomeworkSummary, MockExamResult, StudentStatsOut, SubjectTasks, TopicStatsOut, Totals,
)
from app.services.stats import current_streak


def _ratio(part: int, whole: int) -> float | None:
    return round(part / whole, 4) if whole else None


async def _today(session: AsyncSession, user: UserModel) -> date:
    """Сегодня в поясе ученика — по базе часовых поясов PostgreSQL, как и в статистике"""
    return (await session.execute(
        select(func.date(func.timezone(user.timezone, func.now())))
    )).scalar_one()


async def student_stats(session: AsyncSession, student: UserModel) -> StudentStatsOut:
    sid = student.id

    days = (await session.execute(
        select(StudentDailyActivityModel).where(StudentDailyActivityModel.student_id == sid)
    )).scalars().all()
    solved = (await session.execute(
        select(func.count()).select_from(StudentTaskStatusModel)
        .where(StudentTaskStatusModel.student_id == sid, StudentTaskStatusModel.is_solved)
    )).scalar_one()
    answered = sum(d.answered for d in days)
    correct = sum(d.correct for d in days)
    totals = Totals(
        answered=answered, correct=correct, accuracy=_ratio(correct, answered), tasks_solved=solved,
        seconds=sum(d.seconds for d in days), lessons_done=sum(d.lessons_done for d in days),
    )

    today = await _today(session, student)
    by_day = {d.day: d for d in days}
    week = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        d = by_day.get(day)
        week.append(DayActivity(
            day=day, answered=d.answered if d else 0, correct=d.correct if d else 0,
            seconds=d.seconds if d else 0, lessons_done=d.lessons_done if d else 0,
        ))

    now = func.now()
    hw = (await session.execute(
        select(
            func.count().filter(and_(StudentAssignmentModel.submitted_at.is_(None),
                                     func.coalesce(StudentAssignmentModel.deadline_at >= now, True))),
            func.count().filter(and_(StudentAssignmentModel.submitted_at.is_(None),
                                     StudentAssignmentModel.deadline_at < now)),
            func.count().filter(StudentAssignmentModel.submitted_at.is_not(None)),
        ).where(StudentAssignmentModel.student_id == sid)
    )).one()
    hw_attempts = (await session.execute(
        select(
            func.count().filter(AttemptModel.is_late),
            func.avg(case((AttemptModel.status == AttemptStatus.graded,
                           100.0 * AttemptModel.primary_score / func.nullif(AttemptModel.max_score, 0)))),
        ).where(AttemptModel.student_id == sid, AttemptModel.student_assignment_id.is_not(None),
                AttemptModel.submitted_at.is_not(None))
    )).one()
    homework = HomeworkSummary(
        current=hw[0], overdue=hw[1], done=hw[2], late=hw_attempts[0],
        avg_percent=round(hw_attempts[1], 1) if hw_attempts[1] is not None else None,
    )

    exams = (await session.execute(
        select(AttemptModel, TaskSetModel.title, TaskSetModel.subject)
        .join(TaskSetModel, TaskSetModel.id == AttemptModel.set_id)
        .where(AttemptModel.student_id == sid, TaskSetModel.is_standard, AttemptModel.submitted_at.is_not(None),
               AttemptModel.status != AttemptStatus.abandoned)
        .order_by(AttemptModel.submitted_at)
    )).all()
    mock_exams = [
        MockExamResult(
            attempt_id=a.id, title=title, subject=subject, primary_score=a.primary_score,
            secondary_score=a.secondary_score, max_score=a.max_score, submitted_at=a.submitted_at,
        )
        for a, title, subject in exams
    ]

    unlocked = dict((await session.execute(
        select(StudentAchievementModel.code, StudentAchievementModel.unlocked_at)
        .where(StudentAchievementModel.student_id == sid)
    )).all())
    achievements = [
        AchievementOut(code=a.code, title=a.title, description=a.description, unlocked_at=unlocked.get(a.code))
        for a in (await session.execute(select(AchievementModel).order_by(AchievementModel.code))).scalars()
    ]

    by_subject = dict((await session.execute(
        select(TaskModel.subject, func.count())
        .join(StudentTaskStatusModel, StudentTaskStatusModel.task_id == TaskModel.id)
        .where(StudentTaskStatusModel.student_id == sid, StudentTaskStatusModel.is_solved)
        .group_by(TaskModel.subject)
    )).all())
    totals_by_subject = dict((await session.execute(
        select(TaskModel.subject, func.count()).where(TaskModel.is_active).group_by(TaskModel.subject)
    )).all())
    subjects = [
        SubjectTasks(subject=subject, tasks_solved=by_subject.get(subject, 0), task_count=count)
        for subject, count in sorted(totals_by_subject.items(), key=lambda kv: list(Subject).index(kv[0]))
    ]

    return StudentStatsOut(
        streak=await current_streak(session, sid), rank_percent=await _rank_percent(session, solved),
        subjects=subjects, totals=totals, week=week,
        homework=homework, mock_exams=mock_exams, achievements=achievements,
    )


async def _rank_percent(session: AsyncSession, solved: int) -> int | None:
    """Место по числу решённых заданий: «Топ 8%» — решивших больше меньше 8% учеников"""
    if not solved:
        return None
    per_student = (
        select(StudentTaskStatusModel.student_id, func.count().label('solved'))
        .where(StudentTaskStatusModel.is_solved)
        .group_by(StudentTaskStatusModel.student_id)
        .subquery()
    )
    ahead = (await session.execute(
        select(func.count()).select_from(per_student).where(per_student.c.solved > solved)
    )).scalar_one()
    students = (await session.execute(
        select(func.count()).select_from(UserModel).where(UserModel.role == UserRole.student, UserModel.is_active)
    )).scalar_one()
    return max(1, -(-100 * (ahead + 1) // max(students, 1)))


async def student_topic_stats(session: AsyncSession, student_id: int, subject: Subject) -> list[TopicStatsOut]:
    """Темы верхнего уровня: сколько решено и точность, подтемы сложены в тему"""
    topics = await topics_map(session, {subject})
    rows = (await session.execute(
        select(StudentTopicStatsModel).where(
            StudentTopicStatsModel.student_id == student_id,
            StudentTopicStatsModel.topic_id.in_(list(topics)),
        )
    )).scalars().all() if topics else []

    answers: dict[int, list] = {}
    for row in rows:
        root = root_topic(topics[row.topic_id], topics)
        acc = answers.setdefault(root.id, [0, 0, None])
        acc[0] += row.answered
        acc[1] += row.correct
        if row.last_answer_at and (acc[2] is None or row.last_answer_at > acc[2]):
            acc[2] = row.last_answer_at

    result = []
    for p in await topic_progress(session, subject, student_id):
        answered, correct, last = answers.get(p.topic.id, [0, 0, None])
        result.append(TopicStatsOut(
            topic_id=p.topic.id, task_number=p.topic.task_number, name=p.topic.name,
            task_count=p.task_count, tasks_solved=p.solved_count,
            answered=answered, correct=correct, accuracy=_ratio(correct, answered), last_answer_at=last,
        ))
    return result
