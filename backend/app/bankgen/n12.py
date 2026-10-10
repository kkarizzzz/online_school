"""
№ 12. Наибольшее и наименьшее значение функции, точки экстремума.

Оригиналы ФИПИ решаются в общем виде: функция из условия разбирается в sympy, ищется производная,
её нули и знаки. Решение пишется по шагам этого анализа. Генераторы аналогов подбирают коэффициенты так,
чтобы точки экстремума и значения были целыми, а ответ ещё раз проверяется тем же анализом.
"""
import math
import random
import re
from fractions import Fraction

import sympy as sp

from app.bankgen.core import Rendered, Template, compact, dec, frac, poly, tex_num
from app.bankgen.texmath import to_sympy

X = sp.Symbol('x', real=True)


def _latex(e) -> str:
    s = sp.latex(e, ln_notation=True, mul_symbol='dot').replace('\\cdot', '\\cdot ')
    s = s.replace('\\left(', '(').replace('\\right)', ')')
    s = re.sub(r'\\(sin|cos|tan|ln|log)\{\(x \)\}', r'\\\1 x', s)        # \sin{(x )} → \sin x
    return re.sub(r'\\(sin|cos|tan|ln|log)\{\(([^{}()]+?) \)\}', r'\\\1(\2)', s)  # \ln{(x + 1 )} → \ln(x + 1)


def _interval(dom) -> str:
    """(0, ∞) → (0;+\\infty), как пишут в школе"""
    if isinstance(dom, sp.Interval):
        left = '(' if dom.left_open else '['
        right = ')' if dom.right_open else ']'
        lo = '-\\infty' if dom.start == -sp.oo else _latex(dom.start)
        hi = '+\\infty' if dom.end == sp.oo else _latex(dom.end)
        return f'{left}{lo};{hi}{right}'
    return _latex(dom).replace('\\left', '').replace('\\right', '')


def _to_fraction(v) -> Fraction:
    v = sp.nsimplify(v)
    if not v.is_Rational:
        raise ValueError(f'ответ не рациональный: {v}')
    return Fraction(int(v.p), int(v.q))


def _parse(tex: str) -> sp.Expr:
    e = to_sympy(tex)
    return e.subs(sp.Symbol('x'), X)


def _domain(expr):
    from sympy.calculus.util import continuous_domain
    return continuous_domain(expr, X, sp.S.Reals)


def _sign(d, x0) -> int:
    v = float(d.subs(X, x0))
    return 1 if v > 0 else -1 if v < 0 else 0


def analyze(expr, a=None, b=None):
    """Производная, критические точки (с типом) в области/на отрезке"""
    d = sp.simplify(sp.diff(expr, X))
    dom = _domain(expr)
    region = dom if a is None else sp.Intersection(dom, sp.Interval(a, b))
    crit = sp.solveset(sp.Eq(d, 0), X, region)
    if crit.is_empty:
        points = []
    elif isinstance(crit, sp.FiniteSet):
        points = sorted(crit, key=lambda c: float(c))
    else:
        raise ValueError(f'критические точки не конечны: {crit}')
    kinds = []
    for c in points:
        eps = 1e-6
        left, right = _sign(d, c - eps), _sign(d, c + eps)
        kinds.append('min' if (left, right) == (-1, 1) else 'max' if (left, right) == (1, -1) else 'none')
    return d, points, kinds, dom


def _factor_tex(d) -> str:
    f = sp.factor(sp.together(d))
    return _latex(f)


ASK_POINT = r'Найдите точку (минимума|максимума) функции \$y=(.+?)\$\.?$'
ASK_VALUE = r'Найдите (наименьшее|наибольшее) значение функции\s*\$y=(.+?)\$\s*на отрезке \$\[(.+?);(.+?)\]\$\.?$'


class Extremum(Template):
    number = 12
    topic = 'Исследование функции с помощью производной'
    code = '12.generic'

    def match(self, task):
        text = compact(task['condition']).strip()
        m = re.search(ASK_POINT, text)
        if m:
            return {'ask': 'min-point' if m.group(1) == 'минимума' else 'max-point', 'f': m.group(2)}
        m = re.search(ASK_VALUE, text)
        if m:
            return {'ask': 'min-value' if m.group(1) == 'наименьшее' else 'max-value', 'f': m.group(2), 'a': m.group(3), 'b': m.group(4)}
        return None

    def _bounds(self, p):
        return to_sympy(p['a']), to_sympy(p['b'])

    def solve(self, p):
        expr = _parse(p['f'])
        if p['ask'].endswith('point'):
            _, points, kinds, _ = analyze(expr)
            want = 'min' if p['ask'] == 'min-point' else 'max'
            found = [c for c, k in zip(points, kinds) if k == want]
            if len(found) != 1:
                raise ValueError(f'точек {want}: {len(found)}')
            return _to_fraction(found[0])
        a, b = self._bounds(p)
        _, points, _, _ = analyze(expr, a, b)
        cands = [a, b] + points
        values = [sp.nsimplify(sp.simplify(expr.subs(X, c))) for c in cands]
        best = min(values, key=lambda v: float(v)) if p['ask'] == 'min-value' else max(values, key=lambda v: float(v))
        return _to_fraction(best)

    def verify(self, p, ans):
        # проверка численно: значение/точка на мелкой сетке не лучше найденного
        expr = _parse(p['f'])
        f = sp.lambdify(X, expr, 'math')
        if p['ask'].endswith('value'):
            a, b = (float(x) for x in self._bounds(p))
            grid = [a + (b - a) * i / 4000 for i in range(4001)]
            vals = []
            for x in grid:
                try:
                    vals.append(f(x))
                except (ValueError, ZeroDivisionError):
                    pass
            target = min(vals) if p['ask'] == 'min-value' else max(vals)
            return abs(target - float(ans)) < 1e-3 * max(1, abs(float(ans)))
        x0 = float(ans)
        try:
            y0, yl, yr = f(x0), f(x0 - 1e-3), f(x0 + 1e-3)
        except (ValueError, ZeroDivisionError):
            return False
        return (yl > y0 < yr) if p['ask'] == 'min-point' else (yl < y0 > yr)

    def render(self, p):
        expr = _parse(p['f'])
        ftex = p['f'].replace('·', '\\cdot ')
        if p['ask'].endswith('point'):
            word = 'минимума' if p['ask'] == 'min-point' else 'максимума'
            cond = f'Найдите точку {word} функции $y={ftex}$.'
            d, points, kinds, dom = analyze(expr)
            sol = self._derivative_text(expr, d, dom)
            sol += self._critical_text(points, kinds)
        else:
            word = 'наименьшее' if p['ask'] == 'min-value' else 'наибольшее'
            a, b = self._bounds(p)
            cond = f'Найдите {word} значение функции $y={ftex}$ на отрезке $[{p["a"]};{p["b"]}]$.'
            d, points, kinds, dom = analyze(expr, a, b)
            sol = self._derivative_text(expr, d, dom)
            ans = self.solve(p)
            if not points:
                inc = _sign(d, (a + b) / 2) > 0
                end = (a if inc else b) if p['ask'] == 'min-value' else (b if inc else a)
                sol += (f'На отрезке $[{p["a"]};{p["b"]}]$ производная не обращается в ноль и {"положительна" if inc else "отрицательна"}, '
                        f'функция {"возрастает" if inc else "убывает"}. {word.capitalize()} значение — на {"левом" if end == a else "правом"} конце: '
                        f'$$y\\left({_latex(end)}\\right)={tex_num(ans)}.$$')
            else:
                sol += self._critical_text(points, kinds)
                c = points[0]
                yc = sp.nsimplify(sp.simplify(expr.subs(X, c)))
                k = kinds[0]
                if len(points) == 1 and ((k == 'min' and p['ask'] == 'min-value') or (k == 'max' and p['ask'] == 'max-value')):
                    sol += (f' На отрезке это единственная точка экстремума, и в ней достигается {word} значение: '
                            f'$$y\\left({_latex(c)}\\right)={_latex(yc)}.$$')
                else:
                    ends = ', '.join(f'$y({_latex(e)})={_latex(sp.nsimplify(sp.simplify(expr.subs(X, e))))}$' for e in (a, b))
                    sol += f' Сравним значения в критических точках и на концах: $y({_latex(c)})={_latex(yc)}$, {ends}.'
        return Rendered(cond, sol + f'\n\n**Ответ:** {dec(self.solve(p))}.')

    @staticmethod
    def _derivative_text(expr, d, dom) -> str:
        dom_tex = '' if dom == sp.S.Reals else f'Область определения: $x\\in {_interval(dom)}$. '
        return f'{dom_tex}Найдём производную: $$y\'={_factor_tex(d)}.$$ '

    @staticmethod
    def _critical_text(points, kinds) -> str:
        if not points:
            return 'Производная в ноль не обращается.'
        listing = ', '.join(f'$x={_latex(c)}$' for c in points)
        parts = []
        for c, k in zip(points, kinds):
            if k == 'min':
                parts.append(f'при переходе через $x={_latex(c)}$ производная меняет знак с «−» на «+» — это точка минимума')
            elif k == 'max':
                parts.append(f'при переходе через $x={_latex(c)}$ производная меняет знак с «+» на «−» — это точка максимума')
            else:
                parts.append(f'в точке $x={_latex(c)}$ знак производной не меняется — экстремума нет')
        return f'Производная равна нулю при {listing}. ' + '; '.join(parts).capitalize() + '.'

    def sample(self, rng):
        return GENERATORS[rng.randrange(len(GENERATORS))](rng)

    def nice(self, x):
        return frac(x).denominator in (1, 2, 4) and abs(x) < 10000


# ---------------------------------------------------------------------------
# Генераторы аналогов (функция в LaTeX + вопрос); ответ считает общий анализ выше
# ---------------------------------------------------------------------------

def _c(d: int) -> str:
    """Свободный член со знаком; ноль не пишем"""
    return f'{d:+d}' if d else ''


def gen_cubic(rng):
    """y = x³ + ax² + bx + c, f' = 3(x−p)(x−q)"""
    p, q = sorted(rng.sample(range(-12, 13), 2))
    if rng.random() < 0.4:
        p = -q if q > 0 else p  # симметричный вид x³ − 3q²x + c
    a, b = Fraction(-3 * (p + q), 2), Fraction(3 * p * q)
    if a.denominator != 1:
        return None
    c = rng.randint(-30, 30)
    return {'ask': rng.choice(['min-point', 'max-point']), 'f': poly([1, a, b, c])}


def gen_three_halves(rng):
    """y = A + Bx − Cx^{3/2}: максимум в x = (2B/3C)²; или x√x − Bx + A — минимум"""
    k = rng.randint(2, 12)            # √x в точке экстремума
    C = rng.choice([1, 2])
    B = Fraction(3 * C * k, 2)
    if B.denominator != 1:
        return None
    A = rng.randint(2, 30)
    power = rng.choice(['x\\sqrt{x}', 'x^{\\frac{3}{2}}'])
    cpow = ('' if C == 1 else str(C)) + power
    if rng.random() < 0.5:
        return {'ask': 'max-point', 'f': f'{A}+{B}x-{cpow}'}
    return {'ask': 'min-point', 'f': f'{cpow}-{B}x+{A}'}


def gen_quad_log(rng):
    """y = ax² + bx + c·ln x + d: f' = (2ax² + bx + c)/x с корнями p < q > 0"""
    p, q = sorted(rng.sample(range(1, 15), 2))
    a = Fraction(rng.choice([1, 1, 2, Fraction(1, 2)]))
    # 2a(x−p)(x−q) = 2a x² − 2a(p+q)x + 2a pq
    b, c = -2 * a * (p + q) / 1, 2 * a * p * q
    b = Fraction(b) / 1
    b = -a * 2 * (p + q) / 2 * 1
    # производная ax² даёт 2ax: нужно 2ax² + b x + c = 2a(x−p)(x−q) → b = −2a(p+q), c = 2a·pq
    b = -2 * a * (p + q)
    c = 2 * a * p * q
    d = rng.randint(-40, 80)
    if b.denominator != 1 or c.denominator != 1:
        return None
    f = f'{poly([a, b, 0])}+{c}\\ln x{_c(d)}'
    return {'ask': rng.choice(['min-point', 'max-point']), 'f': f.replace('+-', '-')}


def gen_lin_log(rng):
    """y = kx − k·ln(x + m) + d: минимум при x = 1 − m;  y = k·ln(x+m) − kx + d: максимум"""
    k = rng.randint(2, 12)
    m = rng.randint(-9, 9)
    d = rng.randint(-15, 15)
    arg = f'x{m:+d}' if m else 'x'
    if rng.random() < 0.5:
        return {'ask': 'min-point', 'f': f'{k}x-{k}\\ln({arg}){_c(d)}'}
    return {'ask': 'max-point', 'f': f'{k}\\ln({arg})-{k}x{_c(d)}'}


def gen_exp(rng):
    """y = (x + a)e^{b − x}: максимум при x = 1 − a"""
    a, b = rng.randint(-12, 12), rng.randint(-15, 15)
    return {'ask': 'max-point', 'f': f'(x{a:+d})e^{{{b}-x}}'.replace('(x+0)', 'x')}


def gen_trig_segment(rng):
    """y = A cos x + Bx + C на отрезке с концом 0: функция монотонна, ответ на конце"""
    A = rng.randint(2, 15)
    B = rng.randint(A + 1, A + 15)
    C = rng.randint(-20, 20)
    if rng.random() < 0.5:
        # возрастает: минимум в левом конце x = 0 на [0; 3π/2]
        return {'ask': 'min-value', 'f': f'{A}\\cos x+{B}x{_c(C)}', 'a': '0', 'b': '\\frac{3\\pi}{2}'}
    return {'ask': 'min-value', 'f': f'{A}\\cos x-{B}x{_c(C)}', 'a': '-\\frac{3\\pi}{2}', 'b': '0'}


def gen_log_segment(rng):
    """y = k·ln(x+m) − kx + d на отрезке вокруг x = 1 − m: максимум равен значению в точке"""
    k = rng.randint(2, 12)
    m = rng.randint(2, 11)
    d = rng.randint(-10, 15)
    x0 = 1 - m
    a = Fraction(2 * x0 - 1, 2)
    return {'ask': 'max-value', 'f': f'{k}\\ln(x+{m})-{k}x{_c(d)}', 'a': dec(a).replace(',', '{,}'), 'b': '0'}


GENERATORS = [gen_cubic, gen_cubic, gen_three_halves, gen_quad_log, gen_lin_log, gen_exp, gen_trig_segment, gen_log_segment]

TEMPLATES = [Extremum()]
EXTRA = []
