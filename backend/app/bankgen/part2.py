"""
Задания второй части (№ 14, 17, 18, 19) с развёрнутым решением.

Класс-наследник Solved решает «семейство» — задания ФИПИ с одной формулировкой и разными числами:
    fipi      — {id задания ФИПИ: параметры}, числа сняты с условия;
    solution  — решение по параметрам: доказательство пункта а и вычисление пункта б;
    answer    — точный ответ (sympy) и его запись;
    check     — тот же ответ, полученный независимо (в координатах, перебором и т. п.);
    sample    — новые числа для аналога; condition и figure — наше условие и чертёж.
Если check не совпал с answer, задание в банк не попадает (build пишет его в отчёт).
"""
import math
import re
import random

import sympy as sp

from app.bankgen.core import Rendered, Template


def tx(e) -> str:
    """Число sympy → LaTeX в школьной записи (запятая, без «1.0»)"""
    if isinstance(e, (int, float)) and not isinstance(e, bool):
        e = sp.nsimplify(e)
    s = sp.latex(sp.radsimp(e) if e.has(sp.sqrt) or isinstance(e, sp.Pow) else e)
    s = s.replace('\\operatorname{acos}', '\\arccos').replace('\\operatorname{asin}', '\\arcsin') \
         .replace('\\operatorname{atan}', '\\operatorname{arctg}').replace('\\operatorname{acot}', '\\operatorname{arcctg}')
    s = s.replace('\\left(', '(').replace('\\right)', ')')
    return s.replace('.', '{,}')


def simp(e) -> sp.Expr:
    """Упростить число с корнями: (√2+√6)·√2 − 2√3 → 1, 3√2·√(10−3√2) → 3√(20−6√2)"""
    e = sp.nsimplify(sp.radsimp(sp.expand(e)))
    if e.is_Rational or not e.is_number:
        return e
    try:
        e = sp.nsimplify(sp.sqrtdenest(sp.simplify(e)))
    except Exception:  # noqa: BLE001
        pass
    if e.is_Rational:
        return e
    nested = any(isinstance(a, sp.Pow) and a.base.is_Add for a in e.atoms(sp.Pow))
    e2 = sp.expand(e ** 2)
    if not nested or e.is_Add or e2.is_Rational or len(sp.Add.make_args(e2)) != 2:
        return e
    # e = √(e2), выносим квадрат из общего множителя коэффициентов
    coeffs = [sp.Rational(c) for c in (t.as_coeff_Mul()[0] for t in sp.Add.make_args(e2))]
    num = sp.gcd([c.p for c in coeffs])
    den = sp.lcm([c.q for c in coeffs])
    k = 1
    for prime, mult in sp.factorint(int(num)).items():
        k *= prime ** (mult // 2)
    kd = 1
    for prime, mult in sp.factorint(int(den)).items():
        kd *= prime ** ((mult + 1) // 2)
    out = sp.Rational(k, kd) * sp.sqrt(sp.expand(e2 * kd ** 2 / k ** 2), evaluate=True)
    return out if sp.N(out - e, 30) == 0 or abs(sp.N(out - e, 30)) < 1e-25 else e


def r(*a) -> sp.Rational:
    return sp.Rational(*a)


S = sp.sqrt


class Answer:
    """Ответ: запись для ученика + числовое значение для проверки"""

    def __init__(self, display: str, value: float):
        self.display, self.value = display, float(value)

    @classmethod
    def num(cls, e) -> 'Answer':
        return cls(f'${tx(e)}$', sp.N(e, 30))

    @classmethod
    def angle(cls, e, fn: str = 'arctg') -> 'Answer':
        """Угол: если табличный — в градусах, иначе arctg/arccos/arcsin от значения e"""
        f = {'arctg': sp.atan, 'arccos': sp.acos, 'arcsin': sp.asin}[fn]
        ang = sp.nsimplify(f(e))
        degs = sp.nsimplify(ang * 180 / sp.pi)
        if degs.is_Rational and degs.q == 1:
            return cls(f'${tx(degs)}^\\circ$', ang)
        name = {'arctg': '\\operatorname{arctg}', 'arccos': '\\arccos', 'arcsin': '\\arcsin'}[fn]
        return cls(f'${name}{_arg(e)}$', ang)

    @classmethod
    def ratio(cls, m, n) -> 'Answer':
        q = sp.nsimplify(sp.nsimplify(m) / sp.nsimplify(n))
        if q.is_Rational:          # 1/2 : 5/2 → 1:5
            return cls(f'${q.p}:{q.q}$', q)
        return cls(f'${tx(m)}:{tx(n)}$', q)


def _arg(e) -> str:
    t = tx(e)
    return t if t.lstrip('-').isdigit() else f'{t}' if t.startswith('\\frac') or t.startswith('\\sqrt') else f'({t})'


class Solved(Template):
    detailed = True
    difficulty = 3
    fipi: dict[str, dict] = {}

    @property
    def code(self) -> str:   # noqa: D401 — код шаблона из имени класса
        return f'{self.number}.{type(self).__name__}'

    @property
    def variants(self) -> bool:
        return type(self).sample is not Solved.sample

    # --- что пишет конкретная задача
    def answer(self, p) -> Answer:
        raise NotImplementedError

    def check(self, p) -> float:
        raise NotImplementedError

    def solution(self, p) -> str:
        raise NotImplementedError

    def condition(self, p) -> str:
        raise NotImplementedError

    def figure(self, p) -> str | None:
        return None

    def sample(self, rng: random.Random):
        return None


    # --- интерфейс Template
    def match(self, task):
        p = self.fipi.get(task['id'])
        return {**p, '_fipi': True} if p is not None else None

    def solve(self, p):
        a = self.answer(p)
        return {'accepted': [], 'display': a.display}

    def verify(self, p, answer) -> bool:
        a = self.answer(p)
        v = self.check(p)
        if isinstance(v, bool):
            return v
        return math.isclose(a.value, float(v), rel_tol=1e-7, abs_tol=1e-9)

    def generate(self, rng: random.Random, tries: int | None = None):
        """Как в Template, но аналог не должен повторять числа оригинала ФИПИ"""
        originals = list(self.fipi.values())
        for _ in range(tries or 80):
            try:
                p = self.sample(rng)
                if p is None or p in originals:
                    continue
                answer = self.solve(p)
            except (ValueError, ZeroDivisionError, OverflowError, AssertionError, TypeError):
                continue
            if self.nice(answer) and self.verify(p, answer):
                return p, answer
        raise RuntimeError(f'{self.code}: не нашлось чисел с красивым ответом')

    def nice(self, answer) -> bool:
        d = answer['display']
        return len(d) <= 48 and all(int(x) <= 150 for x in re.findall(r'\d+', d))

    READABLE = 0.09     # чертёж хуже этого (точки ближе 9% размера рисунка) перерисовываем

    def drawing(self, p) -> str | None:
        """
        Чертёж к задаче. Обычно — по её числам, но если при них точки слипаются или фигура вырождается,
        рисуем ту же конфигурацию с «удобными» числами: чертёж — иллюстрация, длины на нём не обязаны совпадать.
        Подходят только данные той же задачи (те же текстовые параметры), чтобы не поменялась конфигурация.
        """
        from app.bankgen import geo2
        geo2.LAST_SCORE = 1.0
        svg = self.figure(p)
        if not svg or geo2.LAST_SCORE >= self.READABLE or type(self).sample is Solved.sample:
            return svg
        best = (geo2.LAST_SCORE, svg)
        # «та же конфигурация» — совпадают смысловые строки (что дано, что найти: 'B1C1', 'EK'), числа могут быть любыми
        same = {k: v for k, v in p.items() if not k.startswith('_')
                and (isinstance(v, bool) or isinstance(v, str) and re.fullmatch(r'[A-Za-z_]\w*', v))}
        for i in range(60):
            try:
                q = self.sample(random.Random(f'{self.code}-figure-{i}'))
                if q is None or set(q) - {'_fipi'} != set(p) - {'_fipi'} or any(q.get(k) != v for k, v in same.items()):
                    continue
                geo2.LAST_SCORE = 1.0
                alt = self.figure(q)
            except (ValueError, ZeroDivisionError, OverflowError, AssertionError, TypeError, KeyError, IndexError):
                continue
            if alt and geo2.LAST_SCORE > best[0]:
                best = (geo2.LAST_SCORE, alt)
                if best[0] >= 2 * self.READABLE:
                    break
        geo2.LAST_SCORE = best[0]
        return best[1]

    def render(self, p) -> Rendered:
        a = self.answer(p)
        svg = self.drawing(p)
        figs = {'fig': svg} if svg else {}
        pic = '![](figure://fig)\n\n' if svg else ''
        if p.get('_fipi'):
            # у ФИПИ условие своё (часто без рисунка) — наш чертёж ставим в начало решения
            return Rendered('', pic + self.solution(p) + f'\n\n**Ответ:** {a.display}.', figs)
        return Rendered(self.condition(p) + ('\n\n' + pic.strip() if svg else ''),
                        self.solution(p) + f'\n\n**Ответ:** {a.display}.', figs)
