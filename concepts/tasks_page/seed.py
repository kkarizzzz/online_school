"""
Заполняет концепт-базу тестовыми заданиями по математике и генерирует рисунки в ./storage.

У тем по 1–2 подтемы, в каждой 2–3 задания: «Следующее» берёт задание из темы, «Похожее» — из той же подтемы.

Запуск:  python seed.py   (пересоздаёт базу с нуля)
"""
from sqlalchemy.orm import Session

from db import STORAGE_DIR, engine
from figures import FIGURES
from models import AnswerType, Base, FileKind, Source, SubjectEnum, Task, TaskFile, Topic


SOURCE = 'concept_seed'
MATH = SubjectEnum.math


def write_storage() -> None:
    for key, draw in FIGURES.items():
        path = STORAGE_DIR / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(draw(), encoding='utf-8')


def seed() -> None:
    write_storage()

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    topics: dict[tuple, Topic] = {}
    sources: dict[str, Source] = {}

    def topic(number: int, name: str, sub: str) -> Topic:
        parent = topics.setdefault((number, name), Topic(subject=MATH, task_number=number, name=name))
        return topics.setdefault((number, name, sub), Topic(subject=MATH, task_number=number, name=sub, parent=parent))

    def task(external_id: str, number: int, tp: Topic, condition: str, solution: str, answer: str,
             display: str | None = None, image: str | None = None, source: str = 'Авторская задача',
             difficulty: int = 1) -> Task:
        files = []
        if image:
            condition += f'\n\n![Рисунок](storage://{image})'
            files.append(TaskFile(kind=FileKind.image, storage_key=image, filename=image.rsplit('/', 1)[-1]))
        return Task(
            subject=MATH, task_number=number, difficulty=difficulty, topic=tp,
            condition=condition, solution=solution,
            answer_type=AnswerType.short, answer={'accepted': [answer], 'display': display or answer},
            files=files, sources=[sources.setdefault(source, Source(name=source))],
            external_source=SOURCE, external_id=external_id,
        )

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

    tasks = triangles + probability + logs + trig + graphs + extra
    with Session(engine) as session:
        session.add_all(tasks)
        session.commit()
        print(f'Создано заданий: {len(tasks)}')


if __name__ == '__main__':
    seed()
