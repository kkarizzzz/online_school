"""
№ 18. Задачи с параметром.

Ответ — множество значений a (sympy). check независимо считает число решений при многих значениях a
(app.bankgen.param.verify): точно, через корни многочленов на кусках, или численно по исходному уравнению.
"""
import math
from fractions import Fraction

import sympy as sp

from app.bankgen.ineq import latex_set
from app.bankgen.param import INF, X, Points, ge, gt, num, poly_roots, scan_roots, verify
from app.bankgen.part2 import S, Answer, Solved, r, tx

TOPIC = 'Задачи с параметром'
x = X
oo = sp.oo
I = sp.Interval
F = sp.FiniteSet
U = sp.Union


def show(s) -> str:
    return f'$a\\in {latex_set(s)}$'


class Param(Solved):
    number, topic, difficulty = 18, TOPIC, 3
    lo, hi, step = -10, 10, Fraction(1, 7)

    def aset(self, p) -> sp.Set:
        raise NotImplementedError

    def ok(self, p, a) -> bool:
        raise NotImplementedError

    def extra(self, p):
        return ()

    def answer(self, p):
        return Answer(show(self.aset(p)), 0)

    def check(self, p):
        return verify(self.aset(p), lambda a: self.ok(p, a), self.lo, self.hi, self.step, self.extra(p))

    def condition(self, p):
        return self.cond(p)

    def nice(self, answer) -> bool:
        return len(answer['display']) <= 160


def roots_count(expr) -> int:
    P = Points()
    for r_ in poly_roots(expr):
        if r_ == INF:
            return 10 ** 9
        P.add(r_)
    return len(P)


# ---------------------------------------------------------------------------
# Уравнения вида (u + v)² = (u − v)²  ⇔  u·v = 0
# ---------------------------------------------------------------------------

class LogSquares(Param):
    """(kx + ln(x + ma))² = (kx − ln(x + ma))² — единственное решение на [0; 1]"""
    fipi = {'8D6C09': dict(k=1, m=1), '3DD135': dict(k=2, m=2)}
    lo, hi, step = -3, 4, Fraction(1, 9)

    def aset(self, p):
        return U(F(0), I(r(1, p['m']), oo))

    def ok(self, p, a):
        k, m, a = p['k'], p['m'], float(a)
        Fx = lambda t: (k * t + math.log(t + m * a)) ** 2 - (k * t - math.log(t + m * a)) ** 2  # noqa: E731
        return scan_roots(Fx, 0.0, 1.0, 1500, points=[0.0, 1.0, 1 - m * a]) == 1

    def cond(self, p):
        k, m = p['k'], p['m']
        kx = 'x' if k == 1 else f'{k}x'
        ma = 'a' if m == 1 else f'{m}a'
        return (f'Найдите все значения $a$, при которых уравнение $$({kx}+\\ln(x+{ma}))^2=({kx}-\\ln(x+{ma}))^2$$ '
                'имеет единственное решение на отрезке $[0;1]$.')

    def solution(self, p):
        k, m = p['k'], p['m']
        kx = 'x' if k == 1 else f'{k}x'
        ma = 'a' if m == 1 else f'{m}a'
        b = r(1, m)
        return (
            f'Разность квадратов: $(u+v)^2-(u-v)^2=4uv$, поэтому уравнение равносильно ${4 * k}x\\cdot\\ln(x+{ma})=0$ при условии $x+{ma}>0$. '
            f'Корни: $x=0$ (если ${ma}>0$, то есть $a>0$) и $\\ln(x+{ma})=0$, $x=1-{ma}$ (условие $x+{ma}=1>0$ выполнено).\n\n'
            f'$x=1-{ma}\\in[0;1]$ при $0\\le a\\le {tx(b)}$. Разберём случаи.\n\n'
            f'- $a<0$: корень $x=0$ не входит в ОДЗ, а $1-{ma}>1$ — решений на отрезке нет.\n'
            f'- $a=0$: $x=0$ не входит в ОДЗ ($\\ln 0$), остаётся $x=1$ — одно решение.\n'
            f'- $0<a<{tx(b)}$: два различных решения $x=0$ и $x=1-{ma}\\in(0;1)$.\n'
            f'- $a={tx(b)}$: оба корня совпадают, $x=0$ — одно решение.\n'
            f'- $a>{tx(b)}$: только $x=0$.\n\n'
            f'**Ответ:** {show(self.aset(p))}.').replace('\n\n**Ответ:** ' + show(self.aset(p)) + '.', '')

    def sample(self, rng):
        return dict(k=rng.randint(1, 5), m=rng.randint(1, 5))


class TanSquares(Param):
    """(2x + a ± 1 ∓ tg x)² = (2x + a ∓ 1 ± tg x)² — единственное решение на отрезке"""
    fipi = {'36F316': dict(s=-1), '211B61': dict(s=1)}
    lo, hi, step = -8, 8, Fraction(1, 5)

    def aset(self, p):
        pi = sp.pi
        if p['s'] == -1:      # tg x = 1 на [0; π]
            return U(I.open(-oo, -2 * pi), F(-pi, -pi / 2), I.open(0, oo))
        return U(I(-oo, -pi), F(pi / 2), I(pi, oo))

    def extra(self, p):
        return (-sp.pi, sp.pi, -sp.pi / 2, sp.pi / 2, -2 * sp.pi)

    def ok(self, p, a):
        a = float(a)
        s = p['s']
        if s == -1:
            Fx = lambda t: (2 * t + a + 1 - math.tan(t)) ** 2 - (2 * t + a - 1 + math.tan(t)) ** 2  # noqa: E731
            lo, hi = 0.0, math.pi
        else:
            Fx = lambda t: (2 * t + a + 1 + math.tan(t)) ** 2 - (2 * t + a - 1 - math.tan(t)) ** 2  # noqa: E731
            lo, hi = -math.pi / 2 + 1e-9, math.pi / 2 - 1e-9

        def G(t):
            if abs(math.cos(t)) < 1e-12:
                return None
            return Fx(t)
        return scan_roots(G, lo, hi, 2000, points=[lo, hi, -a / 2]) == 1

    def cond(self, p):
        if p['s'] == -1:
            return ('Найдите все значения $a$, при которых уравнение $$(2x+a+1-\\operatorname{tg}x)^2=(2x+a-1+\\operatorname{tg}x)^2$$ '
                    'имеет единственное решение на отрезке $[0;\\pi]$.')
        return ('Найдите все значения $a$, при которых уравнение $$(2x+a+1+\\operatorname{tg}x)^2=(2x+a-1-\\operatorname{tg}x)^2$$ '
                'имеет единственное решение на отрезке $\\left[-\\frac{\\pi}{2};\\frac{\\pi}{2}\\right]$.')

    def solution(self, p):
        if p['s'] == -1:
            return (
                'Пусть $u=2x+a$, $v=1-\\operatorname{tg}x$; уравнение $(u+v)^2=(u-v)^2$ равносильно $uv=0$ (при $x\\ne\\frac\\pi2$, где тангенс '
                'определён): $x=-\\frac a2$ или $\\operatorname{tg}x=1$.\n\n'
                'На $[0;\\pi]$ уравнение $\\operatorname{tg}x=1$ имеет ровно один корень $x=\\frac\\pi4$ — он есть при любом $a$. Значит, '
                'решение единственно, если второй корень $x=-\\frac a2$ не даёт нового решения: либо он вне отрезка, либо совпадает с $\\frac\\pi4$, '
                'либо равен $\\frac\\pi2$ (там тангенс не определён).\n\n'
                '- $-\\frac a2\\notin[0;\\pi]$: $a>0$ или $a<-2\\pi$;\n'
                '- $-\\frac a2=\\frac\\pi4$: $a=-\\frac\\pi2$;\n'
                '- $-\\frac a2=\\frac\\pi2$: $a=-\\pi$.')
        return (
            'Пусть $u=2x+a$, $v=1+\\operatorname{tg}x$; уравнение $(u+v)^2=(u-v)^2$ равносильно $uv=0$ (тангенс определён при '
            '$x\\ne\\pm\\frac\\pi2$): $x=-\\frac a2$ или $\\operatorname{tg}x=-1$.\n\n'
            'На $\\left(-\\frac\\pi2;\\frac\\pi2\\right)$ уравнение $\\operatorname{tg}x=-1$ имеет один корень $x=-\\frac\\pi4$; концы отрезка в ОДЗ не входят. '
            'Решение единственно, если $x=-\\frac a2$ не даёт нового: $-\\frac a2\\notin\\left(-\\frac\\pi2;\\frac\\pi2\\right)$, то есть '
            '$a\\le-\\pi$ или $a\\ge\\pi$, либо $-\\frac a2=-\\frac\\pi4$, $a=\\frac\\pi2$.')


class ExpAbsFactor(Param):
    """b^{2x} − (sa + m)b^x = (k + 3|a|)b^x − (sa + m)(3|a| + k): единственное решение"""
    fipi = {'617476': dict(b=2, s=-1, m=6, k=2), 'B384BC': dict(b=5, s=1, m=6, k=5)}
    lo, hi, step = -12, 12, Fraction(1, 6)

    def aset(self, p):
        s, m, k = p['s'], p['m'], p['k']
        a = sp.Symbol('a')
        sol = set()
        for sign in (1, -1):        # s·a + m = 3·sign·a + k при a·sign ≥ 0
            v = sp.solve(sp.Eq(s * a + m, 3 * sign * a + k), a)
            sol |= {w for w in v if w * sign >= 0}
        # s·a + m ≤ 0
        half = I(-oo, sp.Rational(-m, s)) if s > 0 else I(sp.Rational(m, 1), oo)
        return U(half, F(*sol))

    def ok(self, p, a):
        s, m, k = p['s'], p['m'], p['k']
        t = sp.Symbol('t')
        P = Points()
        for r_ in poly_roots((t - (s * a + m)) * (t - (3 * abs(a) + k)), t):
            if gt(r_):
                P.add(r_)
        return len(P) == 1

    def cond(self, p):
        b, s, m, k = p['b'], p['s'], p['m'], p['k']
        if s == -1:
            return (f'Найдите все значения $a$, для каждого из которых уравнение $${b * b}^x+(a-{m})\\cdot {b}^x=({k}+3|a|)\\cdot {b}^x+(a-{m})(3|a|+{k})$$ '
                    'имеет единственное решение.')
        return (f'Найдите все значения $a$, для каждого из которых уравнение $${b * b}^x-(a+{m})\\cdot {b}^x=({k}+3|a|)\\cdot {b}^x-(a+{m})(3|a|+{k})$$ '
                'имеет единственное решение.')

    def solution(self, p):
        b, s, m, k = p['b'], p['s'], p['m'], p['k']
        t1 = f'{m}-a' if s == -1 else f'a+{m}'
        st = self.aset(p)
        return (
            f'Замена $t={b}^x>0$ — каждому $t>0$ соответствует ровно одно $x$. Уравнение примет вид '
            f'$t^2-({t1})t-(3|a|+{k})t+({t1})(3|a|+{k})=0$, то есть $$\\bigl(t-({t1})\\bigr)\\bigl(t-(3|a|+{k})\\bigr)=0.$$\n\n'
            f'Корень $t_2=3|a|+{k}>0$ есть всегда. Решение единственно, если второй корень $t_1={t1}$ не положителен или совпадает с $t_2$.\n\n'
            f'- ${t1}\\le0$.\n'
            f'- ${t1}=3|a|+{k}$: при $a\\ge0$ и при $a<0$ получаем линейные уравнения, их подходящие корни — ' +
            ', '.join(f'$a={tx(v)}$' for v in sorted([w for w in st.args if isinstance(w, sp.FiniteSet)][0], key=float)) + '.')

    def sample(self, rng):
        b = rng.choice([2, 3, 5, 7])
        return dict(b=b, s=rng.choice([1, -1]), m=rng.randint(2, 9), k=rng.randint(1, 6))


class SqrtQuartic(Param):
    """√(x⁴ − p²x² + q²a²) = x² + px − qa: ровно 3 решения"""
    fipi = {'E1F91F': dict(p=2, q=3), '8C0C15': dict(p=4, q=8)}
    lo, hi, step = -10, 6, Fraction(1, 7)

    def aset(self, p):
        b = sp.Rational(-p['p'] ** 2, p['q'])
        return U(I.open(-oo, b), I.open(b, 0))

    def ok(self, p, a):
        pp, q = p['p'], p['q']
        Pt = Points()
        for r_ in poly_roots((x ** 2 + pp * x - q * a) ** 2 - (x ** 4 - pp ** 2 * x ** 2 + q ** 2 * a ** 2)):
            if r_ == INF:
                return False
            if ge(r_ ** 2 + pp * r_ - q * a):
                Pt.add(r_)
        return len(Pt) == 3

    def cond(self, p):
        pp, q = p['p'], p['q']
        return (f'Найдите все значения параметра $a$, при каждом из которых уравнение $$\\sqrt{{x^4-{pp * pp}x^2+{q * q}a^2}}=x^2+{pp}x-{q}a$$ '
                'имеет ровно 3 решения.')

    def solution(self, p):
        pp, q = p['p'], p['q']
        b = sp.Rational(-pp ** 2, q)
        return (
            f'Уравнение равносильно системе $x^2+{pp}x-{q}a\\ge0$, $x^4-{pp * pp}x^2+{q * q}a^2=(x^2+{pp}x-{q}a)^2$. Раскрываем квадрат: '
            f'$0={2 * pp * pp}x^2+{2 * pp}x^3-{2 * q}ax^2-{2 * pp * q}ax=2x\\bigl({pp}x^2+{pp * pp}x-{q}ax-{pp * q}a\\bigr)=2x(x+{pp})({pp}x-{q}a)$.\n\n'
            f'Корни $x=0$, $x=-{pp}$, $x=\\frac{{{q}a}}{{{pp}}}$. Проверим условие $x^2+{pp}x-{q}a\\ge0$: при $x=0$ и при $x=-{pp}$ оно даёт '
            f'$-{q}a\\ge0$, то есть $a\\le0$; при $x=\\frac{{{q}a}}{{{pp}}}$ получаем $\\frac{{{q * q}a^2}}{{{pp * pp}}}\\ge0$ — верно всегда.\n\n'
            f'Три решения будут, если $a\\le0$ и три корня различны: $\\frac{{{q}a}}{{{pp}}}\\ne0$ ($a\\ne0$) и $\\frac{{{q}a}}{{{pp}}}\\ne-{pp}$ '
            f'($a\\ne{tx(b)}$).')

    def sample(self, rng):
        pp = rng.randint(1, 6)
        return dict(p=pp, q=rng.randint(1, 9))


class SystemProductSqrt3(Param):
    """(xy² − 3xy − 3y + 9)√(3 − x) = 0, y = ax: ровно три решения"""
    fipi = {'56C747': {}}
    lo, hi, step = -5, 6, Fraction(1, 9)

    def aset(self, p):
        return U(I.Lopen(r(1, 3), 1), F(3))

    def ok(self, p, a):
        P = Points()
        P.add(3, 3 * a)
        if a != 0:                              # y = 3
            xr = 3 / a
            if ge(3 - xr):
                P.add(xr, 3)
        if a > 0:                               # xy = 3: a x² = 3
            for xr in (sp.sqrt(3 / a), -sp.sqrt(3 / a)):
                if ge(3 - xr):
                    P.add(xr, a * xr)
        return len(P) == 3

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}(xy^2-3xy-3y+9)\\sqrt{3-x}=0,\\\\ y=ax\\end{cases}$$ '
                'имеет ровно три различных решения.')

    def solution(self, p):
        return (
            '$xy^2-3xy-3y+9=xy(y-3)-3(y-3)=(y-3)(xy-3)$, ОДЗ: $x\\le3$. Решения системы — точки прямой $y=ax$, для которых $x=3$, или '
            '$y=3$, или $xy=3$ (при $x\\le3$).\n\n'
            '1) $x=3$: точка $(3;3a)$ — при любом $a$.\n\n'
            '2) $y=3$: $ax=3$, $x=\\frac3a\\le3$ — при $a<0$ или $a\\ge1$ (при $a=1$ это та же точка $(3;3)$).\n\n'
            '3) $xy=3$: $ax^2=3$ — при $a>0$, $x=\\pm\\sqrt{\\frac3a}$; условие $x\\le3$: для $x=-\\sqrt{\\frac3a}$ всегда, для $x=\\sqrt{\\frac3a}$ — '
            'при $a\\ge\\frac13$ (при $a=\\frac13$ это точка $(3;1)$, совпадающая с точкой из п. 1).\n\n'
            'Точка из п. 2 совпадает с точкой из п. 3, когда $y=3$ и $xy=3$, то есть $x=1$, $a=3$.\n\n'
            'Подсчёт: при $a\\le0$ — не более двух решений; при $0<a\\le\\frac13$ — два; при $\\frac13<a<1$ — три (п. 1 и две точки п. 3); '
            'при $a=1$ — три ($(3;3)$ и $(\\pm\\sqrt3;\\pm\\sqrt3)$); при $a>1$ — четыре, кроме $a=3$, где точки п. 2 и п. 3 совпадают — три.')


# ---------------------------------------------------------------------------
# Произведения с корнем и логарифмами на отрезке
# ---------------------------------------------------------------------------

class SqrtLogProduct(Param):
    """Семейство «корень × логарифмы»: каждое задание — свой набор функций"""
    lo, hi, step = -6, 6, Fraction(1, 6)
    KIND = {}

    def ok(self, p, a):
        k = self.KIND[p['kind']]
        return scan_roots(lambda t: k['F'](t, float(a)), k['lo'], k['hi'], 1500, points=k['points'](float(a))) == k['need']


def ssqrt(v):
    """Корень с допуском на округление: −1e−12 считаем нулём"""
    if abs(v) < 1e-12:
        return 0.0
    if v < 0:
        raise ValueError
    return math.sqrt(v)


def slog(v):
    """Логарифм с отбраковкой аргумента, неотличимого от нуля"""
    if v < 1e-12:
        raise ValueError
    return math.log(v)


def _safe(f):
    def g(t, a):
        try:
            return f(t, a)
        except (ValueError, ZeroDivisionError):
            return None
    return g


SQRTLOG = {
    'A22E40': dict(F=_safe(lambda t, a: ssqrt(2 - 3 * t) * (slog(16 * t * t - a * a) - slog(4 * t + a))), lo=-6.0, hi=2 / 3,
                   points=lambda a: [2 / 3, (a + 1) / 4], need=1),
    '9437D5': dict(F=_safe(lambda t, a: (5 * t - 2) * (slog(t + a) - slog(2 * t - a))), lo=0.0, hi=1.0,
                   points=lambda a: [0.0, 1.0, 0.4, 2 * a], need=1),
    '997C65': dict(F=_safe(lambda t, a: ssqrt(2 * t - 1) * (slog(4 * t - a) - slog(5 * t + a))), lo=0.0, hi=1.0,
                   points=lambda a: [0.5, 1.0, -2 * a], need=1),
    'C7C26F': dict(F=_safe(lambda t, a: (ssqrt(t + 2 * a) - (t - 1)) * slog(t - a)), lo=0.0, hi=1.0,
                   points=lambda a: [0.0, 1.0, a + 1], need=1),
    '9F53F5': dict(F=_safe(lambda t, a: ssqrt(4 * t - 1) * slog(t * t - 2 * t + 2 - a * a)), lo=0.0, hi=1.0,
                   points=lambda a: [0.25, 1.0, 1 - abs(a), 1 + abs(a)], need=1),
    '7F7EC4': dict(F=_safe(lambda t, a: ssqrt(7 * t - 4) * slog(t * t - 8 * t + 17 - a * a)), lo=0.0, hi=4.0,
                   points=lambda a: [4 / 7, 4.0, 4 - abs(a)], need=1),
    '3E3293': dict(F=_safe(lambda t, a: slog(4 * t - 1) * ssqrt(t * t - 6 * t + 6 * a - a * a)), lo=0.0, hi=3.0,
                   points=lambda a: [0.5, 3.0, a, 6 - a], need=1),
}


class SqrtLogEq(SqrtLogProduct):
    KIND = SQRTLOG
    fipi = {k: dict(kind=k) for k in SQRTLOG}

    SETS = {
        'A22E40': lambda: U(I.Lopen(r(-8, 3), r(-1, 2)), I.Ropen(r(5, 3), r(8, 3))),
        '9437D5': lambda: U(I.Lopen(r(-2, 5), 0), F(r(1, 5)), I.open(r(1, 2), r(4, 5))),
        '997C65': lambda: U(I.open(r(-5, 2), r(-1, 2)), I.Ropen(r(-1, 4), 2)),
        'C7C26F': lambda: U(F(r(-1, 2)), I(r(-1, 3), 0)),
        '9F53F5': lambda: U(I.Lopen(r(-5, 4), r(-3, 4)), I.Ropen(r(3, 4), r(5, 4))),
        '7F7EC4': lambda: U(I.Lopen(r(-25, 7), r(-24, 7)), I.Ropen(r(24, 7), r(25, 7))),
        '3E3293': lambda: U(I.Lopen(r(1, 4), r(1, 2)), I.Ropen(r(11, 2), r(23, 4))),
    }
    CONDS = {
        'A22E40': 'уравнение $$\\sqrt{2-3x}\\cdot\\ln(16x^2-a^2)=\\sqrt{2-3x}\\cdot\\ln(4x+a)$$ имеет ровно один корень.',
        '9437D5': 'уравнение $$(5x-2)\\cdot\\ln(x+a)=(5x-2)\\cdot\\ln(2x-a)$$ имеет ровно один корень на отрезке $[0;1]$.',
        '997C65': 'уравнение $$\\sqrt{2x-1}\\cdot\\ln(4x-a)=\\sqrt{2x-1}\\cdot\\ln(5x+a)$$ имеет ровно один корень на отрезке $[0;1]$.',
        'C7C26F': 'уравнение $$\\sqrt{x+2a}\\cdot\\ln(x-a)=(x-1)\\cdot\\ln(x-a)$$ имеет ровно один корень на отрезке $[0;1]$.',
        '9F53F5': 'уравнение $$\\sqrt{4x-1}\\cdot\\ln(x^2-2x+2-a^2)=0$$ имеет ровно один корень на отрезке $[0;1]$.',
        '7F7EC4': 'уравнение $$\\sqrt{7x-4}\\cdot\\ln(x^2-8x+17-a^2)=0$$ имеет на отрезке $[0;4]$ ровно один корень.',
        '3E3293': 'уравнение $$\\ln(4x-1)\\cdot\\sqrt{x^2-6x+6a-a^2}=0$$ имеет ровно один корень на отрезке $[0;3]$.',
    }
    TEXTS = {
        'A22E40': (
            'ОДЗ: $x\\le\\frac23$, $16x^2-a^2>0$, $4x+a>0$. Уравнение равносильно $\\sqrt{2-3x}\\bigl(\\ln(16x^2-a^2)-\\ln(4x+a)\\bigr)=0$.\n\n'
            '1) $x=\\frac23$ — корень, если в этой точке определены логарифмы: $\\frac{64}{9}-a^2>0$ и $\\frac83+a>0$, то есть $-\\frac83<a<\\frac83$.\n\n'
            '2) $16x^2-a^2=4x+a>0$: $(4x+a)(4x-a)=4x+a$, и так как $4x+a>0$, получаем $4x-a=1$, $x=\\frac{a+1}{4}$. Условия: '
            '$4x+a=2a+1>0$, то есть $a>-\\frac12$, и $x\\le\\frac23$, то есть $a\\le\\frac53$; при $a=\\frac53$ корень совпадает с $x=\\frac23$.\n\n'
            'Ровно один корень: при $-\\frac83<a\\le-\\frac12$ (только $x=\\frac23$), при $a=\\frac53$ (корни совпали) и при $\\frac53<a<\\frac83$ '
            '(только $x=\\frac23$). При $-\\frac12<a<\\frac53$ корней два, при $|a|\\ge\\frac83$ — ни одного.'),
        '9437D5': (
            'ОДЗ: $x+a>0$, $2x-a>0$. Уравнение: $(5x-2)\\bigl(\\ln(x+a)-\\ln(2x-a)\\bigr)=0$.\n\n'
            '1) $x=\\frac25$ — корень при $\\frac25+a>0$ и $\\frac45-a>0$: $-\\frac25<a<\\frac45$.\n\n'
            '2) $x+a=2x-a$, $x=2a$: условие $x+a=3a>0$ ($a>0$) и $x\\in[0;1]$ ($a\\le\\frac12$). При $a=\\frac15$ корень $2a=\\frac25$ совпадает с первым.\n\n'
            'Ровно один корень: $-\\frac25<a\\le0$; $a=\\frac15$; $\\frac12<a<\\frac45$.'),
        '997C65': (
            'ОДЗ: $x\\ge\\frac12$, $4x-a>0$, $5x+a>0$. Уравнение: $\\sqrt{2x-1}\\bigl(\\ln(4x-a)-\\ln(5x+a)\\bigr)=0$.\n\n'
            '1) $x=\\frac12$ — корень при $2-a>0$ и $\\frac52+a>0$: $-\\frac52<a<2$.\n\n'
            '2) $4x-a=5x+a$, $x=-2a$: нужно $4x-a=-9a>0$ ($a<0$) и $x\\in\\left[\\frac12;1\\right]$, то есть $-\\frac12\\le a\\le-\\frac14$. '
            'При $a=-\\frac14$ корень совпадает с $x=\\frac12$.\n\n'
            'Ровно один корень: $-\\frac52<a<-\\frac12$ и $-\\frac14\\le a<2$.'),
        'C7C26F': (
            'Уравнение: $\\bigl(\\sqrt{x+2a}-(x-1)\\bigr)\\ln(x-a)=0$, ОДЗ: $x-a>0$, $x+2a\\ge0$.\n\n'
            '1) $\\ln(x-a)=0$: $x=a+1$. На отрезке $[0;1]$ при $-1\\le a\\le0$; ОДЗ: $x+2a=3a+1\\ge0$, $a\\ge-\\frac13$. Итак, $a\\in\\left[-\\frac13;0\\right]$.\n\n'
            '2) $\\sqrt{x+2a}=x-1$: на $[0;1]$ правая часть неположительна, равенство возможно только при $x=1$ и $x+2a=0$, то есть $a=-\\frac12$; '
            'ОДЗ: $x-a=\\frac32>0$. При $a=-\\frac12$ корень $x=a+1=\\frac12$ не входит в ОДЗ, так что корень один.\n\n'
            'Ровно один корень на отрезке: $a=-\\frac12$ или $-\\frac13\\le a\\le0$.'),
        '9F53F5': (
            'ОДЗ: $x\\ge\\frac14$, $x^2-2x+2-a^2>0$.\n\n'
            '1) $x=\\frac14$ — корень, если логарифм определён: $\\frac{25}{16}-a^2>0$, $|a|<\\frac54$.\n\n'
            '2) $x^2-2x+2-a^2=1$: $(x-1)^2=a^2$, $x=1\\pm a$. На $\\left[\\frac14;1\\right]$ лежит $x=1-|a|$ при $|a|\\le\\frac34$; при $|a|=\\frac34$ он совпадает с $\\frac14$.\n\n'
            'Ровно один корень: $\\frac34\\le|a|<\\frac54$.'),
        '7F7EC4': (
            'ОДЗ: $x\\ge\\frac47$, $x^2-8x+17-a^2>0$.\n\n'
            '1) $x=\\frac47$ — корень, если $\\frac{625}{49}-a^2>0$, то есть $|a|<\\frac{25}{7}$.\n\n'
            '2) $(x-4)^2+1-a^2=1$: $x=4\\pm a$; на $\\left[\\frac47;4\\right]$ лежит $x=4-|a|$ при $|a|\\le\\frac{24}{7}$, при $|a|=\\frac{24}{7}$ он равен $\\frac47$.\n\n'
            'Ровно один корень: $\\frac{24}{7}\\le|a|<\\frac{25}{7}$.'),
        '3E3293': (
            'ОДЗ: $x>\\frac14$, $x^2-6x+6a-a^2\\ge0$.\n\n'
            '1) $\\ln(4x-1)=0$: $x=\\frac12$ — корень, если $\\frac14-3+6a-a^2\\ge0$, то есть $\\frac12\\le a\\le\\frac{11}{2}$.\n\n'
            '2) $x^2-6x+6a-a^2=0$: $(x-a)(x-6+a)=0$, $x=a$ или $x=6-a$. С учётом $x\\in\\left(\\frac14;3\\right]$: $x=a$ при $\\frac14<a\\le3$, '
            '$x=6-a$ при $3\\le a<\\frac{23}{4}$ (при $a=3$ корни совпадают).\n\n'
            'Совпадения с $x=\\frac12$: $a=\\frac12$ и $a=\\frac{11}{2}$. Ровно один корень: $\\frac14<a\\le\\frac12$ и $\\frac{11}{2}\\le a<\\frac{23}{4}$ '
            '(при $\\frac12<a<\\frac{11}{2}$ корней два).'),
    }

    def aset(self, p):
        return self.SETS[p['kind']]()

    def cond(self, p):
        return 'Найдите все значения $a$, при каждом из которых ' + self.CONDS[p['kind']]

    def solution(self, p):
        return self.TEXTS[p['kind']]


Y = sp.Symbol('y')
T = sp.Symbol('t')


def count_points(pieces) -> int:
    """pieces: [(многочлен от x, функция x → y, условие (x, y) → bool)]; одинаковые точки считаются один раз"""
    P = Points()
    for poly, yf, cond in pieces:
        for r_ in poly_roots(poly):
            if r_ == INF:
                return 10 ** 9
            y = yf(r_)
            if cond(r_, y):
                P.add(r_, y)
    return len(P)


class SystemXAbsY(Param):
    """x + ay + a − 2 = 0, x|y| + x − 2 = 0: единственное решение"""
    fipi = {'ABE248': {}}
    lo, hi, step = -6, 6, Fraction(1, 8)

    def aset(self, p):
        return U(I(-oo, 0), I.open(r(1, 2), oo))

    def ok(self, p, a):
        P = Points()
        for r_ in poly_roots(a * (Y + 1) ** 2 - 2 * Y, Y):       # y ≥ 0
            if r_ == INF:
                return False
            if ge(r_):
                P.add(r_)
        for r_ in poly_roots(a * (1 - Y ** 2) + 2 * Y, Y):       # y < 0
            if r_ == INF:
                return False
            if num(r_) < -1e-30:
                P.add(r_)
        return len(P) == 1

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}x+ay+a-2=0,\\\\ x|y|+x-2=0\\end{cases}$$ '
                'имеет единственное решение.')

    def solution(self, p):
        return (
            'Из второго уравнения $x=\\frac{2}{|y|+1}$, поэтому каждому $y$ соответствует одно $x$, и число решений системы равно числу корней '
            'уравнения $\\frac{2}{|y|+1}=2-a(y+1)$.\n\n'
            'При $y\\ge0$: $2=2(y+1)-a(y+1)^2$, то есть $ay^2+(2a-2)y+a=0$. При $y<0$: $2=2(1-y)-a(1-y^2)$, то есть $ay^2-2y-a=0$.\n\n'
            '$a=0$: первое уравнение даёт $y=0$, второе — $y=0$, но $0\\not<0$. Решение одно.\n\n'
            '$a\\ne0$: уравнение $ay^2-2y-a=0$ имеет дискриминант $4+4a^2>0$ и произведение корней $-1$, так что ровно один его корень '
            'отрицателен — одно решение есть всегда. Решение единственно, если у $ay^2+(2a-2)y+a=0$ нет неотрицательных корней. '
            'Его дискриминант $4-8a$, произведение корней $1$, сумма $\\frac{2-2a}{a}$.\n\n'
            '- $a>\\frac12$: корней нет.\n- $0<a\\le\\frac12$: корни положительны — решений больше одного.\n'
            '- $a<0$: сумма корней отрицательна, произведение положительно — оба корня отрицательны, подходящих нет.\n\n'
            'Итак, $a\\le0$ или $a>\\frac12$.')


class QuarticCircleLine(Param):
    """x⁴ + y² = a², x² + y = |2a − 4|: ровно четыре решения"""
    fipi = {'EE054F': {}}
    lo, hi, step = -4, 10, Fraction(1, 8)

    def aset(self, p):
        return U(I.open(4 - 2 * S(2), r(4, 3)), I.open(4, 4 + 2 * S(2)))

    def ok(self, p, a):
        c = abs(2 * a - 4)
        n = 0
        P = Points()
        for u in poly_roots(2 * T ** 2 - 2 * c * T + c ** 2 - a ** 2, T):
            if u == INF:
                return False
            if gt(u):
                P.add(sp.sqrt(u), c - u)
                P.add(-sp.sqrt(u), c - u)
            elif ge(u) and num(u) < 1e-30:
                P.add(0, c)
        return len(P) == 4

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}x^4+y^2=a^2,\\\\ x^2+y=|2a-4|\\end{cases}$$ '
                'имеет ровно четыре различных решения.')

    def solution(self, p):
        return (
            'Пусть $u=x^2\\ge0$, $c=|2a-4|\\ge0$. Система: $u^2+y^2=a^2$, $u+y=c$. Каждому решению $(u;y)$ с $u>0$ соответствуют два решения '
            'исходной системы ($x=\\pm\\sqrt u$), с $u=0$ — одно. Четыре решения будут, только если уравнение '
            '$u^2+(c-u)^2=a^2$, то есть $2u^2-2cu+c^2-a^2=0$, имеет два различных положительных корня:\n\n'
            '$D/4=2a^2-c^2>0$, сумма $c>0$, произведение $\\frac{c^2-a^2}{2}>0$. Итак, $a^2<c^2<2a^2$.\n\n'
            '$c^2>a^2$: $(2a-4)^2>a^2$, $3a^2-16a+16>0$, $a<\\frac43$ или $a>4$.\n\n'
            '$c^2<2a^2$: $(2a-4)^2<2a^2$, $a^2-8a+8<0$, $4-2\\sqrt2<a<4+2\\sqrt2$.\n\n'
            'Пересечение: $4-2\\sqrt2<a<\\frac43$ или $4<a<4+2\\sqrt2$.')


class VShapeLens(Param):
    """y = |x − a| − 4, 4|y| + x² + 8x = 0: ровно четыре решения"""
    fipi = {'DA9BFE': {}}
    lo, hi, step = -15, 7, Fraction(1, 7)

    def aset(self, p):
        return U(I.open(-5, -4), I.open(-4, -3))

    def ok(self, p, a):
        pieces = []
        for s1 in (1, -1):
            for s2 in (1, -1):
                pieces.append((x ** 2 / 4 + (2 + s1 * s2) * x - s2 * (s1 * a + 4),
                               (lambda s1: lambda t: s1 * (t - a) - 4)(s1),
                               (lambda s1, s2: lambda t, y: ge(s1 * (t - a)) and ge(s2 * y))(s1, s2)))
        return count_points(pieces) == 4

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}y=|x-a|-4,\\\\ 4|y|+x^2+8x=0\\end{cases}$$ '
                'имеет ровно четыре различных решения.')

    def solution(self, p):
        return (
            'Второе уравнение: $|y|=\\frac{16-(x+4)^2}{4}$ — «линза» из двух дуг парабол $y=\\pm\\left(4-\\frac{(x+4)^2}{4}\\right)$ при '
            '$-8\\le x\\le0$ с угловыми точками $(-8;0)$, $(0;0)$, верхней точкой $(-4;4)$ и нижней $(-4;-4)$. Первое уравнение — «уголок» с '
            'вершиной $(a;-4)$ на прямой $y=-4$ (она касается нижней дуги в точке $(-4;-4)$), стороны уголка имеют наклоны $\\pm1$.\n\n'
            'Найдём положения, при которых меняется число общих точек.\n\n'
            '- Правая сторона $y=x-a-4$ касается верхней дуги $y=-\\frac{x^2}{4}-2x$: $\\frac{x^2}{4}+3x-a-4=0$, $D=0$ при $a=-13$.\n'
            '- Уголок проходит через угловые точки: левая сторона через $(-8;0)$ при $a=-4$, правая — через $(0;0)$ при $a=-4$ и через '
            '$(-8;0)$ при $a=-12$; вершина в нижней точке $(-4;-4)$ при $a=-4$.\n'
            '- Левая сторона $y=-x+a-4$ касается нижней дуги $y=\\frac{x^2}{4}+2x$: $\\frac{x^2}{4}+3x-a+4=0$, $D=0$ при $a=-5$; '
            'правая сторона касается нижней дуги ($\\frac{x^2}{4}+x+a+4=0$) при $a=-3$; левая сторона касается верхней дуги при $a=5$.\n\n'
            'Перемещая вершину по прямой $y=-4$ слева направо и считая точки пересечения, получаем: при $a<-13$ — нет решений, при $a=-13$ — одно, '
            'при $-13<a<-5$ — два, при $a=-5$ — три, при $-5<a<-4$ — четыре, при $a=-4$ — три, при $-4<a<-3$ — четыре, при $a=-3$ — три, '
            'при $-3<a<5$ — два, при $a=5$ — одно, при $a>5$ — нет.')


class CircleTwoLines(Param):
    """Окружность радиуса 1 с центром (2a + 2; a) и прямые y = ±x: ровно четыре решения"""
    fipi = {'CDB8F3': {}}
    lo, hi, step = -4, 2, Fraction(1, 17)

    def aset(self, p):
        return U(I.open((-2 - S(2)) / 3, -1), I.open(-1, r(-3, 5)), I.open(r(-3, 5), S(2) - 2))

    def ok(self, p, a):
        circ = lambda X_, Y_: X_ ** 2 + Y_ ** 2 - 4 * (a + 1) * X_ - 2 * a * Y_ + 5 * a ** 2 + 8 * a + 3  # noqa: E731
        return count_points([(circ(x, x), lambda t: t, lambda t, y: True), (circ(x, -x), lambda t: -t, lambda t, y: True)]) == 4

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений '
                '$$\\begin{cases}x^2+y^2-4(a+1)x-2ay+5a^2+8a+3=0,\\\\ y^2=x^2\\end{cases}$$ имеет ровно четыре различных решения.')

    def solution(self, p):
        return (
            'Первое уравнение: $(x-2a-2)^2+(y-a)^2=1$ — окружность радиуса 1 с центром $Q(2a+2;a)$. Второе — пара прямых $y=x$ и $y=-x$, '
            'пересекающихся в начале координат. Четыре решения будут, если окружность пересекает каждую прямую в двух точках и не проходит '
            'через их общую точку $O(0;0)$.\n\n'
            'Расстояние от $Q$ до $y=x$: $\\frac{|a+2|}{\\sqrt2}<1$, $-2-\\sqrt2<a<-2+\\sqrt2$. До $y=-x$: $\\frac{|3a+2|}{\\sqrt2}<1$, '
            '$\\frac{-2-\\sqrt2}{3}<a<\\frac{-2+\\sqrt2}{3}$. Пересечение: $\\frac{-2-\\sqrt2}{3}<a<\\sqrt2-2$.\n\n'
            'Окружность проходит через $O$, если $(2a+2)^2+a^2=1$, то есть $5a^2+8a+3=0$, $a=-1$ или $a=-\\frac35$ — оба значения из найденного '
            'промежутка, их исключаем.')


class FactorPoly(Param):
    """Уравнение, раскладывающееся на множители: ровно два различных корня"""
    lo, hi, step = -8, 8, Fraction(1, 6)
    DATA = {
        'e76FF5': dict(eq=lambda a: (x ** 2 - x) * a ** 2 + (x ** 4 - x ** 3 - x + 1) * a - x ** 3 + x ** 2,
                       tex='\\left(x^2-x\\right)a^2+\\left(x^4-x^3-x+1\\right)a-x^3+x^2=0',
                       fac='(x-1)(ax-1)(x^2+a)', ans=lambda: U(F(-1), I.Ropen(0, 1), I.open(1, oo)),
                       roots='$x=1$; $x=\\frac1a$ (при $a\\ne0$); $x=\\pm\\sqrt{-a}$ (при $a\\le0$)',
                       cases=('При $a>0$: корни $1$ и $\\frac1a$ — два, если $a\\ne1$. При $a=0$: $(x-1)\\cdot(-1)\\cdot x^2=0$ — корни $1$ и $0$. '
                              'При $a<0$: четыре числа $1$, $\\frac1a<0$, $\\pm\\sqrt{-a}$; совпадения возможны только при $\\sqrt{-a}=1$ '
                              'или $\\frac1a=-\\sqrt{-a}$, то есть при $a=-1$: тогда корни $1$ и $-1$ — два.')),
        '4B165e': dict(eq=lambda a: (x ** 2 - x) * a ** 2 - (x ** 4 - x ** 3 - x + 1) * a - x ** 3 + x ** 2,
                       tex='\\left(x^2-x\\right)a^2-\\left(x^4-x^3-x+1\\right)a-x^3+x^2=0',
                       fac='(x-1)(ax+1)(a-x^2)', ans=lambda: U(I.open(-oo, -1), I.Lopen(-1, 0), F(1)),
                       roots='$x=1$; $x=-\\frac1a$ (при $a\\ne0$); $x=\\pm\\sqrt a$ (при $a\\ge0$)',
                       cases=('При $a<0$: корни $1$ и $-\\frac1a>0$ — два, если $a\\ne-1$. При $a=0$: корни $1$ и $0$. При $a>0$: четыре числа '
                              '$1$, $-\\frac1a<0$, $\\pm\\sqrt a$, совпадения только при $a=1$: корни $1$ и $-1$.')),
        'FD16D2': dict(eq=lambda a: (x - 1) * a ** 2 - (x ** 3 - 2 * x ** 2 + 3 * x - 2) * a - x ** 4 + 3 * x ** 3 - 2 * x ** 2,
                       tex='(x-1)a^2-(x^3-2x^2+3x-2)a-x^4+3x^3-2x^2=0',
                       fac='(x-1)(a-x^2)(a+x-2)', ans=lambda: U(I.open(-oo, 0), F(1)),
                       roots='$x=1$; $x=2-a$; $x=\\pm\\sqrt a$ (при $a\\ge0$)',
                       cases=('При $a<0$: корни $1$ и $2-a>2$ — два. При $a=0$: $1$, $2$, $0$ — три. При $a>0$: числа $1$, $2-a$, $\\pm\\sqrt a$; '
                              'совпадения: $2-a=1$ или $\\sqrt a=1$ при $a=1$ (корни $1$, $-1$ — два), $2-a=-\\sqrt a$ при $a=4$ (корни $1$, $\\pm2$ — три); '
                              'в остальных случаях корней больше двух.')),
        '5F6c59': dict(eq=lambda a: (x + 1) * a ** 2 + x * (x + 1) ** 2 * a + x ** 4 + 2 * x ** 3 - 2 * x - 1,
                       tex='(x+1)a^2+x(x+1)^2a+x^4+2x^3-2x-1=0',
                       fac='(x+1)(a+x^2-1)(a+x+1)', ans=lambda: U(F(0), I.open(1, oo)),
                       roots='$x=-1$; $x=-a-1$; $x=\\pm\\sqrt{1-a}$ (при $a\\le1$)',
                       cases=('При $a>1$: корни $-1$ и $-a-1$ — два. При $a=1$: $-1$, $-2$, $0$ — три. При $a<1$: числа $-1$, $-a-1$, $\\pm\\sqrt{1-a}$; '
                              'совпадения: при $a=0$ — корни $-1$ и $1$ (два); при $a=-3$ — корни $-1$, $\\pm2$ (три); иначе четыре.')),
        'AeA2cF': dict(eq=lambda a: (x - 2) * a ** 2 + (x ** 3 - x ** 2 - 4) * a + x ** 4 - 4 * x ** 2,
                       tex='(x-2)a^2+(x^3-x^2-4)a+x^4-4x^2=0',
                       fac='(x-2)(a+x^2)(a+x+2)', ans=lambda: U(F(-4), I.open(0, oo)),
                       roots='$x=2$; $x=-a-2$; $x=\\pm\\sqrt{-a}$ (при $a\\le0$)',
                       cases=('При $a>0$: корни $2$ и $-a-2$ — два. При $a=0$: $2$, $-2$, $0$ — три. При $a<0$: числа $2$, $-a-2$, $\\pm\\sqrt{-a}$; '
                              'совпадения: при $a=-4$ — корни $2$, $-2$ (два); при $a=-1$ — $2$, $\\pm1$ (три); иначе четыре.')),
        'F7e0eA': dict(eq=lambda a: x ** 4 - x ** 3 - 3 * x ** 2 - x + a * (x + 1) * x - (3 * x ** 3 - 3 * x ** 2 - 9 * x - 3 + 3 * a * (x + 1)),
                       tex='x^4-x^3-3x^2-x+a(x+1)x=3x^3-3x^2-9x-3+3a(x+1)',
                       fac='(x+1)(x-3)(x^2-2x+a-1)', ans=lambda: U(F(-2), I.open(2, oo)),
                       roots='$x=-1$; $x=3$; $x=1\\pm\\sqrt{2-a}$ (при $a\\le2$)',
                       cases=('Корни $-1$ и $3$ есть всегда. При $a>2$ других нет — два корня. При $a=2$ добавляется $x=1$. При $a<2$ корни $1\\pm\\sqrt{2-a}$ '
                              'совпадают с $-1$ и $3$ только при $\\sqrt{2-a}=2$, $a=-2$ — тогда корней два.')),
        '8F4718': dict(eq=lambda a: a * x ** 4 - 2 * x ** 3 + (a ** 3 - a) * x ** 2 - (2 * a ** 2 - 2) * x - (-a * x ** 3 + 2 * x ** 2 - (a ** 3 - a) * x + 2 * a ** 2 - 2),
                       tex='ax^4-2x^3+\\left(a^3-a\\right)x^2-\\left(2a^2-2\\right)x=-ax^3+2x^2-\\left(a^3-a\\right)x+2a^2-2',
                       fac='(x+1)(ax-2)(x^2+a^2-1)', ans=lambda: U(I.open(-oo, -2), I.open(-2, -1), F(0), I.open(1, oo)),
                       roots='$x=-1$; $x=\\frac2a$ (при $a\\ne0$); $x=\\pm\\sqrt{1-a^2}$ (при $|a|\\le1$)',
                       cases=('$a=0$: $(x+1)(-2)(x^2-1)=0$ — корни $\\pm1$, два. $|a|>1$: корни $-1$ и $\\frac2a$ — два, кроме $a=-2$ (совпадают). '
                              '$|a|=1$: добавляется $x=0$ — три. $0<|a|<1$: $\\left|\\frac2a\\right|>2$, $0<\\sqrt{1-a^2}<1$ — четыре различных корня.')),
    }
    fipi = {k: dict(kind=k) for k in DATA}

    def aset(self, p):
        return self.DATA[p['kind']]['ans']()

    def ok(self, p, a):
        return roots_count(self.DATA[p['kind']]['eq'](a)) == 2

    def cond(self, p):
        return f'Найдите все значения $a$, при каждом из которых уравнение $${self.DATA[p["kind"]]["tex"]}$$ имеет ровно два различных корня.'

    def solution(self, p):
        d = self.DATA[p['kind']]
        return (f'Перенесём всё в левую часть и сгруппируем слагаемые (удобно рассматривать выражение как многочлен от $a$ или выделить общий '
                f'множитель). Левая часть раскладывается на множители: $${d["fac"]}=0.$$\n\nКорни: {d["roots"]}.\n\n{d["cases"]}')


class AbsParabolas(Param):
    """x + y = a, |y| = |x² − 2x|: ровно два решения"""
    fipi = {'7B510F': {}}
    lo, hi, step = -3, 4, Fraction(1, 13)

    def aset(self, p):
        return U(I.open(-oo, r(-1, 4)), I.open(r(9, 4), oo))

    def ok(self, p, a):
        return count_points([(a - x - (x ** 2 - 2 * x), lambda t: a - t, lambda t, y: True),
                             (a - x + (x ** 2 - 2 * x), lambda t: a - t, lambda t, y: True)]) == 2

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}x+y=a,\\\\ |y|=|x^2-2x|\\end{cases}$$ '
                'имеет ровно два различных решения.')

    def solution(self, p):
        return (
            'Подставим $y=a-x$: $|a-x|=|x^2-2x|$, то есть $a-x=x^2-2x$ или $a-x=2x-x^2$: $$a=x^2-x\\quad\\text{или}\\quad a=3x-x^2.$$ '
            'Каждому корню $x$ соответствует одно решение системы, поэтому считаем точки пересечения прямой $y=a$ с объединением парабол '
            '$y=x^2-x$ (вершина $\\left(\\frac12;-\\frac14\\right)$) и $y=3x-x^2$ (вершина $\\left(\\frac32;\\frac94\\right)$). Параболы пересекаются '
            'в точках с $x=0$ ($y=0$) и $x=2$ ($y=2$).\n\n'
            'При $a<-\\frac14$ общих точек две (только вторая парабола), при $a=-\\frac14$ — три, при $-\\frac14<a<\\frac94$ — четыре '
            '(при $a=0$ и $a=2$ — три из-за общих точек парабол), при $a=\\frac94$ — три, при $a>\\frac94$ — две.')


class SegmentSystem(Param):
    """Система неравенств имеет решение на отрезке"""
    lo, hi, step = -6, 6, Fraction(1, 11)
    DATA = {
        'BB4A02': dict(seg=(4, 5), conds=lambda a, t: 2 * a <= t and 6 * t > t * t + a * a and t + a <= 6,
                       tex='\\begin{cases}2a\\le x,\\\\ 6x>x^2+a^2,\\\\ x+a\\le6\\end{cases}', ans=lambda: I.Lopen(-2 * S(2), 2),
                       text=('Для $x\\in[4;5]$ система означает: $a\\le\\frac x2$, $|a|<\\sqrt{6x-x^2}$, $a\\le6-x$. На отрезке $\\frac x2\\ge2\\ge6-x$, '
                             'поэтому остаются условия $-\\sqrt{6x-x^2}<a\\le6-x$. Функция $6x-x^2$ убывает на $[4;5]$, а $6-x$ тоже убывает, поэтому '
                             'шире всего промежуток при $x=4$: $-2\\sqrt2<a\\le2$. При любом таком $a$ число $x=4$ — решение, а при других $a$ решений '
                             'на отрезке нет (при $x>4$ промежуток для $a$ лежит внутри найденного).')),
        'AD93BF': dict(seg=(4, 5), conds=lambda a, t: a * (t - 1) >= 4 and 2 * math.sqrt(t - 2) >= a and 3 * t < a + 14,
                       tex='\\begin{cases}a(x-1)\\ge4,\\\\ 2\\sqrt{x-2}\\ge a,\\\\ 3x<a+14\\end{cases}', ans=lambda: I.Lopen(1, 2 * S(3)),
                       text=('Для $x\\in[4;5]$: $a\\ge\\frac{4}{x-1}$, $a\\le2\\sqrt{x-2}$, $a>3x-14$. На отрезке $\\frac{4}{x-1}\\ge1$ и $3x-14\\le1$, '
                             'причём при $x=5$ оба ограничения дают $a\\ge1$ и $a>1$. Наибольшая верхняя граница $2\\sqrt3$ — при $x=5$. '
                             'При $x=5$ система выполнена для $1<a\\le2\\sqrt3$; при $a\\le1$ первое и третье неравенства несовместны на отрезке '
                             '(при $x<5$ нужно $a\\ge\\frac{4}{x-1}>1$), а при $a>2\\sqrt3$ нарушается второе.')),
        '8257C0': dict(seg=(3, 4), conds=lambda a, t: a * t >= 2 and math.sqrt(t - 1) > a and 3 * t <= 2 * a + 11,
                       tex='\\begin{cases}ax\\ge2,\\\\ \\sqrt{x-1}>a,\\\\ 3x\\le2a+11\\end{cases}', ans=lambda: I.Ropen(r(1, 2), S(3)),
                       text=('Для $x\\in[3;4]$: $a\\ge\\frac2x$, $a<\\sqrt{x-1}$, $a\\ge\\frac{3x-11}{2}$. Нижние границы $\\frac2x$ и $\\frac{3x-11}{2}$ '
                             'при $x=4$ обе равны $\\frac12$, при $x<4$ первая больше $\\frac12$. Верхняя граница $\\sqrt{x-1}$ наибольшая при $x=4$. '
                             'Значит, при $x=4$ получаем $\\frac12\\le a<\\sqrt3$, а другие $x$ новых значений не дают.')),
        '456B95': dict(seg=(1, 2), conds=lambda a, t: t <= 2 * a + 6 and 6 * t >= t * t + a * a and t + a > 0,
                       tex='\\begin{cases}x\\le2a+6,\\\\ 6x\\ge x^2+a^2,\\\\ x+a>0\\end{cases}', ans=lambda: I.Lopen(-2, 2 * S(2)),
                       text=('Для $x\\in[1;2]$: $a\\ge\\frac{x-6}{2}$, $|a|\\le\\sqrt{6x-x^2}$, $a>-x$. На отрезке $-x\\ge\\frac{x-6}{2}$ и '
                             '$-x>-\\sqrt{6x-x^2}$, так что условия: $-x<a\\le\\sqrt{6x-x^2}$. Обе границы наиболее широки при $x=2$: $-2<a\\le2\\sqrt2$.')),
    }
    fipi = {k: dict(kind=k) for k in DATA}

    def aset(self, p):
        return self.DATA[p['kind']]['ans']()

    def ok(self, p, a):
        d = self.DATA[p['kind']]
        lo, hi = d['seg']
        av = float(a)
        for i in range(0, 3001):
            t = lo + (hi - lo) * i / 3000
            try:
                if d['conds'](av, t):
                    return True
            except ValueError:
                pass
        return False

    def cond(self, p):
        d = self.DATA[p['kind']]
        return (f'Найдите все значения $a$, при каждом из которых система неравенств $${d["tex"]}$$ имеет хотя бы одно решение на отрезке '
                f'$[{d["seg"][0]};{d["seg"][1]}]$.')

    def solution(self, p):
        return self.DATA[p['kind']]['text']


class QuadraticInT(Param):
    """a(x + 4/x)² + 2(x + 4/x) − 25a + 10 = 0: ровно два различных корня"""
    fipi = {'11D603': {}}
    lo, hi, step = -3, 4, Fraction(1, 17)

    def aset(self, p):
        return U(F(0, r(1, 5)), I.open(r(2, 9), 2))

    def ok(self, p, a):
        P = Points()
        for r_ in poly_roots(a * (x ** 2 + 4) ** 2 + 2 * x * (x ** 2 + 4) + (10 - 25 * a) * x ** 2):
            if r_ == INF:
                return False
            if abs(num(r_)) > 1e-30:
                P.add(r_)
        return len(P) == 2

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых уравнение $$a\\left(x+\\frac4x\\right)^2+2\\left(x+\\frac4x\\right)-25a+10=0$$ '
                'имеет ровно два различных корня.')

    def solution(self, p):
        return (
            'Пусть $t=x+\\frac4x$. Уравнение $x+\\frac4x=t$, то есть $x^2-tx+4=0$, имеет два корня при $|t|>4$, один при $|t|=4$ и ни одного при '
            '$|t|<4$; разным $t$ соответствуют разные $x$.\n\n'
            'Уравнение $at^2+2t-25a+10=0$ раскладывается: $(t+5)(at-5a+2)=0$. Корень $t=-5$ есть всегда и даёт два корня $x$ ($x=-1$, $x=-4$). '
            'Значит, второй множитель не должен давать новых корней.\n\n'
            '- $a=0$: остаётся $t=-5$ — подходит.\n'
            '- $a\\ne0$: $t=5-\\frac2a$. Новых $x$ нет, если $|t|<4$: $1<\\frac2a<9$, $\\frac29<a<2$, или если $t=-5$: $a=\\frac15$.')


class ExpCircleSymmetric(Param):
    """2^{|x|+3} + 7|x| + 1 = 8y + 7x² + a, x² + y² = 1: единственное решение"""
    fipi = {'907104': {}}
    lo, hi, step = -10, 25, Fraction(1, 2)

    def aset(self, p):
        return F(1)

    def ok(self, p, a):
        av = float(a)
        n = 0
        roots = set()
        for sgn in (1, -1):
            f = lambda t: 2 ** (abs(t) + 3) + 7 * abs(t) + 1 - 8 * sgn * math.sqrt(max(0.0, 1 - t * t)) - 7 * t * t - av  # noqa: E731
            xs = [-1 + 2 * i / 4000 for i in range(4001)]
            vals = [f(t) for t in xs]
            for t, v in zip(xs, vals):
                if abs(v) < 1e-9:
                    roots.add((round(t, 6), round(sgn * math.sqrt(max(0.0, 1 - t * t)), 6)))
            for (t1, v1), (t2, v2) in zip(zip(xs, vals), zip(xs[1:], vals[1:])):
                if abs(v1) > 1e-9 and abs(v2) > 1e-9 and (v1 > 0) != (v2 > 0):
                    roots.add((round((t1 + t2) / 2, 7), sgn))
        return len(roots) == 1

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система $$\\begin{cases}2^{|x|+3}+7|x|+1=8y+7x^2+a,\\\\ x^2+y^2=1\\end{cases}$$ '
                'имеет единственное решение.')

    def solution(self, p):
        return (
            'Если $(x_0;y_0)$ — решение, то и $(-x_0;y_0)$ — решение (в систему входят только $|x|$ и $x^2$). Поэтому единственным решение может '
            'быть, только если $x_0=0$. Тогда $y_0=\\pm1$ и $9=8y_0+a$: $a=1$ (при $y_0=1$) или $a=17$ (при $y_0=-1$).\n\n'
            '$a=1$: пусть $u=|x|\\in[0;1]$. Первое уравнение: $8\\cdot2^u+7u=8y+7u^2$. Так как $y\\le1$, правая часть не больше $8+7u^2$, а '
            '$8\\cdot2^u+7u-8-7u^2=8(2^u-1)+7u(1-u)\\ge0$, причём равенство только при $u=0$, $y=1$. Решение единственно.\n\n'
            '$a=17$: точки $(\\pm1;0)$ тоже являются решениями: $2^4+7+1=24=7+17$. Решений не меньше трёх.\n\n'
            'Ответ: $a=1$.')


class CircleTwoLinesProduct(Param):
    """Окружность и пара прямых x = 1, y = x (или y = 1, x = 1): ровно четыре решения"""
    lo, hi, step = -5, 5, Fraction(1, 9)
    DATA = {
        '45927B': dict(circle=lambda a, X_, Y_: a * X_ ** 2 + a * Y_ ** 2 - (2 * a - 5) * X_ + 2 * a * Y_ + 1,
                       lines=[('x1', 1), ('yx', None)], ans=lambda: U(I.open(-oo, -3), I.open(-3, 0), I.open(3, r(25, 8))),
                       tex='\\begin{cases}ax^2+ay^2-(2a-5)x+2ay+1=0,\\\\ x^2+y=xy+x\\end{cases}',
                       text=('Второе уравнение: $x^2-x+y-xy=(x-1)(x-y)=0$ — прямые $x=1$ и $y=x$, пересекающиеся в точке $(1;1)$.\n\n'
                             'При $a=0$ первое уравнение даёт $x=-\\frac15$ — одно решение.\n\n'
                             'При $a\\ne0$ на прямой $x=1$: $ay^2+2ay+5-a+1-2a+5\\cdot0=0$, после упрощения $(y+1)^2=2-\\frac6a$ — два корня при $2-\\frac6a>0$, '
                             'то есть $a<0$ или $a>3$. На прямой $y=x$: $2ax^2+5x+1=0$ — два корня при $25-8a>0$, $a<\\frac{25}{8}$.\n\n'
                             'Четыре решения: $a<0$ или $3<a<\\frac{25}{8}$, причём окружность не должна проходить через общую точку прямых $(1;1)$: '
                             '$a+a-(2a-5)+2a+1=2a+6=0$, $a=-3$ — исключаем.')),
        'D5A8E6': dict(circle=lambda a, X_, Y_: a * X_ ** 2 + a * Y_ ** 2 + 2 * a * X_ + (a + 2) * Y_ + 1,
                       lines=[('x1', 1), ('y1', 1)], ans=lambda: U(I.open(-2 * S(11) / 11, r(-3, 5)), I.open(r(-3, 5), 0)),
                       tex='\\begin{cases}ax^2+ay^2+2ax+(a+2)y+1=0,\\\\ xy+1=x+y\\end{cases}',
                       text=('Второе уравнение: $(x-1)(y-1)=0$ — прямые $x=1$ и $y=1$ с общей точкой $(1;1)$.\n\n'
                             'При $a=0$: $2y+1=0$ — одно решение $\\left(1;-\\frac12\\right)$.\n\n'
                             'При $a\\ne0$ на прямой $x=1$: $y^2+\\left(1+\\frac2a\\right)y+3+\\frac1a=0$, дискриминант $\\frac{4}{a^2}-11>0$ при '
                             '$|a|<\\frac{2}{\\sqrt{11}}$. На прямой $y=1$: $x^2+2x+2+\\frac3a=0$, дискриминант $-4-\\frac{12}{a}>0$ при $-3<a<0$.\n\n'
                             'Четыре решения: $-\\frac{2}{\\sqrt{11}}<a<0$, если окружность не проходит через $(1;1)$: $5a+3=0$, $a=-\\frac35$ — '
                             'исключаем (оно лежит в промежутке, так как $\\frac35<\\frac{2}{\\sqrt{11}}$).')),
    }
    fipi = {k: dict(kind=k) for k in DATA}

    def aset(self, p):
        return self.DATA[p['kind']]['ans']()

    def ok(self, p, a):
        d = self.DATA[p['kind']]
        c = d['circle']
        pieces = []
        for kind, v in d['lines']:
            if kind == 'x1':      # x = 1: многочлен от y, решаем относительно «x» как y
                pieces.append((c(a, sp.Integer(1), x), None, 'x1'))
            elif kind == 'y1':
                pieces.append((c(a, x, sp.Integer(1)), None, 'y1'))
            else:
                pieces.append((c(a, x, x), None, 'yx'))
        P = Points()
        for poly, _, kind in pieces:
            for r_ in poly_roots(poly):
                if r_ == INF:
                    return False
                pt = {'x1': (1, r_), 'y1': (r_, 1), 'yx': (r_, r_)}[kind]
                P.add(*pt)
        return len(P) == 4

    def cond(self, p):
        return f'Найдите все значения $a$, при каждом из которых система уравнений $${self.DATA[p["kind"]]["tex"]}$$ имеет ровно четыре различных решения.'

    def solution(self, p):
        return self.DATA[p['kind']]['text']


class AbsTwoCircles(Param):
    """x² + a² ∓ x − 7a = |7x ∓ a|: дуги двух окружностей в плоскости (x; a)"""
    fipi = {'44907E': dict(sign=-1, ask='two'), 'EDB7D3': dict(sign=1, ask='more')}
    lo, hi, step = -3, 10, Fraction(1, 9)

    def aset(self, p):
        if p['ask'] == 'two':
            return U(I.open(-2, -1), I.open(0, 7), I.open(8, 9))
        return U(I(-1, 0), I(7, 8))

    def ok(self, p, a):
        s = p['sign']
        P = Points()
        # x² + a² + s·x − 7a = |7x + s·a|
        for poly, cond in ((x ** 2 + a ** 2 + s * x - 7 * a - (7 * x - s * (-a) * 1 if False else 7 * x + s * a), lambda t: ge(7 * t + s * a)),
                           (x ** 2 + a ** 2 + s * x - 7 * a + (7 * x + s * a), lambda t: num(7 * t + s * a) < 1e-30)):
            for r_ in poly_roots(poly):
                if r_ == INF:
                    return False
                if cond(r_):
                    P.add(r_)
        n = len(P)
        return n == 2 if p['ask'] == 'two' else n > 2

    def cond(self, p):
        if p['sign'] == -1:
            return ('Найдите все значения $a$, при каждом из которых уравнение $$x^2+a^2-x-7a=|7x-a|$$ имеет ровно два различных корня.')
        return ('Найдите все значения $a$, при каждом из которых уравнение $$x^2+a^2+x-7a=|7x+a|$$ имеет больше двух различных корней.')

    def solution(self, p):
        if p['sign'] == -1:
            eqs = ('$7x-a\\ge0$: $x^2-8x+a^2-6a=0$, то есть $(x-4)^2+(a-3)^2=25$;\n'
                   '$7x-a<0$: $x^2+6x+a^2-8a=0$, то есть $(x+3)^2+(a-4)^2=25$.')
            line, pts = 'a=7x', '$(0;0)$ и $(1;7)$'
        else:
            eqs = ('$7x+a\\ge0$: $x^2-6x+a^2-8a=0$, то есть $(x-3)^2+(a-4)^2=25$;\n'
                   '$7x+a<0$: $x^2+8x+a^2-6a=0$, то есть $(x+4)^2+(a-3)^2=25$.')
            line, pts = 'a=-7x', '$(0;0)$ и $(-1;7)$'
        t = (f'Рассмотрим плоскость $(x;a)$. Раскрываем модуль:\n\n{eqs}\n\n'
             f'Обе окружности пересекают прямую ${line}$ в одних и тех же точках {pts}. Множество решений — две большие дуги этих окружностей, '
             'лежащие по разные стороны от прямой и соединённые в этих точках. Число корней при данном $a$ — число точек пересечения '
             'горизонтальной прямой с этим множеством.\n\n'
             'Первая окружность занимает по $a$ отрезок $[-2;8]$, вторая — $[-1;9]$. Подсчёт: при $a<-2$ и $a>9$ корней нет; $a=-2$ — один; '
             '$-2<a<-1$ — два; $a=-1$ — три; $-1<a<0$ — четыре; $a=0$ — три (общая точка дуг); $0<a<7$ — два; $a=7$ — три; $7<a<8$ — четыре; '
             '$a=8$ — три; $8<a<9$ — два; $a=9$ — один.')
        return t


class AbsComposite(Param):
    """Квадратное уравнение относительно кусочно-линейной функции g(x)"""
    lo, hi, step = -8, 8, Fraction(1, 9)
    DATA = {
        '1cce7c': dict(g=lambda a: 4 * x + sp.Abs(x - a) - sp.Abs(3 * x + 1), q=lambda a, t: t ** 2 - (a + 1) * t + 1, need=2,
                       tex='(4x+|x-a|-|3x+1|)^2-(a+1)(4x+|x-a|-|3x+1|)+1=0', ask='ровно два различных корня',
                       ans=lambda: U(I.open(-oo, -3), I.open(1, r(3, 2)), I.open(r(3, 2), oo)),
                       text=('Пусть $g(x)=4x+|x-a|-|3x+1|$. На каждом промежутке знакопостоянства модулей $g$ линейна с угловым коэффициентом '
                             '$4\\pm1\\pm3$: это $8$, $6$, $2$ или $0$. Коэффициент $0$ получается, когда $x<a$ и $x>-\\frac13$: при $a>-\\frac13$ функция '
                             'постоянна на $\\left[-\\frac13;a\\right]$ и равна $a-1$, а вне этого отрезка строго возрастает от $-\\infty$ до $+\\infty$. '
                             'Значит, каждое значение $t\\ne a-1$ принимается ровно в одной точке, а $t=a-1$ (при $a>-\\frac13$) — на целом отрезке.\n\n'
                             'Уравнение $t^2-(a+1)t+1=0$: два различных корня при $(a+1)^2>4$, то есть $a<-3$ или $a>1$; они дают два корня $x$, если ни '
                             'один из них не равен $a-1$: $(a-1)^2-(a+1)(a-1)+1=3-2a=0$ при $a=\\frac32$ — исключаем (бесконечно много корней).')),
        'AcF79c': dict(g=lambda a: 3 * x + sp.Abs(x - a) + sp.Abs(2 * x + a + 1), q=lambda a, t: t ** 2 - a * t + a ** 2 - 16, need=1,
                       tex='(3x+|x-a|+|2x+a+1|)^2-a(3x+|x-a|+|2x+a+1|)+a^2-16=0', ask='ровно один корень',
                       ans=lambda: U(I.open((-1 - S(61)) / 2, (-1 + S(61)) / 2), F(8 * S(3) / 3)),
                       text=('Пусть $g(x)=3x+|x-a|+|2x+a+1|$. Угловые коэффициенты на промежутках: $3\\pm1\\pm2$, то есть $6$, $4$, $2$ или $0$; '
                             'коэффициент $0$ — при $x<a$ и $2x+a+1<0$, то есть левее обеих точек излома. Там $g(x)=-1$, а дальше $g$ строго '
                             'возрастает до $+\\infty$. Значит, $t>-1$ даёт ровно один корень, $t=-1$ — бесконечно много, $t<-1$ — ни одного.\n\n'
                             'Уравнение $f(t)=t^2-at+a^2-16=0$ должно иметь ровно один корень больше $-1$ и не иметь корня $-1$.\n\n'
                             '- $f(-1)<0$: корни по разные стороны от $-1$ — подходит. $a^2+a-15<0$: $\\frac{-1-\\sqrt{61}}{2}<a<\\frac{-1+\\sqrt{61}}{2}$.\n'
                             '- Двойной корень больше $-1$: $D=64-3a^2=0$, $a=\\pm\\frac{8}{\\sqrt3}$, корень $t=\\frac a2$; при $a=\\frac{8}{\\sqrt3}$ он больше $-1$.\n'
                             '- $f(-1)=0$ — бесконечно много корней; $f(-1)>0$ с двумя корнями больше $-1$ — два корня, меньше $-1$ — ни одного.')),
        'c06958': dict(g=lambda a: sp.Abs(x - a - 1) + sp.Abs(x - a + 1), q=lambda a, t: t ** 2 + a * t + a ** 2 - 16, need=2,
                       tex='(|x-a-1|+|x-a+1|)^2+a(|x-a-1|+|x-a+1|)+a^2-16=0', ask='ровно два различных корня',
                       ans=lambda: U(F(-8 * S(3) / 3), I.open(-1 - S(13), -1 + S(13))),
                       text=('$t=|x-a-1|+|x-a+1|$ — сумма расстояний от $x$ до точек $a-1$ и $a+1$: $t=2$ на всём отрезке $[a-1;a+1]$, а каждое '
                             '$t>2$ достигается ровно в двух точках.\n\n'
                             'Уравнение $f(t)=t^2+at+a^2-16=0$ должно иметь ровно один корень больше $2$ и не иметь корня $2$.\n\n'
                             '- $f(2)<0$: $a^2+2a-12<0$, $-1-\\sqrt{13}<a<-1+\\sqrt{13}$ — один корень больше 2, другой меньше.\n'
                             '- Двойной корень больше 2: $D=64-3a^2=0$, $t=-\\frac a2>2$ при $a=-\\frac{8}{\\sqrt3}$ (тогда $f(2)>0$).\n'
                             '- $f(2)=0$ — бесконечно много корней; иначе корней нет или их четыре.')),
        'Bc0636': dict(g=lambda a: sp.Abs(x - a ** 2) + sp.Abs(x + 1), q=lambda a, t: t ** 2 - 7 * t + 4 * a ** 2 + 4, need=2,
                       tex='(|x-a^2|+|x+1|)^2-7(|x-a^2|+|x+1|)+4a^2+4=0', ask='ровно два различных корня',
                       ans=lambda: U(I.open(-S(2), S(2)), F(-S(33) / 4, S(33) / 4)),
                       text=('$t=|x-a^2|+|x+1|$ — сумма расстояний от $x$ до точек $-1$ и $a^2$. Пусть $m=a^2+1$: $t=m$ на отрезке $[-1;a^2]$, а каждое '
                             '$t>m$ достигается ровно в двух точках.\n\n'
                             'Уравнение $t^2-7t+4m=0$ ($4a^2+4=4m$) должно иметь ровно один корень больше $m$ и не иметь корня $m$. $f(m)=m^2-3m=m(m-3)$.\n\n'
                             '- $f(m)<0$: $m<3$, $a^2<2$ — подходит.\n'
                             '- $f(m)=0$: $m=3$ — бесконечно много корней.\n'
                             '- $f(m)>0$ ($m>3$): подходит только двойной корень больше $m$: $49-16m=0$, $m=\\frac{49}{16}$, корень $\\frac72>\\frac{49}{16}$. '
                             'Тогда $a^2=\\frac{33}{16}$, $a=\\pm\\frac{\\sqrt{33}}{4}$.')),
        'e9FA32': dict(g=lambda a: 4 * x - 3 * sp.Abs(x + a ** 2) + sp.Abs(x - 1) + 3 * a ** 2, q=lambda a, t: t ** 2 - (a + 1) * t + 4, need=2,
                       tex='(4x-3|x+a^2|+|x-1|+3a^2)^2-(a+1)(4x-3|x+a^2|+|x-1|+3a^2)+4=0', ask='ровно два различных корня',
                       ans=lambda: U(I.open(-oo, -5), I.open(3, 4), I.open(4, oo)),
                       text=('Пусть $g(x)=4x-3|x+a^2|+|x-1|+3a^2$. Угловые коэффициенты: при $x<-a^2$ — $4+3-1=6$, при $-a^2<x<1$ — $4-3-1=0$, при $x>1$ — '
                             '$4-3+1=2$. На $[-a^2;1]$ функция постоянна и равна $g(1)=1$, вне отрезка строго возрастает. Значит, $t\\ne1$ даёт ровно один '
                             'корень, $t=1$ — бесконечно много.\n\n'
                             'Уравнение $t^2-(a+1)t+4=0$ должно иметь два различных корня, отличных от 1: $(a+1)^2>16$ ($a<-5$ или $a>3$) и '
                             '$1-(a+1)+4\\ne0$ ($a\\ne4$).')),
    }
    fipi = {k: dict(kind=k) for k in DATA}

    def aset(self, p):
        return self.DATA[p['kind']]['ans']()

    def extra(self, p):
        return {'1cce7c': (1, -3), 'AcF79c': (), 'c06958': (), 'Bc0636': (), 'e9FA32': (-5, 3, 4)}[p['kind']]

    def ok(self, p, a):
        d = self.DATA[p['kind']]
        gexpr = d['g'](a)
        P = Points()
        breaks = sorted({sp.nsimplify(sp.solve(arg.args[0], x)[0]) for arg in gexpr.atoms(sp.Abs)}, key=num)
        edges = [-oo] + breaks + [oo]
        for t in poly_roots(d['q'](a, T), T):
            if t == INF:
                return False
            for lo_, hi_ in zip(edges, edges[1:]):
                mid = (lo_ + hi_) / 2 if lo_.is_finite and hi_.is_finite else (hi_ - 1 if lo_ == -oo else lo_ + 1)
                if lo_ == -oo and hi_ == oo:
                    mid = 0
                lin = sp.expand(gexpr.subs({ab: (ab.args[0] if num(ab.args[0].subs(x, mid)) >= 0 else -ab.args[0]) for ab in gexpr.atoms(sp.Abs)}))
                k0 = lin.coeff(x, 1)
                b0 = lin.subs(x, 0)
                if k0 == 0:
                    if abs(num(b0 - t)) < 1e-30:
                        return d['need'] == 10 ** 9
                    continue
                xr = (t - b0) / k0
                if (lo_ == -oo or ge(xr - lo_)) and (hi_ == oo or ge(hi_ - xr)):
                    P.add(xr)
        return len(P) == d['need']

    def cond(self, p):
        d = self.DATA[p['kind']]
        return f'Найдите все значения $a$, при каждом из которых уравнение $${d["tex"]}$$ имеет {d["ask"]}.'

    def solution(self, p):
        return self.DATA[p['kind']]['text']


class TwoParallelLinesCircle(Param):
    """(x + ay − 5)(x + ay − 5a) = 0, x² + y² = 16: ровно четыре решения"""
    fipi = {'D5CA79': {}}
    lo, hi, step = -3, 3, Fraction(1, 19)

    def aset(self, p):
        return U(I.open(r(-4, 3), r(-3, 4)), I.open(r(3, 4), 1), I.open(1, r(4, 3)))

    def ok(self, p, a):
        P = Points()
        for c in (5, 5 * a):
            if a == 0:
                if abs(c) < 4:
                    for y in (sp.sqrt(16 - c ** 2), -sp.sqrt(16 - c ** 2)):
                        P.add(c, y)
                elif abs(c) == 4:
                    P.add(c, 0)
                continue
            for y in poly_roots((c - a * Y) ** 2 + Y ** 2 - 16, Y):
                P.add(c - a * y, y)
        return len(P) == 4

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}(x+ay-5)(x+ay-5a)=0,\\\\ x^2+y^2=16\\end{cases}$$ '
                'имеет ровно четыре различных решения.')

    def solution(self, p):
        return (
            'Первое уравнение задаёт две параллельные прямые $x+ay=5$ и $x+ay=5a$ (они совпадают при $a=1$), второе — окружность радиуса 4 с '
            'центром в начале координат. Четыре решения — когда прямые различны и каждая пересекает окружность в двух точках, то есть удалена '
            'от центра меньше чем на 4:\n\n'
            '$\\frac{5}{\\sqrt{1+a^2}}<4$: $a^2>\\frac{9}{16}$; $\\frac{5|a|}{\\sqrt{1+a^2}}<4$: $a^2<\\frac{16}{9}$.\n\n'
            'Итак, $\\frac34<|a|<\\frac43$, $a\\ne1$.')


class FractionTwoRoots(Param):
    """(k²x² − a²)/((x + m)² − a²) = 0: ровно два различных корня"""
    fipi = {'831474': dict(k=3, m=4), '162563': dict(k=2, m=3)}
    lo, hi, step = -12, 12, Fraction(1, 7)

    def bad(self, p):
        k, m = p['k'], p['m']
        return sorted({sp.Rational(m * k, k - 1), sp.Rational(-m * k, k + 1), sp.Rational(m * k, k + 1), sp.Rational(-m * k, k - 1)})

    def aset(self, p):
        pts = sorted(set(self.bad(p)) | {sp.Integer(0)})
        return sp.Complement(sp.S.Reals, F(*pts))

    def ok(self, p, a):
        k, m = p['k'], p['m']
        P = Points()
        for r_ in poly_roots(k ** 2 * x ** 2 - a ** 2):
            if abs(num((r_ + m) ** 2 - a ** 2)) > 1e-30:
                P.add(r_)
        return len(P) == 2

    def answer(self, p):
        pts = sorted(set(self.bad(p)) | {sp.Integer(0)})
        return Answer('$a\\ne ' + ',\\ '.join(f'{tx(v)}' for v in pts).replace(', ', ';\\ ') + '$', 0)

    def cond(self, p):
        k, m = p['k'], p['m']
        return (f'Найдите все значения $a$, при каждом из которых уравнение $$\\frac{{{k * k}x^2-a^2}}{{x^2+{2 * m}x+{m * m}-a^2}}=0$$ '
                'имеет ровно два различных корня.')

    def solution(self, p):
        k, m = p['k'], p['m']
        b = self.bad(p)
        return (
            f'Числитель равен нулю при $x=\\pm\\frac a{k}$, знаменатель $(x+{m})^2-a^2$ — при $x=-{m}\\pm a$. При $a=0$ числитель имеет один корень '
            f'$x=0$ — не подходит. При $a\\ne0$ корни $\\frac a{k}$ и $-\\frac a{k}$ различны; уравнение имеет два корня, если ни один из них не '
            'обращает знаменатель в нуль.\n\n'
            f'$\\frac a{k}=-{m}+a$, $\\frac a{k}=-{m}-a$, $-\\frac a{k}=-{m}+a$, $-\\frac a{k}=-{m}-a$ дают $a=' +
            ',\\ '.join(tx(v) for v in b) + '$ — при этих $a$ корень один.')

    def sample(self, rng):
        return dict(k=rng.randint(2, 5), m=rng.randint(1, 9))


class ParabolaSqrtLine(Param):
    """(x² − 5x − y + 3)·√(x − y + 3) = 0 и прямая: ровно два решения"""
    fipi = {'04FEB6': dict(kind='y3x'), '37FD10': dict(kind='through')}
    lo, hi, step = -16, 6, Fraction(1, 9)

    def aset(self, p):
        if p['kind'] == 'y3x':
            return U(F(-13), I.Ropen(-9, 3))
        return U(F(-1, 1), I.Ropen(r(9, 7), 3))

    def ok(self, p, a):
        k, m = (3, a) if p['kind'] == 'y3x' else (a, a)
        P = Points()
        if k != 1:
            xr = (3 - m) / (k - 1)
            P.add(xr, k * xr + m)
        for r_ in poly_roots(x ** 2 - 5 * x + 3 - k * x - m):
            y = k * r_ + m
            if ge(r_ - y + 3):
                P.add(r_, y)
        return len(P) == 2

    def cond(self, p):
        line = 'y=3x+a' if p['kind'] == 'y3x' else 'y=ax+a'
        return ('Найдите все значения $a$, при каждом из которых система уравнений '
                f'$$\\begin{{cases}}(x^2-5x-y+3)\\cdot\\sqrt{{x-y+3}}=0,\\\\ {line}\\end{{cases}}$$ имеет ровно два различных решения.')

    def solution(self, p):
        base = ('Первое уравнение при условии $y\\le x+3$ задаёт объединение прямой $\\ell$: $y=x+3$ и части параболы $y=x^2-5x+3$, лежащей не выше '
                '$\\ell$, то есть при $0\\le x\\le6$ (парабола пересекает $\\ell$ в точках $A(0;3)$ и $B(6;9)$).\n\n')
        if p['kind'] == 'y3x':
            return base + (
                'Прямая $y=3x+a$ пересекает $\\ell$ ровно в одной точке $x=\\frac{3-a}{2}$. С параболой: $x^2-8x+3-a=0$, $x=4\\pm\\sqrt{13+a}$. '
                'Условие $x\\in[0;6]$: корень $4+\\sqrt{13+a}$ подходит при $a\\le-9$, корень $4-\\sqrt{13+a}$ — при $a\\le3$.\n\n'
                '- $a<-13$: только точка на $\\ell$ — одно решение.\n- $a=-13$: касание параболы ($x=4$) и точка на $\\ell$ — два.\n'
                '- $-13<a<-9$: две точки параболы и точка на $\\ell$ — три; при $a=-9$ точка $x=6$ параболы совпадает с точкой на $\\ell$ ($B$) — два.\n'
                '- $-9<a<3$: одна точка параболы и точка на $\\ell$ — два; при $a=3$ они совпадают в $A$ — одно.\n- $a>3$: одно.')
        return base + (
            'Прямые $y=ax+a$ проходят через точку $P(-1;0)$. Ключевые положения: через $A$ ($a=3$), через $B$ ($a=\\frac97$), параллельно $\\ell$ '
            '($a=1$), касание параболы: $x^2-(5+a)x+3-a=0$, $D=(a+1)(a+13)=0$; при $a=-1$ точка касания $x=2\\in[0;6]$, при $a=-13$ — вне отрезка.\n\n'
            '- $a<-1$: с параболой на $[0;6]$ общих точек нет, с $\\ell$ — одна: одно решение.\n'
            '- $a=-1$: касание и точка на $\\ell$ — два.\n'
            '- $-1<a<\\frac97$, $a\\ne1$: две точки параболы и точка на $\\ell$ — три; при $a=1$ прямая параллельна $\\ell$ — два.\n'
            '- $a=\\frac97$: прямая проходит через $B$ — точка на $\\ell$ совпадает с точкой параболы — два.\n'
            '- $\\frac97<a<3$: одна точка параболы и точка на $\\ell$ — два.\n- $a\\ge3$: одно.')


class ParabolaTwoLines(Param):
    """y = (a + 2)x² + 2ax + a − 2, y² = x²: ровно четыре решения"""
    fipi = {'07CC1C': {}}
    lo, hi, step = -6, 6, Fraction(1, 11)

    def aset(self, p):
        return U(I.open(r(-17, 4), -2), I.open(-2, 2), I.open(2, r(17, 4)))

    def ok(self, p, a):
        par = (a + 2) * x ** 2 + 2 * a * x + a - 2
        return count_points([(par - x, lambda t: t, lambda t, y: True), (par + x, lambda t: -t, lambda t, y: True)]) == 4

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}y=(a+2)x^2+2ax+a-2,\\\\ y^2=x^2\\end{cases}$$ '
                'имеет ровно четыре различных решения.')

    def solution(self, p):
        return (
            '$y^2=x^2$: $y=x$ или $y=-x$. Подставляя: $(a+2)x^2+(2a-1)x+a-2=0$ и $(a+2)x^2+(2a+1)x+a-2=0$. Общее решение двух уравнений '
            'возможно только при $x=0$ (тогда $y=0$), то есть при $a=2$.\n\n'
            'При $a=-2$ уравнения линейные — решений два. При $a\\ne-2$ нужны два корня у каждого: $D_1=17-4a>0$, $D_2=17+4a>0$, то есть '
            '$-\\frac{17}{4}<a<\\frac{17}{4}$; и $a\\ne2$ (иначе совпадение в точке $(0;0)$ — три решения).')


class CircleSqrtPencil(Param):
    """(x² + y² + 4x)·√(2x + y + 6) = 0 и прямая: ровно два решения"""
    fipi = {'4A8E2F': dict(kind='pencil'), 'F3A6D5': dict(kind='parallel')}
    lo, hi, step = -3, 6, Fraction(1, 13)

    def aset(self, p):
        if p['kind'] == 'pencil':
            return U(F(-S(3) / 3, S(3) / 3), I(r(-3, 14), r(1, 2)))
        return U(F(2 - 2 * S(2), 2 + 2 * S(2)), I(0, r(24, 5)))

    def ok(self, p, a):
        k, m = (a, -2 * a) if p['kind'] == 'pencil' else (1, a)
        P = Points()
        if k != -2:
            xr = (-6 - m) / (k + 2)
            P.add(xr, k * xr + m)
        for r_ in poly_roots(x ** 2 + (k * x + m) ** 2 + 4 * x):
            y = k * r_ + m
            if ge(2 * r_ + y + 6):
                P.add(r_, y)
        return len(P) == 2

    def cond(self, p):
        line = 'y=ax-2a' if p['kind'] == 'pencil' else 'y=x+a'
        return ('Найдите все значения $a$, при каждом из которых система уравнений '
                f'$$\\begin{{cases}}(x^2+y^2+4x)\\cdot\\sqrt{{2x+y+6}}=0,\\\\ {line}\\end{{cases}}$$ имеет ровно два различных решения.')

    def solution(self, p):
        base = ('Первое уравнение при $2x+y+6\\ge0$: прямая $\\ell$: $y=-2x-6$ или окружность $(x+2)^2+y^2=4$ (центр $(-2;0)$, радиус 2) '
                'в полуплоскости над $\\ell$. Прямая $\\ell$ пересекает окружность в точках $P(-2;-2)$ и $Q\\left(-\\frac{18}{5};\\frac65\\right)$; '
                'нужна большая дуга $PQ$ (центр окружности лежит в полуплоскости).\n\n')
        if p['kind'] == 'pencil':
            return base + (
                'Прямые $y=a(x-2)$ проходят через $M(2;0)$ и пересекают $\\ell$ в одной точке (при $a\\ne-2$). Ключевые положения: касательные из '
                '$M$ к окружности ($a=\\pm\\frac{1}{\\sqrt3}$, точки касания $(-1;\\mp\\sqrt3)$ лежат на дуге), прямые через $P$ ($a=\\frac12$) и через '
                '$Q$ ($a=-\\frac{3}{14}$).\n\n'
                '- $|a|>\\frac{1}{\\sqrt3}$: с окружностью общих точек нет — одно решение (при $a=-2$ — ни одного).\n'
                '- $a=\\pm\\frac{1}{\\sqrt3}$: касание и точка на $\\ell$ — два.\n'
                '- $-\\frac{1}{\\sqrt3}<a<-\\frac{3}{14}$ и $\\frac12<a<\\frac{1}{\\sqrt3}$: две точки дуги и точка на $\\ell$ — три.\n'
                '- $-\\frac{3}{14}\\le a\\le\\frac12$: одна из точек пересечения с окружностью не на дуге (или совпадает с $P$, $Q$) — два.')
        return base + (
            'Прямые $y=x+a$ параллельны и всегда пересекают $\\ell$ в одной точке. Касание с окружностью: $\\frac{|a-2|}{\\sqrt2}=2$, '
            '$a=2\\pm2\\sqrt2$ (точки касания на дуге); через $P$: $a=0$; через $Q$: $a=\\frac{24}{5}$.\n\n'
            '- $a<2-2\\sqrt2$ или $a>2+2\\sqrt2$: одно решение.\n- $a=2\\pm2\\sqrt2$: два.\n'
            '- $2-2\\sqrt2<a<0$ и $\\frac{24}{5}<a<2+2\\sqrt2$: три.\n- $0\\le a\\le\\frac{24}{5}$: два.')


class AbsQuadCircles(Param):
    """|x² + a² − 6x ± 4a| = 2x ∓ 2a: дуги двух окружностей в плоскости (x; a)"""
    fipi = {'093D22': dict(s=1, need='two'), '421A63': dict(s=-1, need='four')}
    lo, hi, step = -9, 9, Fraction(1, 9)

    def aset(self, p):
        if p['s'] == 1:
            return U(I.open(-8, -1 - S(5)), I.open(0, 1), I.open(S(5) - 1, 2))
        return U(I.open(1 - S(5), -1), I.open(0, 1 + S(5)))

    def ok(self, p, a):
        s = p['s']
        P = Points()
        g = 2 * x - 2 * s * a
        for e in (x ** 2 + a ** 2 - 6 * x + 4 * s * a - g, x ** 2 + a ** 2 - 6 * x + 4 * s * a + g):
            for r_ in poly_roots(e):
                if r_ == INF:
                    return False
                if ge(r_ - s * a):
                    P.add(r_)
        return len(P) == (2 if p['need'] == 'two' else 4)

    def cond(self, p):
        if p['s'] == 1:
            return 'Найдите все значения $a$, при каждом из которых уравнение $$|x^2+a^2-6x+4a|=2x-2a$$ имеет ровно два различных корня.'
        return 'Найдите все значения $a$, при каждом из которых уравнение $$|x^2+a^2-6x-4a|=2x+2a$$ имеет четыре различных корня.'

    def solution(self, p):
        if p['s'] == 1:
            return (
                'Уравнение равносильно условию $x\\ge a$ вместе с $x^2+a^2-6x+4a=\\pm(2x-2a)$. В плоскости $(x;a)$ это окружности '
                '$\\omega_1$: $(x-4)^2+(a+3)^2=25$ и $\\omega_2$: $(x-2)^2+(a+1)^2=5$ в полуплоскости $x\\ge a$. Обе окружности пересекают прямую '
                '$x=a$ в точках $(0;0)$ и $(1;1)$; $\\omega_1$ занимает по $a$ отрезок $[-8;2]$, $\\omega_2$ — $[-1-\\sqrt5;\\sqrt5-1]$.\n\n'
                'Считаем точки пересечения горизонтальной прямой с этими дугами: $a<-8$ — нет; $a=-8$ — одна; $-8<a<-1-\\sqrt5$ — две; '
                '$a=-1-\\sqrt5$ — три; $-1-\\sqrt5<a<0$ — четыре; $a=0$ — три; $0<a<1$ — две; $a=1$ — три; $1<a<\\sqrt5-1$ — четыре; '
                '$a=\\sqrt5-1$ — три; $\\sqrt5-1<a<2$ — две; $a=2$ — одна; $a>2$ — нет.')
        return (
            'Уравнение равносильно условию $x\\ge-a$ вместе с $x^2+a^2-6x-4a=\\pm(2x+2a)$. В плоскости $(x;a)$ это окружности '
            '$\\omega_1$: $(x-4)^2+(a-3)^2=25$ и $\\omega_2$: $(x-2)^2+(a-1)^2=5$ в полуплоскости $x\\ge-a$. Обе пересекают прямую $x=-a$ в точках '
            '$(0;0)$ и $(1;-1)$; $\\omega_1$ занимает по $a$ отрезок $[-2;8]$, $\\omega_2$ — $[1-\\sqrt5;1+\\sqrt5]$.\n\n'
            'Подсчёт точек пересечения горизонтальной прямой с дугами: $a<-2$ — нет; $a=-2$ — одна; $-2<a<1-\\sqrt5$ — две; $a=1-\\sqrt5$ — три; '
            '$1-\\sqrt5<a<-1$ — четыре; $a=-1$ — три; $-1<a<0$ — две; $a=0$ — три; $0<a<1+\\sqrt5$ — четыре; $a=1+\\sqrt5$ — три; '
            '$1+\\sqrt5<a<8$ — две; $a=8$ — одна.')


class EvenQuartic(Param):
    """x⁴ + (a − c)² = |x − a + c| + |x + a − c|: единственное решение или нет решений"""
    fipi = {'0106DC': dict(c=3)}
    lo, hi, step = -6, 12, Fraction(1, 7)

    def aset(self, p):
        c = p['c']
        return U(I(-oo, c - 2), I(c + 2, oo))

    def ok(self, p, a):
        b = a - p['c']
        P = Points()
        brk = sorted({b, -b}, key=num)
        edges = [-oo] + brk + [oo]
        for lo_, hi_ in zip(edges, edges[1:]):
            mid = 0 if lo_ == -oo and hi_ == oo else ((hi_ - 1) if lo_ == -oo else ((lo_ + 1) if hi_ == oo else (lo_ + hi_) / 2))
            s1 = 1 if num(mid - b) >= 0 else -1
            s2 = 1 if num(mid + b) >= 0 else -1
            for r_ in poly_roots(x ** 4 + b ** 2 - s1 * (x - b) - s2 * (x + b)):
                if (lo_ == -oo or ge(r_ - lo_)) and (hi_ == oo or ge(hi_ - r_)):
                    P.add(r_)
        return len(P) <= 1

    def cond(self, p):
        c = p['c']
        return (f'Найдите все значения $a$, при каждом из которых уравнение $$x^4+(a-{c})^2=|x-a+{c}|+|x+a-{c}|$$ '
                'либо имеет единственное решение, либо не имеет решений.')

    def solution(self, p):
        c = p['c']
        return (
            f'Пусть $b=a-{c}$: $x^4+b^2=|x-b|+|x+b|=2\\max(|x|;|b|)$. Уравнение не меняется при замене $x\\to-x$, поэтому корни идут парами $\\pm x$, '
            'и единственным может быть только корень $x=0$.\n\n'
            '$x=0$ — корень, если $b^2=2|b|$: $b=0$ или $|b|=2$. При $b=0$: $x^4=2|x|$ — корни $0$ и $\\pm\\sqrt[3]2$, их три. При $|b|=2$: при $|x|\\le2$ '
            'уравнение $x^4+4=4$ даёт только $x=0$, а при $|x|>2$ $x^4+4>2|x|$ — корень единственный.\n\n'
            'Решений нет, если $x^4+b^2>2\\max(|x|;|b|)$ при всех $x$: при $|x|\\le|b|$ нужно $b^2>2|b|$, то есть $|b|>2$; тогда и при $|x|>|b|>2$ '
            '$x^4>2|x|$. Если же $|b|<2$, то при $x=0$ левая часть меньше правой, а при больших $|x|$ — больше, и корни есть.\n\n'
            f'Итак, $|a-{c}|\\ge2$.')

    def sample(self, rng):
        return dict(c=rng.randint(-6, 8))


class AbsXQuadratic(Param):
    """a² ± ax − 2x² − 6a ∓ 3x + 9|x| = 0: четыре различных корня / меньше четырёх"""
    fipi = {'577658': dict(s=1, ask='less'), '073F98': dict(s=-1, ask='four')}
    lo, hi, step = -4, 10, Fraction(1, 9)

    def aset(self, p):
        four = U(I.open(0, 2), I.open(2, 4), I.open(4, 6))
        return four if p['ask'] == 'four' else sp.Complement(sp.S.Reals, four)

    def ok(self, p, a):
        s = p['s']
        P = Points()
        for sign in (1, -1):
            for r_ in poly_roots(a ** 2 + s * a * x - 2 * x ** 2 - 6 * a - s * 3 * x + 9 * sign * x):
                if r_ == INF:
                    return False
                if (sign == 1 and ge(r_)) or (sign == -1 and num(r_) < -1e-30):
                    P.add(r_)
        n = len(P)
        return n == 4 if p['ask'] == 'four' else n < 4

    def answer(self, p):
        if p['ask'] == 'four':
            return Answer(show(self.aset(p)), 0)
        return Answer('$a\\in(-\\infty;0]\\cup\\{2;\\ 4\\}\\cup[6;+\\infty)$', 0)

    def cond(self, p):
        if p['s'] == 1:
            return 'Найдите все значения $a$, при каждом из которых уравнение $$a^2+ax-2x^2-6a-3x+9|x|=0$$ имеет меньше четырёх различных корней.'
        return 'Найдите все значения $a$, при каждом из которых уравнение $$a^2-ax-2x^2-6a+3x+9|x|=0$$ имеет четыре различных корня.'

    def solution(self, p):
        if p['s'] == 1:
            pos, neg = ('$2x^2-(a+6)x-a^2+6a=0$, дискриминант $9(a-2)^2$, корни $x=a$ и $x=\\frac{6-a}{2}$',
                        '$2x^2-(a-12)x-a^2+6a=0$, дискриминант $9(a-4)^2$, корни $x=a-6$ и $x=-\\frac a2$')
            cond = ('корни $a\\ge0$ и $\\frac{6-a}{2}\\ge0$ (из первого), $a-6<0$ и $-\\frac a2<0$ (из второго)')
        else:
            pos, neg = ('$2x^2+(a-12)x-a^2+6a=0$, корни $x=6-a$ и $x=\\frac a2$',
                        '$2x^2+(a+6)x-a^2+6a=0$, корни $x=-a$ и $x=\\frac{a-6}{2}$')
            cond = 'корни $6-a\\ge0$, $\\frac a2\\ge0$ (из первого), $-a<0$, $\\frac{a-6}{2}<0$ (из второго)'
        res = ('Четыре корня при $a\\in(0;2)\\cup(2;4)\\cup(4;6)$, меньше четырёх — при остальных $a$.' if p['s'] == 1 else
               'Четыре корня: $a\\in(0;2)\\cup(2;4)\\cup(4;6)$.')
        return (
            f'При $x\\ge0$: {pos}. При $x<0$: {neg}.\n\n'
            f'Четыре различных корня будут, если все четыре числа подходят по знаку — {cond}, то есть $0<a<6$ — и попарно различны: '
            'совпадения возможны только при $a=2$ (два корня первого уравнения совпадают) и $a=4$ (совпадают корни второго). ' + res)


class LineTwoParabolasAbs(Param):
    """4x − y + a = 0, 2|y| − x² + 4x = 0: ровно два решения"""
    fipi = {'F605A0': {}}
    lo, hi, step = -22, 5, Fraction(1, 6)

    def aset(self, p):
        return U(I.open(-oo, -18), I.open(-16, 0), I.open(2, oo))

    def ok(self, p, a):
        pieces = []
        for s in (1, -1):
            pieces.append((x ** 2 - (4 + 8 * s) * x - 2 * s * a, lambda t: 4 * t + a, (lambda s: lambda t, y: ge(s * y))(s)))
        return count_points(pieces) == 2

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}4x-y+a=0,\\\\ 2|y|-x^2+4x=0\\end{cases}$$ '
                'имеет ровно два различных решения.')

    def solution(self, p):
        return (
            'Второе уравнение: $|y|=\\frac{x^2-4x}{2}$ — две параболы $y=\\pm\\frac{x^2-4x}{2}$ при $x\\le0$ или $x\\ge4$; они смыкаются в точках '
            '$(0;0)$ и $(4;0)$. Первое — прямая $y=4x+a$ с угловым коэффициентом 4.\n\n'
            'Подставим: при $y\\ge0$: $x^2-12x-2a=0$; при $y\\le0$: $x^2+4x+2a=0$. Ключевые положения: касание верхней ветви '
            '($D=144+8a=0$, $a=-18$, точка $x=6$), касание нижней ветви ($D=16-8a=0$, $a=2$, точка $x=-2$), прохождение через $(0;0)$ ($a=0$) и '
            'через $(4;0)$ ($a=-16$).\n\n'
            'Подсчёт: $a<-18$ — две точки; $a=-18$ — три; $-18<a<-16$ — четыре; $a=-16$ — три; $-16<a<0$ — две; $a=0$ — три; $0<a<2$ — четыре; '
            '$a=2$ — три; $a>2$ — две.')


class HyperbolaSqrtLine(Param):
    """(xy − 2x + 12)·√(y − 2x + 12) = 0 и прямая: ровно два решения"""
    fipi = {'752FA4': dict(kind='pencil'), '6854C0': dict(kind='parallel')}
    lo, hi, step = -22, 18, Fraction(1, 5)

    def aset(self, p):
        if p['kind'] == 'pencil':
            return U(I.open(-oo, 0), I.Lopen(0, r(5, 3)), F(2, 3))
        return U(I.Lopen(-18, -13), F(-10, 14))

    def ok(self, p, a):
        k, m = (a, -10) if p['kind'] == 'pencil' else (3, a)
        P = Points()
        if k != 2:
            xr = (-12 - m) / (k - 2)
            P.add(xr, k * xr + m)
        for r_ in poly_roots(k * x ** 2 + (m - 2) * x + 12):
            if r_ == INF:
                return False
            y = k * r_ + m
            if ge(y - 2 * r_ + 12):
                P.add(r_, y)
        return len(P) == 2

    def cond(self, p):
        line = 'y=ax-10' if p['kind'] == 'pencil' else 'y=3x+a'
        return ('Найдите все значения $a$, при каждом из которых система уравнений '
                f'$$\\begin{{cases}}(xy-2x+12)\\cdot\\sqrt{{y-2x+12}}=0,\\\\ {line}\\end{{cases}}$$ имеет ровно два различных решения.')

    def solution(self, p):
        base = ('ОДЗ: $y\\ge2x-12$. Первое уравнение задаёт прямую $\\ell$: $y=2x-12$ и часть гиперболы $y=2-\\frac{12}{x}$ в ОДЗ. Гипербола '
                'пересекает $\\ell$ в точках $A(1;-10)$ и $B(6;0)$; в ОДЗ лежат вся левая ветвь ($x<0$) и дуга правой ветви при $1\\le x\\le6$.\n\n')
        if p['kind'] == 'pencil':
            return base + (
                'Прямые $y=ax-10$ проходят через $(0;-10)$. С $\\ell$ общая точка $x=\\frac{2}{2-a}$ (при $a\\ne2$). С гиперболой: $ax^2-12x+12=0$.\n\n'
                '- $a<0$: корни разных знаков; отрицательный лежит на левой ветви, положительный — в $(0;1)$, вне ОДЗ. Плюс точка на $\\ell$ — два решения.\n'
                '- $a=0$: $x=1$ — точка $A$, она же точка на $\\ell$ — одно решение.\n'
                '- $0<a<\\frac53$: на дуге $[1;6]$ один корень, плюс точка на $\\ell$ — два; при $a=\\frac53$ прямая проходит через $B$, корни $1{,}2$ и $6$, '
                'точка на $\\ell$ совпадает с $B$ — два.\n'
                '- $\\frac53<a<3$: оба корня на дуге и точка на $\\ell$ — три, но при $a=2$ прямая параллельна $\\ell$ — два.\n'
                '- $a=3$: касание ($x=2$) и точка на $\\ell$ — два.\n- $a>3$: одно.')
        return base + (
            'Прямая $y=3x+a$ пересекает $\\ell$ в одной точке $x=-12-a$. С гиперболой: $3x^2+(a-2)x+12=0$, $D=(a-2)^2-144\\ge0$ при $a\\le-10$ '
            'или $a\\ge14$.\n\n'
            '- $a\\ge14$: корни отрицательны (левая ветвь): при $a=14$ — касание, всего два решения; при $a>14$ — три.\n'
            '- $a\\le-10$: корни положительны; нужно $x\\in[1;6]$. Пусть $g(x)=3x^2+(a-2)x+12$: $g(1)=a+13$, $g(6)=6a+108$. При $a=-10$ — касание '
            '($x=2$), всего два решения. При $-13\\le a<-10$ оба корня на дуге — с точкой на $\\ell$ три, но при $a=-13$ точка на $\\ell$ совпадает '
            'с $A$ — два. При $-18<a<-13$ на дуге один корень — два решения. При $a=-18$ корень $x=6$ совпадает с точкой на $\\ell$ ($B$) — одно. '
            'При $a<-18$ — одно.\n- $-10<a<14$: только точка на $\\ell$ — одно.')


class SqrtEqualSegment(Param):
    """√(x² − a²) = √(4x² − (4a + 2)x + 2a) на [0; 1]: ровно один корень"""
    fipi = {'93CF53': {}}
    lo, hi, step = -3, 3, Fraction(1, 13)

    def aset(self, p):
        return U(I.Ropen(r(-1, 2), 0), F(1))

    def ok(self, p, a):
        P = Points()
        for r_ in poly_roots(x ** 2 - a ** 2 - (4 * x ** 2 - (4 * a + 2) * x + 2 * a)):
            if r_ == INF:
                return False
            if ge(r_) and ge(1 - r_) and ge(r_ ** 2 - a ** 2):
                P.add(r_)
        return len(P) == 1

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых уравнение $$\\sqrt{x^2-a^2}=\\sqrt{4x^2-(4a+2)x+2a}$$ на отрезке $[0;1]$ '
                'имеет ровно один корень.')

    def solution(self, p):
        return (
            'Уравнение равносильно системе $x^2-a^2\\ge0$, $x^2-a^2=4x^2-(4a+2)x+2a$. Второе: $3x^2-(4a+2)x+a^2+2a=0$, дискриминант '
            '$4(a-1)^2$, корни $x=a$ и $x=\\frac{a+2}{3}$.\n\n'
            '- $x=a$: условие $x^2\\ge a^2$ выполнено; на отрезке при $0\\le a\\le1$.\n'
            '- $x=\\frac{a+2}{3}$: на отрезке при $-2\\le a\\le1$; условие $\\frac{a+2}{3}\\ge|a|$ даёт $-\\frac12\\le a\\le1$.\n'
            '- Корни совпадают при $a=1$.\n\n'
            'Ровно один корень: $-\\frac12\\le a<0$ (только второй) и $a=1$ (совпали). При $0\\le a<1$ корней два.')


class QuarticDifference(Param):
    """x⁴ − y⁴ = 12a − 28, x² + y² = a: ровно четыре решения"""
    fipi = {'E156E1': {}}
    lo, hi, step = -3, 14, Fraction(1, 9)

    def aset(self, p):
        return U(I.open(2, 6 - 2 * S(2)), I.open(6 + 2 * S(2), oo))

    def ok(self, p, a):
        if a == 0:
            return False
        u = (a ** 2 + 12 * a - 28) / (2 * a)       # x²
        v = a - u                                  # y²
        if num(u) < -1e-30 or num(v) < -1e-30:
            return False
        nx = 1 if abs(num(u)) < 1e-30 else 2
        ny = 1 if abs(num(v)) < 1e-30 else 2
        return nx * ny == 4

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}x^4-y^4=12a-28,\\\\ x^2+y^2=a\\end{cases}$$ '
                'имеет ровно четыре различных решения.')

    def solution(self, p):
        return (
            '$x^4-y^4=(x^2-y^2)(x^2+y^2)=a(x^2-y^2)$. При $a=0$ из второго уравнения $x=y=0$, но тогда $0\\ne-28$. При $a\\ne0$: '
            '$x^2-y^2=12-\\frac{28}{a}$, $x^2+y^2=a$, откуда $x^2=\\frac{a^2+12a-28}{2a}$, $y^2=\\frac{a^2-12a+28}{2a}$.\n\n'
            'Решений четыре, если $x^2>0$ и $y^2>0$ (тогда $(\\pm x;\\pm y)$); если одно из чисел равно нулю — решений два.\n\n'
            '$a>0$ (иначе $x^2+y^2=a<0$): $a^2+12a-28>0$ при $a>2$; $a^2-12a+28>0$ при $a<6-2\\sqrt2$ или $a>6+2\\sqrt2$.')


class AbsSumSqrt(Param):
    """|x| + |y| = a, y = √(x + 4): ровно два решения (a > 0)"""
    fipi = {'7CC260': {}}
    lo, hi, step = Fraction(1, 9), 8, Fraction(1, 17)

    def aset(self, p):
        return U(I.open(2, 4), F(r(17, 4)))

    def ok(self, p, a):
        P = Points()
        for s in poly_roots(T ** 2 + T - 4 - a, T):       # x ≥ 0: s ≥ 2
            if ge(s - 2):
                P.add(s ** 2 - 4)
        for s in poly_roots(-T ** 2 + T + 4 - a, T):      # −4 ≤ x < 0: 0 ≤ s < 2
            if ge(s) and num(2 - s) > 1e-30:
                P.add(s ** 2 - 4)
        return len(P) == 2

    def cond(self, p):
        return ('Найдите все положительные значения $a$, при каждом из которых система уравнений $$\\begin{cases}|x|+|y|=a,\\\\ y=\\sqrt{x+4}\\end{cases}$$ '
                'имеет ровно два различных решения.')

    def solution(self, p):
        return (
            'Пусть $s=\\sqrt{x+4}\\ge0$, $x=s^2-4$, $y=s$; каждому $s$ соответствует одно решение. Уравнение $|s^2-4|+s=a$.\n\n'
            '- $x\\ge0$ ($s\\ge2$): $s^2+s-4=a$ — функция возрастает от $2$ (при $s=2$) — один корень при $a\\ge2$.\n'
            '- $-4\\le x<0$ ($0\\le s<2$): $-s^2+s+4=a$. Функция $h(s)=-s^2+s+4$ на $[0;2)$ возрастает до максимума $\\frac{17}{4}$ при $s=\\frac12$, '
            'а затем убывает до $2$ (не включительно): $h(0)=4$. Корней два при $4\\le a<\\frac{17}{4}$, один при $a=\\frac{17}{4}$ и при $2<a<4$, '
            'ни одного при $a\\le2$ и $a>\\frac{17}{4}$.\n\n'
            'Итого: $2<a<4$ — два решения; $a=4$ и $4<a<\\frac{17}{4}$ — три; $a=\\frac{17}{4}$ — два; при $a=2$ — одно ($s=2$), при $a>\\frac{17}{4}$ — одно.')


class AbsProductLine(Param):
    """(x + 1)|x + 1| = 2x − a: ровно два корня"""
    fipi = {'3D498A': {}}
    lo, hi, step = -6, 3, Fraction(1, 11)

    def aset(self, p):
        return F(-3, -1)

    def ok(self, p, a):
        P = Points()
        for r_ in poly_roots((x + 1) ** 2 - (2 * x - a)):
            if ge(r_ + 1):
                P.add(r_)
        for r_ in poly_roots(-(x + 1) ** 2 - (2 * x - a)):
            if num(r_ + 1) < -1e-30:
                P.add(r_)
        return len(P) == 2

    def cond(self, p):
        return 'Найдите все значения $a$, при каждом из которых уравнение $$(x+1)\\cdot|x+1|=2x-a$$ имеет ровно два различных корня.'

    def solution(self, p):
        return (
            'Пусть $u=x+1$: $u|u|-2u=-(a+2)$. Функция $h(u)=u|u|-2u$: при $u\\ge0$ $h=u^2-2u$ (минимум $-1$ при $u=1$), при $u<0$ $h=-u^2-2u$ '
            '(максимум $1$ при $u=-1$). Она возрастает на $(-\\infty;-1]$ до 1, убывает на $[-1;1]$ до $-1$ и возрастает на $[1;+\\infty)$.\n\n'
            'Горизонтальная прямая $h=c$ пересекает график в двух точках только при $c=1$ и $c=-1$ (касание в вершине), в остальных случаях — '
            'в одной или трёх. $-(a+2)=1$: $a=-3$; $-(a+2)=-1$: $a=-1$.')


class LogLinesCircle(Param):
    """Логарифмы/корни с y² = a²x² и окружностью через начало координат: ровно два решения"""
    lo, hi, step = -6, 6, Fraction(1, 9)
    DATA = {
        'CF1240': dict(R=6, circ=(1, 3), strict=True, kind='log7'),
        'FF3CE9': dict(R=4, circ=(4, 2), strict=True, kind='log3'),
        '8F61E2': dict(R=6, circ=(1, 3), strict=False, kind='sqrt'),
    }
    fipi = {k: dict(kind=k) for k in DATA}

    def _vals(self, p):
        d = self.DATA[p['kind']]
        R, (c1, c2) = d['R'], d['circ']
        # вторая точка на y = kx: x = (2c₁ + 2c₂k)/(1 + k²), y = kx; y < R ⇔ (2c₁k + 2c₂k²) < R(1 + k²)
        k = sp.Symbol('k')
        yk = (2 * c1 * k + 2 * c2 * k ** 2) / (1 + k ** 2)
        kmax = sp.solve(sp.Eq(2 * c1 * k + 2 * c2 * k ** 2, R * (1 + k ** 2)), k)
        kz = sp.Rational(-c1, c2)        # вторая точка совпадает с началом координат
        return d, R, c1, c2, kmax, kz

    def aset(self, p):
        d, R, c1, c2, kmax, kz = self._vals(p)
        km = [v for v in kmax if v.is_real][0]
        z = abs(kz)
        big = U(I(-oo, -km), I(km, oo)) if d['strict'] else U(I.open(-oo, -km), I.open(km, oo))
        good_z = (z < km)
        return U(sp.Complement(big, F(z, -z)), F(0), F(z, -z) if good_z else sp.S.EmptySet)

    def ok(self, p, a):
        d = self.DATA[p['kind']]
        R, (c1, c2) = d['R'], d['circ']
        P = Points()
        for k in (a, -a):
            for r_ in poly_roots((x - c1) ** 2 + (k * x - c2) ** 2 - c1 ** 2 - c2 ** 2):
                y = k * r_
                val = num(R ** 2 - y ** 2)
                if (d['strict'] and val > 1e-30) or (not d['strict'] and val > -1e-30):
                    P.add(r_, y)
        return len(P) == 2

    def cond(self, p):
        d = self.DATA[p['kind']]
        R, (c1, c2) = d['R'], d['circ']
        circ = f'x^2+y^2={2 * c1}x+{2 * c2}y'.replace('=2x', '=2x')
        if d['kind'] == 'sqrt':
            first = f'\\sqrt{{{R * R}-y^2}}=\\sqrt{{{R * R}-a^2x^2}}'
        else:
            b = d['kind'][3:]
            first = f'\\log_{b}({R * R}-y^2)=\\log_{b}({R * R}-a^2x^2)'
        return (f'Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{{cases}}{first},\\\\ {circ}\\end{{cases}}$$ '
                'имеет ровно два различных решения.')

    def solution(self, p):
        d, R, c1, c2, kmax, kz = self._vals(p)
        km = [v for v in kmax if v.is_real][0]
        z = abs(kz)
        rel = '<' if d['strict'] else '\\le '
        nrel = '\\ge ' if d['strict'] else '>'
        dom = '>' if d['strict'] else '\\ge '
        tail = (f'или $a={tx(z)}$ (тогда точка для $k=-a$ совпадает с $O$, а точка для $k=a$ подходит, так как ${tx(z)}{rel}{tx(km)}$)' if z < km else
                f'кроме $a={tx(z)}$ (тогда точка для $k=-a$ совпадает с $O$, а точка для $k=a$ не подходит)')
        return (
            f'Первое уравнение равносильно $y^2=a^2x^2$ при условии ${R * R}-y^2{dom}0$, то есть $y=\\pm ax$, $|y|{rel}{R}$. '
            f'Второе — окружность $(x-{c1})^2+(y-{c2})^2={c1 * c1 + c2 * c2}$, проходящая через начало координат $O$; точка $O$ — решение при любом $a$. '
            f'Прямая $y=kx$ пересекает окружность ещё в точке с $x=\\frac{{{2 * c1}+{2 * c2}k}}{{1+k^2}}$, '
            f'$y=\\frac{{{2 * c1}k+{2 * c2}k^2}}{{1+k^2}}$; при $k={tx(kz)}$ она совпадает с $O$.\n\n'
            f'Неравенство $y>-{R}$ для этой точки выполнено всегда, а $y{rel}{R}$ равносильно $k{rel}{tx(km)}$.\n\n'
            f'При $a=0$ обе прямые — это $y=0$, решений два: $O$ и $({2 * c1};0)$. При $a\\ne0$ решений $1+n$, где $n$ — число подходящих вторых '
            f'точек для $k=a$ и $k=-a$. По симметрии рассмотрим $a>0$: точка для $k=-a$ подходит при $a\\ne{tx(z)}$, точка для $k=a$ — при '
            f'$a{rel}{tx(km)}$. Ровно два решения: $a{nrel}{tx(km)}$, {tail}. Для $a<0$ — симметрично.')


class LogLinesParam(Param):
    """log(a − y²) = log(a − x²) (или корни) и окружность: ровно два решения"""
    lo, hi, step = -3, 20, Fraction(1, 5)
    DATA = {
        'D354DE': dict(circ=(1, 3), strict=True, base='11', ans=lambda: I.Lopen(4, 16)),
        '3D7367': dict(circ=(1, 2), strict=False, base=None, ans=lambda: I.Ropen(1, 9)),
    }
    fipi = {k: dict(kind=k) for k in DATA}

    def aset(self, p):
        return self.DATA[p['kind']]['ans']()

    def ok(self, p, a):
        d = self.DATA[p['kind']]
        c1, c2 = d['circ']
        P = Points()
        for k in (1, -1):
            for r_ in poly_roots((x - c1) ** 2 + (k * x - c2) ** 2 - c1 ** 2 - c2 ** 2):
                v = num(a - r_ ** 2)
                if (d['strict'] and v > 1e-30) or (not d['strict'] and v > -1e-30):
                    P.add(r_, k * r_)
        return len(P) == 2

    def cond(self, p):
        d = self.DATA[p['kind']]
        c1, c2 = d['circ']
        first = f'\\log_{{{d["base"]}}}(a-y^2)=\\log_{{{d["base"]}}}(a-x^2)' if d['base'] else '\\sqrt{a-y^2}=\\sqrt{a-x^2}'
        return (f'Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{{cases}}{first},\\\\ x^2+y^2={2 * c1}x+{2 * c2}y\\end{{cases}}$$ '
                'имеет ровно два различных решения.')

    def solution(self, p):
        d = self.DATA[p['kind']]
        c1, c2 = d['circ']
        rel = '>' if d['strict'] else '\\ge '
        x1, x2 = sp.Rational(2 * c1 + 2 * c2, 2), sp.Rational(2 * c1 - 2 * c2, 2)
        pts = [(0, 0), (x1, x1), (x2, -x2)]
        need = sorted(v[0] ** 2 for v in pts)
        return (
            f'Первое уравнение равносильно $y^2=x^2$ при $a-x^2{rel}0$, то есть $y=\\pm x$. Окружность $x^2+y^2={2 * c1}x+{2 * c2}y$ проходит через '
            f'начало координат и пересекает прямую $y=x$ ещё в точке $({tx(x1)};{tx(x1)})$, прямую $y=-x$ — в точке $({tx(x2)};{tx(-x2)})$.\n\n'
            f'Точка подходит, если $a{rel}x^2$: для $(0;0)$ — $a{rel}0$, для второй и третьей точек — $a{rel}{tx(need[1])}$ и $a{rel}{tx(need[2])}$. '
            'Ровно две подходящие точки — когда выполнены два первых условия, но не третье: ' + show(self.aset(p)).strip('$') + '.')


class TwoCirclesA(Param):
    """x² + y² = 6x + 8y − 9 и x² + y² = a²: ровно два решения"""
    fipi = {'DADE95': {}}
    lo, hi, step = -12, 12, Fraction(1, 7)

    def aset(self, p):
        return U(I.open(-9, -1), I.open(1, 9))

    def ok(self, p, a):
        # вычитаем: 6x + 8y − 9 = a² → y = (a² + 9 − 6x)/8
        yf = lambda t: (a ** 2 + 9 - 6 * t) / 8  # noqa: E731
        return count_points([(x ** 2 + yf(x) ** 2 - a ** 2, yf, lambda t, y: True)]) == 2

    def cond(self, p):
        return ('Найдите все значения $a$, при каждом из которых система уравнений $$\\begin{cases}x^2+y^2=6x+8y-9,\\\\ x^2+y^2=a^2\\end{cases}$$ '
                'имеет ровно два различных решения.')

    def solution(self, p):
        return (
            'Первое уравнение: $(x-3)^2+(y-4)^2=16$ — окружность с центром $(3;4)$ радиуса 4; второе — окружность с центром $O$ радиуса $|a|$ '
            '(при $a=0$ — точка $O$, не лежащая на первой окружности). Расстояние между центрами $5$. Две общие точки — когда '
            '$|4-|a||<5<4+|a|$, то есть $1<|a|<9$.')


TEMPLATES = [c() for c in Param.__subclasses__() if c.__module__ == __name__ and c is not SqrtLogProduct] + \
            [c() for c in SqrtLogProduct.__subclasses__() if c.__module__ == __name__]
EXTRA = []

# Подтемы (фильтр в банке) и сложность 1–4 (1 базовый … 4 «гроб») по семействам
CIRCLES, ABS, ROOTS, POLY = ('Графический метод: окружности и прямые', 'Уравнения и системы с модулем',
                             'Корни, логарифмы и тригонометрия', 'Многочлены, дроби и замена переменной')
SECTION = {
    CIRCLES: {'CircleTwoLines': 2, 'CircleSqrtPencil': 2, 'TwoParallelLinesCircle': 1, 'SegmentSystem': 2,
              'ExpCircleSymmetric': 3, 'CircleTwoLinesProduct': 3, 'LogLinesCircle': 3, 'TwoCirclesA': 3,
              'QuarticCircleLine': 3, 'QuarticDifference': 3, 'AbsTwoCircles': 3, 'AbsQuadCircles': 3},
    ABS: {'AbsProductLine': 1, 'AbsParabolas': 2, 'AbsSumSqrt': 2, 'LineTwoParabolasAbs': 2, 'ExpAbsFactor': 2,
          'VShapeLens': 3, 'SystemXAbsY': 3, 'AbsXQuadratic': 3, 'AbsComposite': 4, 'EvenQuartic': 4},
    ROOTS: {'LogSquares': 2, 'TanSquares': 2, 'ParabolaSqrtLine': 2, 'HyperbolaSqrtLine': 2, 'SystemProductSqrt3': 2,
            'SqrtQuartic': 3, 'SqrtLogEq': 3, 'SqrtEqualSegment': 3, 'LogLinesParam': 3},
    POLY: {'FractionTwoRoots': 1, 'QuadraticInT': 1, 'ParabolaTwoLines': 2, 'FactorPoly': 3},
}
for _t in TEMPLATES:
    _t.topic, _t.difficulty = next((s, d[type(_t).__name__]) for s, d in SECTION.items() if type(_t).__name__ in d)
