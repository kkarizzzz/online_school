"""
Проверка ответов задач с параметром (№ 18): для многих значений a число решений считается
независимо — точно (sympy, рациональное a) или численно по исходному уравнению — и сравнивается
с найденным в решении множеством.
"""
import math
from fractions import Fraction

import sympy as sp

X = sp.Symbol('x')
INF = math.inf


def num(e) -> float:
    return float(sp.N(e, 40))


def poly_roots(expr, var=X) -> list:
    """Вещественные корни многочлена (точно); тождественный ноль — бесконечно много"""
    expr = sp.expand(expr)
    if expr == 0:
        return [INF]
    p = sp.Poly(expr, var)
    if p.degree() <= 0:
        return []
    try:
        return list(p.real_roots())
    except NotImplementedError:      # иррациональные коэффициенты (a = −1 − √5 и т. п.) — корни в радикалах
        return [r_ for r_ in sp.roots(p, multiple=False) if abs(sp.N(sp.im(r_), 30)) < 1e-25]


class Points:
    """Множество решений с отбрасыванием совпадающих (по 40 знакам)"""

    def __init__(self):
        self.items: list[tuple] = []
        self.infinite = False

    def add(self, *coords):
        vals = tuple(num(c) for c in coords)
        if all(max(abs(v - w) for v, w in zip(vals, u)) > 1e-25 * max(1.0, max(abs(t) for t in vals)) for u in self.items):
            self.items.append(vals)

    def __len__(self):
        return 10 ** 9 if self.infinite else len(self.items)


def ge(e, tol=1e-30) -> bool:
    return num(e) >= -tol


def gt(e, tol=1e-30) -> bool:
    return num(e) > tol


def samples(answer: sp.Set, lo, hi, step=Fraction(1, 7), extra=()) -> list:
    """Рациональные a: сетка, точки около концов промежутков ответа и сами концы (если рациональные)"""
    out, a = set(), Fraction(lo)
    while a <= hi:
        out.add(a)
        a += step
    for b in list(_bounds(answer)) + [sp.nsimplify(e) for e in extra]:
        bf = num(b)
        if not math.isfinite(bf):
            continue
        for d in (Fraction(1, 997), Fraction(1, 113), Fraction(1, 31)):
            out.add(Fraction(bf).limit_denominator(10 ** 6) + d)
            out.add(Fraction(bf).limit_denominator(10 ** 6) - d)
        if b.is_Rational:
            out.add(Fraction(int(b.p), int(b.q)))
    return sorted(out)


def _bounds(s):
    if isinstance(s, sp.Union):
        for a in s.args:
            yield from _bounds(a)
    elif isinstance(s, sp.Interval):
        for b in (s.start, s.end):
            if b.is_finite:
                yield b
    elif isinstance(s, sp.FiniteSet):
        yield from s


def verify(answer: sp.Set, ok, lo, hi, step=Fraction(1, 7), extra=()) -> bool:
    """ok(a: sp.Rational) -> bool — выполнено ли условие задачи при данном a"""
    for a in samples(answer, lo, hi, step, extra):
        ar = sp.Rational(a.numerator, a.denominator)
        expected = bool(answer.contains(ar))
        if ok(ar) != expected:
            raise AssertionError(f'a = {ar}: условие {"не " if expected else ""}выполнено, а по ответу {"да" if expected else "нет"}')
    return True


def scan_roots(F, lo, hi, n=4000, points=()) -> int:
    """Число корней F на [lo, hi] численно: смены знака (с отбраковкой полюсов) и точные нули в узлах/точках"""
    roots = []

    def val(x):
        try:
            v = F(x)
            return v if v is not None and math.isfinite(v) else None
        except (ValueError, ZeroDivisionError, OverflowError):
            return None
    xs = [lo + (hi - lo) * i / n for i in range(n + 1)] + [t for t in points if lo <= t <= hi]
    xs = sorted(set(xs))
    vals = [val(x) for x in xs]
    for x, v in zip(xs, vals):
        if v is not None and abs(v) < 1e-11:
            roots.append(x)
    for (x1, v1), (x2, v2) in zip(zip(xs, vals), zip(xs[1:], vals[1:])):
        if v1 is None or v2 is None or abs(v1) < 1e-11 or abs(v2) < 1e-11 or (v1 > 0) == (v2 > 0):
            continue
        a, b, fa = x1, x2, v1
        for _ in range(100):
            m = (a + b) / 2
            fm = val(m)
            if fm is None:
                break
            if (fm > 0) == (fa > 0):
                a, fa = m, fm
            else:
                b = m
        fm = val((a + b) / 2)
        if fm is not None and abs(fm) < 1e-7:
            roots.append((a + b) / 2)
    roots.sort()
    uniq = []
    for r_ in roots:
        if not uniq or abs(r_ - uniq[-1]) > 1e-6:
            uniq.append(r_)
    return len(uniq)
