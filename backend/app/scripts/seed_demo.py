"""
Демо-наполнение для локальной разработки: задания из концепта нарешки (concepts/tasks_page),
ДЗ всем ученикам и две отработки, затем учебное содержимое (app/scripts/import_content.py).

    python -m app.scripts.seed_demo

Повторный запуск ничего не дублирует: каждая часть пропускается, если уже есть.
"""
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import exists, select

from app.db.database import engine, new_session
from app.db.enums import AnswerType, FileKind, Subject, TaskSetKind, UserRole
from app.db.models import SourceModel, TaskFileModel, TaskModel, TopicModel, UserModel
from app.scripts import import_content
from app.scripts.demo_figures import FIGURES
from app.services import storage
from app.services.assignments import assign_set
from app.services.task_sets import create_task_set


SOURCE = 'concept_seed'


def topic(number: int, name: str, sub: str) -> tuple:
    """Подтема темы номера — ключ, по которому задания раскладываются по темам"""
    return number, name, sub


def task(external_id: str, number: int, tp: tuple, condition: str, solution: str, answer: str,
         display: str | None = None, image: str | None = None, source: str = 'Авторская задача',
         difficulty: int = 1) -> dict:
    if image:
        condition += f'\n\n![Рисунок](storage://{image})'
    return dict(
        external_id=external_id, task_number=number, topic=tp, condition=condition, solution=solution,
        answer={'accepted': [answer], 'display': display or answer}, image=image, source=source,
        difficulty=difficulty, answer_type=AnswerType.short, part=1, max_score=1,
    )


def build_specs() -> list[dict]:
    """Тексты заданий — без изменений из concepts/tasks_page/seed.py"""
    # ---------------------------------- №1 ----------------------------------
    t1 = topic(1, 'Планиметрия', 'Радиус описанной окружности')
    triangle_condition = (
        'В треугольнике $ABC$ угол $C$ равен $90^\\circ$, $AC = {ac}$, $BC = {bc}$. '
        'Найдите радиус окружности, описанной около этого треугольника.'
    )
    triangle_solution = (
        'Центр описанной окружности прямоугольного треугольника — середина гипотенузы, '
        'поэтому $R = \\dfrac{{AB}}{{2}}$.\n\n'
        'По теореме Пифагора:\n\n'
        '$$AB = \\sqrt{{AC^2 + BC^2}} = \\sqrt{{{ac2} + {bc2}}} = {ab}.$$\n\n'
        'Значит, $R = {r}$.'
    )
    triangles = []
    for i, (ac, bc, ab, r) in enumerate([(6, 8, 10, '5'), (5, 12, 13, '6{,}5'), (9, 12, 15, '7{,}5')], 1):
        triangles.append(task(
            f'math-1-00{i}', 1, t1,
            triangle_condition.format(ac=ac, bc=bc),
            triangle_solution.format(ac2=ac * ac, bc2=bc * bc, ab=ab, r=r),
            answer=r.replace('{,}', '.'), display=r.replace('{,}', ','),
            image=f'figures/math-1-triangle-{ac}-{bc}.svg',
            source='Тренировочный вариант №1' if i == 1 else 'Авторская задача',
        ))

    # ---------------------------------- №4 ----------------------------------
    t4 = topic(4, 'Теория вероятностей', 'Классическое определение вероятности')
    probability = []
    for i, (subject, total, marked, theme, answer) in enumerate([
        ('биологии', 25, 10, 'Грибы', '0.6'),
        ('физике', 40, 6, 'Электростатика', '0.85'),
        ('химии', 50, 9, 'Электролиз', '0.82'),
    ], 1):
        rest = total - marked
        probability.append(task(
            f'math-4-00{i}', 4, t4,
            f'В сборнике билетов по {subject} всего ${total}$ билетов, в ${marked}$ из них встречается '
            f'вопрос по теме «{theme}». На экзамене школьнику достаётся один случайно выбранный билет. '
            f'Найдите вероятность того, что в этом билете **не будет** вопроса по теме «{theme}».',
            f'Благоприятных исходов $ {total} - {marked} = {rest} $, всего исходов ${total}$:\n\n'
            f'$$P = \\dfrac{{{rest}}}{{{total}}} = {answer.replace(".", "{,}")}.$$',
            answer=answer, display=answer.replace('.', ','),
        ))

    # ---------------------------------- №6 ----------------------------------
    t6 = topic(6, 'Уравнения', 'Логарифмические уравнения')
    logs = []
    for i, (base, left, right, eq, x, check) in enumerate([
        (2, 'x + 3', '3x - 5', 'x + 3 = 3x - 5', '4', 'x + 3 = 7 > 0,\\ 3x - 5 = 7 > 0'),
        (3, '2x + 1', 'x + 6', '2x + 1 = x + 6', '5', '2x + 1 = 11 > 0,\\ x + 6 = 11 > 0'),
        (5, '4x - 3', 'x + 9', '4x - 3 = x + 9', '4', '4x - 3 = 13 > 0,\\ x + 9 = 13 > 0'),
    ], 1):
        logs.append(task(
            f'math-6-00{i}', 6, t6,
            f'Найдите корень уравнения $\\log_{base}({left}) = \\log_{base}({right})$.',
            'Логарифмы с одинаковым основанием равны, значит равны аргументы:\n\n'
            f'$${eq} \\;\\Rightarrow\\; x = {x}.$$\n\n'
            f'Проверка ОДЗ: ${check}$ — подходит.',
            answer=x,
        ))

    # ---------------------------------- №7 ----------------------------------
    t7 = topic(7, 'Вычисления и преобразования', 'Формулы приведения')
    trig = [
        task(
            'math-7-001', 7, t7,
            'Найдите значение выражения $\\dfrac{14\\sin 19^\\circ}{\\sin 341^\\circ}$.',
            'Так как $\\sin 341^\\circ = \\sin(360^\\circ - 19^\\circ) = -\\sin 19^\\circ$,\n\n'
            '$$\\dfrac{14\\sin 19^\\circ}{-\\sin 19^\\circ} = -14.$$',
            answer='-14', display='−14', difficulty=2,
        ),
        task(
            'math-7-002', 7, t7,
            'Найдите значение выражения $\\dfrac{24\\cos 22^\\circ}{\\cos 338^\\circ}$.',
            'Так как $\\cos 338^\\circ = \\cos(360^\\circ - 22^\\circ) = \\cos 22^\\circ$,\n\n'
            '$$\\dfrac{24\\cos 22^\\circ}{\\cos 22^\\circ} = 24.$$',
            answer='24', difficulty=2,
        ),
        task(
            'math-7-003', 7, t7,
            'Найдите значение выражения $\\dfrac{-10\\sin 107^\\circ}{\\sin 253^\\circ}$.',
            'Так как $\\sin 253^\\circ = \\sin(360^\\circ - 107^\\circ) = -\\sin 107^\\circ$,\n\n'
            '$$\\dfrac{-10\\sin 107^\\circ}{-\\sin 107^\\circ} = 10.$$',
            answer='10', difficulty=2,
        ),
    ]

    # ---------------------------------- №8 ----------------------------------
    t8 = topic(8, 'Производная и первообразная', 'Производная по графику функции')
    graph_condition = (
        'На рисунке изображён график функции $y = f(x)$, определённой на интервале $({a};\\,{b})$. '
        'Найдите количество точек, в которых производная функции $f(x)$ равна $0$.'
    )
    graph_solution = (
        'Производная равна нулю в точках экстремума — там, где касательная горизонтальна. '
        'На графике это вершины «горок» и «впадин»: {points}.\n\n'
        'Всего **{n}** {word}.'
    )
    graphs = [
        task(
            'math-8-001', 8, t8,
            graph_condition.format(a=-3, b=5),
            graph_solution.format(points='$x \\approx -2$, $x \\approx 1$, $x \\approx 3{,}5$', n=3, word='точки'),
            answer='3', image='figures/math-8-graph-a.svg', source='Тренировочный вариант №1', difficulty=2,
        ),
        task(
            'math-8-002', 8, t8,
            graph_condition.format(a=-3, b=4),
            graph_solution.format(points='$x = -1$ и $x = 2$', n=2, word='точки'),
            answer='2', image='figures/math-8-graph-b.svg', difficulty=2,
        ),
    ]

    # ------------- вторые подтемы: «следующее» и «похожее» начинают отличаться -------------
    t4b = topic(4, 'Теория вероятностей', 'Теоремы о вероятностях событий')
    t6b = topic(6, 'Уравнения', 'Показательные уравнения')
    t7b = topic(7, 'Вычисления и преобразования', 'Логарифмические выражения')
    extra = [
        task(
            'math-4-101', 4, t4b,
            'Стрелок при каждом выстреле попадает в мишень с вероятностью $0{,}8$. '
            'Найдите вероятность того, что, сделав два выстрела, стрелок **оба раза** попадёт.',
            'Выстрелы независимы, поэтому вероятности перемножаются:\n\n$$P = 0{,}8 \\cdot 0{,}8 = 0{,}64.$$',
            answer='0.64', display='0,64', difficulty=2,
        ),
        task(
            'math-4-102', 4, t4b,
            'В магазине два платёжных терминала, они работают независимо друг от друга. '
            'Вероятность того, что терминал неисправен, равна $0{,}1$. '
            'Найдите вероятность того, что **хотя бы один** терминал исправен.',
            'Перейдём к противоположному событию «оба неисправны»: $0{,}1 \\cdot 0{,}1 = 0{,}01$.\n\n'
            '$$P = 1 - 0{,}01 = 0{,}99.$$',
            answer='0.99', display='0,99', difficulty=2,
        ),
        task(
            'math-6-101', 6, t6b,
            'Найдите корень уравнения $2^{x - 3} = 16$.',
            'Представим правую часть как степень двойки: $16 = 2^4$.\n\n$$x - 3 = 4 \\;\\Rightarrow\\; x = 7.$$',
            answer='7',
        ),
        task(
            'math-6-102', 6, t6b,
            'Найдите корень уравнения $3^{2x - 1} = 27$.',
            'Так как $27 = 3^3$:\n\n$$2x - 1 = 3 \\;\\Rightarrow\\; x = 2.$$',
            answer='2',
        ),
        task(
            'math-6-103', 6, t6b,
            'Найдите корень уравнения $5^{x + 1} = \\dfrac{1}{25}$.',
            'Так как $\\dfrac{1}{25} = 5^{-2}$:\n\n$$x + 1 = -2 \\;\\Rightarrow\\; x = -3.$$',
            answer='-3', display='−3',
        ),
        task(
            'math-7-101', 7, t7b,
            'Найдите значение выражения $\\log_2 32 - \\log_2 4$.',
            'Разность логарифмов с одинаковым основанием — логарифм частного:\n\n'
            '$$\\log_2 32 - \\log_2 4 = \\log_2 \\dfrac{32}{4} = \\log_2 8 = 3.$$',
            answer='3',
        ),
        task(
            'math-7-102', 7, t7b,
            'Найдите значение выражения $\\dfrac{\\log_5 49}{\\log_5 7}$.',
            'Так как $49 = 7^2$, то $\\log_5 49 = 2\\log_5 7$:\n\n'
            '$$\\dfrac{2\\log_5 7}{\\log_5 7} = 2.$$',
            answer='2',
        ),
    ]

    # Вторая часть — чтобы было что проверять преподавателю
    t13 = topic(13, 'Уравнения', 'Тригонометрические уравнения')
    detailed = [dict(
        external_id='math-13-001', task_number=13, topic=t13, part=2, max_score=2, difficulty=3,
        condition='а) Решите уравнение $2\\cos^2 x - \\cos x = 0$.\n\n'
                  'б) Найдите все корни этого уравнения, принадлежащие отрезку '
                  '$\\left[\\dfrac{\\pi}{2};\\, 2\\pi\\right]$.',
        solution='Вынесем $\\cos x$ за скобки: $\\cos x\\,(2\\cos x - 1) = 0$.\n\n'
                 '$\\cos x = 0 \\Rightarrow x = \\dfrac{\\pi}{2} + \\pi k$; '
                 '$\\cos x = \\dfrac12 \\Rightarrow x = \\pm\\dfrac{\\pi}{3} + 2\\pi k$.\n\n'
                 'На отрезке: $\\dfrac{\\pi}{2},\\ \\dfrac{3\\pi}{2},\\ \\dfrac{5\\pi}{3}$.',
        answer={'accepted': [], 'display': 'а) $\\dfrac{\\pi}{2} + \\pi k,\\ \\pm\\dfrac{\\pi}{3} + 2\\pi k$; '
                                           'б) $\\dfrac{\\pi}{2},\\ \\dfrac{3\\pi}{2},\\ \\dfrac{5\\pi}{3}$'},
        grade_criteria='2 балла — обоснованно получены верные ответы в обоих пунктах.\n\n'
                       '1 балл — обоснованно получен верный ответ в пункте а) или б).\n\n'
                       '0 баллов — решение не соответствует ни одному из критериев.',
        answer_type=AnswerType.detailed, image=None, source='Авторская задача',
    )]

    return triangles + probability + logs + trig + graphs + extra + detailed


async def seed() -> None:
    async with new_session() as session:
        if (await session.execute(select(exists().where(TaskModel.external_source == SOURCE)))).scalar_one():
            print('демо-нарешка: уже есть')
            return

        for key, draw in FIGURES.items():
            storage.save(key, draw().encode())

        specs = build_specs()
        roots: dict[tuple, TopicModel] = {}
        for number, name, _ in (s['topic'] for s in specs):
            if (number, name) not in roots:
                roots[(number, name)] = TopicModel(subject=Subject.math, task_number=number, name=name)
                session.add(roots[(number, name)])
        await session.flush()

        subs: dict[tuple, TopicModel] = {}
        for key in (s['topic'] for s in specs):
            if key not in subs:
                siblings = sum(1 for k in subs if k[:2] == key[:2])
                subs[key] = TopicModel(subject=Subject.math, task_number=key[0], name=key[2],
                                       parent_id=roots[key[:2]].id, position=siblings)
                session.add(subs[key])
        sources = {name: SourceModel(name=name) for name in dict.fromkeys(s['source'] for s in specs)}
        session.add_all(sources.values())
        await session.flush()

        tasks: dict[str, TaskModel] = {}
        for spec in specs:
            image = spec['image']
            tasks[spec['external_id']] = TaskModel(
                subject=Subject.math, task_number=spec['task_number'], part=spec['part'],
                difficulty=spec['difficulty'], topic_id=subs[spec['topic']].id, condition=spec['condition'],
                answer_type=spec['answer_type'], answer=spec['answer'], max_score=spec['max_score'],
                solution=spec['solution'], grade_criteria=spec.get('grade_criteria'),
                external_source=SOURCE, external_id=spec['external_id'],
                sources=[sources[spec['source']]],
                files=[TaskFileModel(kind=FileKind.image, storage_key=image, filename=image.rsplit('/', 1)[-1])]
                if image else [],
            )
        session.add_all(tasks.values())
        await session.flush()

        def ids(*external_ids: str) -> list[int]:
            return [tasks[e].id for e in external_ids]

        now = datetime.now(timezone.utc)
        homework = await create_task_set(
            session, TaskSetKind.homework, Subject.math, 'Уравнения: логарифмы и степени',
            ids('math-6-001', 'math-6-002', 'math-6-101', 'math-6-102', 'math-7-101', 'math-13-001'),
            description='Уравнения и выражения',
        )
        await create_task_set(
            session, TaskSetKind.drill, Subject.math, 'Отработка: вероятности и вычисления',
            ids('math-4-001', 'math-4-002', 'math-4-101', 'math-7-001', 'math-7-002', 'math-7-102'),
            publisher='Авторский', difficulty=2, is_public=True, published_at=now,
        )
        await create_task_set(
            session, TaskSetKind.drill, Subject.math, 'Мини-пробник: часть 1',
            ids('math-1-001', 'math-4-003', 'math-6-003', 'math-7-003', 'math-8-001'),
            publisher='Авторский', difficulty=2, time_limit_sec=30 * 60, is_public=True, published_at=now,
        )

        students = (await session.execute(
            select(UserModel.id).where(UserModel.role == UserRole.student, UserModel.is_active)
        )).scalars().all()
        if students:
            await assign_set(session, homework.id, None, deadline_at=now + timedelta(days=3), student_ids=list(students))

        await session.commit()
        print(f'Заданий: {len(tasks)}, тем: {len(roots)}, подтем: {len(subs)}, ДЗ назначено ученикам: {len(students)}')


async def main() -> None:
    await seed()
    await import_content.run()
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(main())
