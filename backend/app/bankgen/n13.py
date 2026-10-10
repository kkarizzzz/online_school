"""
№ 13. Уравнения (вторая часть): а) решить, б) отобрать корни на отрезке.

Решение пишет trig_exp.solve13 (приведение, замены, разложение), ответ подтверждается численно
(trig.numeric_roots). Аналоги собираются из «красивых» корней: сначала выбираем значения sin x / cos x / tg x,
затем строим уравнение и маскируем его формулами приведения.
"""
import math
import random
import re

import sympy as sp

from app.bankgen.core import Rendered, Template, compact
from app.bankgen.texmath import to_sympy
from app.bankgen.trig import TWO_PI, X, _nice_base, in_segment, numeric_roots, series_text
from app.bankgen.trig_exp import solve13

PATTERN = (r'а\) Решите уравнение\s*\$(.+?)\$[.,]?\s*б\) (?:Найдите все корни этого уравнения|Найдите все его корни|Укажите корни этого уравнения),? '
           r'принадлежащие отрезку \$\[(.+?);(.+?)\]\$')


def _clean_bound(s: str) -> str:
    s = re.sub(r'\\text\{([^{}]*)\}', r'\1', s)   # \frac{7\pi}{\text{2}} → \frac{7\pi}{2}
    return s.replace('\\text', '').strip()


def _tex(v) -> str:
    return sp.latex(v).replace('\\left(', '(').replace('\\right)', ')')


def _equation(eq_tex: str):
    left, right = eq_tex.split('=', 1)
    return sp.expand((to_sympy(left) - to_sympy(right)).subs(sp.Symbol('x'), X))


class Equation13(Template):
    number, topic, code, detailed, difficulty = 13, 'Уравнения', '13.equation', True, 2

    def match(self, task):
        text = re.sub(r'\\text\{([^{}]*)\}', r'\1', compact(task['condition']))  # [\frac{7\pi}{\text{2}}\text{;}5\pi]
        m = re.search(PATTERN, text, re.S)
        if not m:
            return None
        return {'eq': m.group(1).rstrip(',.'), 'a': _clean_bound(m.group(2)), 'b': _clean_bound(m.group(3))}

    def _solve_full(self, p):
        expr = _equation(p['eq'])
        res = solve13(expr)
        if res is None:
            raise ValueError('не решилось аналитически')
        steps, roots, kind = res
        a, b = to_sympy(p['a']), to_sympy(p['b'])
        if kind == 'trig':
            seg = in_segment(roots, a, b)
        else:
            seg = [r for r in roots if float(a) - 1e-12 <= float(r) <= float(b) + 1e-12]
        return expr, steps, roots, kind, seg, (a, b)

    def solve(self, p):
        _, _, roots, kind, seg, _ = self._solve_full(p)
        if not roots:
            raise ValueError('нет корней')
        if kind == 'trig':
            a_part = '; '.join(f'${s}$' for s in series_text(roots)).replace('$;', ',$').replace(',$ $', ', ')
            a_part = ', '.join(f'${s}$' for s in series_text(roots)) + ', $k\\in\\mathbb{Z}$'
        else:
            a_part = ', '.join(f'${_tex(r)}$' for r in roots)
        b_part = ', '.join(f'${_tex(r)}$' for r in seg) if seg else 'корней нет'
        return {'accepted': [], 'display': f'а) {a_part}; б) {b_part}'}

    def verify(self, p, answer):
        expr, _, roots, kind, _, _ = self._solve_full(p)
        if kind == 'trig':
            return set(roots) == set(numeric_roots(expr))
        for r in roots:
            if abs(complex(sp.N(expr.subs(X, r), 30))) > 1e-15:
                return False
        return True

    def render(self, p):
        expr, steps, roots, kind, seg, (a, b) = self._solve_full(p)
        cond = (f'а) Решите уравнение $${p["eq"]}.$$\n\nб) Найдите все корни этого уравнения, принадлежащие отрезку $[{p["a"]};{p["b"]}]$.')
        sol = '**а)** ' + '\n\n'.join(steps)
        if kind == 'trig':
            sol += '\n\nОтвет пункта а): ' + ', '.join(f'$x={s}$' for s in series_text(roots)) + ', $k\\in\\mathbb{Z}$.'
            sol += f'\n\n**б)** Отберём корни на отрезке $[{p["a"]};{p["b"]}]$ (длина отрезка меньше $2\\pi$, из каждой серии берём подходящие $k$). '
            sol += self._selection(roots, a, b)
        else:
            sol += f'\n\n**б)** Сравним корни с концами отрезка $[{p["a"]};{p["b"]}]$: ' + '; '.join(
                f'$x={_tex(r)}\\approx {float(r):.3f}$ — {"подходит" if r in seg else "не подходит"}' for r in roots) + \
                f' (концы: ${p["a"]}\\approx {float(a):.3f}$, ${p["b"]}\\approx {float(b):.3f}$).'
        return Rendered(cond, sol + f'\n\n**Ответ:** {self.solve(p)["display"]}.')

    @staticmethod
    def _selection(roots, a, b) -> str:
        lines = []
        for r in sorted(roots, key=lambda v: float(_nice_base(v, TWO_PI))):
            base = _nice_base(r, TWO_PI)
            ks = []
            lo, hi = float(a), float(b)
            for k in range(-12, 13):
                x = sp.nsimplify(base + 2 * k * sp.pi)
                if lo - 1e-12 <= float(x) <= hi + 1e-12:
                    ks.append((k, x))
            if ks:
                lines.append(f'из серии $x={_tex(base)}+2\\pi k$: ' + ', '.join(f'$k={k}$: $x={_tex(x)}$' for k, x in ks))
        if not lines:
            return 'На отрезке корней нет.'
        return '\n\n' + '\n\n'.join(f'- {l};' for l in lines)

    def sample(self, rng):
        gen = rng.choice(GENERATORS)
        p = gen(rng)
        if p is None:
            return None
        p['a'], p['b'] = _segment(rng)
        return p

    def nice(self, answer):
        return 'корней нет' not in answer['display']


# ---------------------------------------------------------------------------
# Генераторы уравнений с «табличными» корнями
# ---------------------------------------------------------------------------

SIN_VALUES = [sp.Rational(1, 2), -sp.Rational(1, 2), sp.sqrt(2) / 2, -sp.sqrt(2) / 2, sp.sqrt(3) / 2, -sp.sqrt(3) / 2, 1, -1, 0]
EXTRA_VALUES = [2, -2, sp.Rational(3, 2), -sp.Rational(3, 2), 3, -3]

# как записать sin x и cos x «замаскированно» (формулы приведения)
SIN_FORMS = ['\\sin x', '-\\sin(x+\\pi)', '\\cos\\left(\\frac{\\pi}{2}-x\\right)', '-\\sin(-x)', '-\\cos\\left(\\frac{\\pi}{2}+x\\right)', '\\sin(\\pi-x)']
COS_FORMS = ['\\cos x', '\\cos(-x)', '-\\cos(\\pi-x)', '\\sin\\left(\\frac{\\pi}{2}+x\\right)', '-\\sin\\left(x-\\frac{\\pi}{2}\\right)', '-\\cos(x+\\pi)']


def _sgn(v) -> str:
    """Слагаемое со знаком: 3 → «+3», −1/2 → «-\frac{1}{2}»"""
    v = sp.nsimplify(v)
    return ('-' if v < 0 else '+') + sp.latex(abs(v))


def _coef_tex(c, first=False) -> str:
    """Коэффициент перед множителем: 1 → «+», −1 → «−», √2 → «+\\sqrt{2}»"""
    c = sp.nsimplify(c)
    if c == 1:
        return '' if first else '+'
    if c == -1:
        return '-'
    s = sp.latex(c)
    if not s.startswith('-') and not first:
        s = '+' + s
    return s


def _term(c, form: str, first=False) -> str:
    if c == 0:
        return ''
    if form.startswith('-'):
        c, form = -c, form[1:]
    return _coef_tex(c, first) + (form if not form.startswith('\\') else form)


def gen_quadratic(rng):
    """A·f² + B·f + C = 0, f = sin x или cos x; квадрат записан через cos 2x или 1 − sin²"""
    func = rng.choice(['sin', 'cos'])
    t1 = sp.S(rng.choice([v for v in SIN_VALUES if v != 0]))
    t2 = sp.S(rng.choice(EXTRA_VALUES + [v for v in SIN_VALUES if v != t1]))
    k = rng.choice([2, 2, 4]) if (t1 + t2).is_rational and (t1 * t2).is_rational else 2
    if not ((t1 + t2) * k).is_rational or not (t1 * t2 * k).is_rational:
        return None
    A, B, C0 = k, -k * (t1 + t2), k * t1 * t2
    if not all(sp.nsimplify(v).is_Rational for v in (A, B, C0)):
        return None
    # A f² через другую функцию: sin²x = 1 − cos²x (или cos 2x = 1 − 2sin²x)
    form = SIN_FORMS if func == 'sin' else COS_FORMS
    other = 'cos' if func == 'sin' else 'sin'
    style = rng.choice(['square-other', 'cos2x'])
    if style == 'square-other':
        # A f² = A − A other²  →  −A other² + B f + (C0 + A) = 0
        eq = (_term(-A, f'\\{other}^2 x', True) + _term(B, rng.choice(form)) + (f'{_sgn(C0 + A)}' if C0 + A else '')) + '=0'
    else:
        if func == 'sin':
            # sin²x = (1 − cos 2x)/2:  A sin² = A/2 − (A/2) cos2x
            eq = _term(-sp.Rational(A, 2), '\\cos 2x', True) + _term(B, rng.choice(form)) + (f'{_sgn(C0 + sp.Rational(A, 2))}' if C0 + sp.Rational(A, 2) else '') + '=0'
        else:
            eq = _term(sp.Rational(A, 2), '\\cos 2x', True) + _term(B, rng.choice(form)) + (f'{_sgn(C0 + sp.Rational(A, 2))}' if C0 + sp.Rational(A, 2) else '') + '=0'
    return {'eq': eq.replace('+-', '-')}


def gen_factor(rng):
    """sin 2x + k·sin x = 0, sin 2x + k cos x = 0 — вынесение множителя"""
    k = rng.choice([1, -1, sp.sqrt(2), -sp.sqrt(2), sp.sqrt(3), -sp.sqrt(3)])
    func = rng.choice(['sin', 'cos'])
    form = rng.choice(SIN_FORMS if func == 'sin' else COS_FORMS)
    return {'eq': f'\\sin 2x{_term(k, form)}=0'.replace('+-', '-')}


def gen_homogeneous(rng):
    """a·sin²x + b·sin x cos x + c·cos²x = 0 с корнями tg x ∈ {±1, ±√3, ±√3/3}"""
    vals = [1, -1, sp.sqrt(3), -sp.sqrt(3), sp.sqrt(3) / 3, -sp.sqrt(3) / 3]
    t1, t2 = rng.sample(vals, 2)
    s, p = sp.nsimplify(t1 + t2), sp.nsimplify(t1 * t2)
    # a(tg − t1)(tg − t2): a tg² − a s tg + a p → a sin² − a s sin cos + a p cos²
    a = 1 if s.is_rational else (sp.sqrt(3) if (s * sp.sqrt(3)).is_rational else None)
    if a is None:
        return None
    a_ = sp.nsimplify(a)
    terms = [(a_, '\\sin^2 x'), (sp.nsimplify(-a_ * s), '\\sin x\\cos x'), (sp.nsimplify(a_ * p), '\\cos^2 x')]
    if rng.random() < 0.5:
        terms[1] = (sp.nsimplify(-a_ * s / 2), '\\sin 2x')
    eq = ''.join(_term(c, f, i == 0) for i, (c, f) in enumerate(terms) if c != 0) + '=0'
    return {'eq': eq.replace('+-', '-')}


def gen_exp_quadratic(rng):
    """a^{2f} − (p+q)·a^{f} + pq = 0 с a^f = p, q, где f = sin x или cos x"""
    a = rng.choice([2, 3, 4, 9])
    func = rng.choice(['\\sin x', '\\cos x'])
    vals = [sp.Rational(1, 2), -sp.Rational(1, 2), 1, 0, -1]
    f1, f2 = rng.sample(vals, 2)
    p, q = sp.Integer(a) ** f1, sp.Integer(a) ** f2
    if not (p.is_rational and q.is_rational):
        return None
    s, pr = p + q, p * q
    den = sp.ilcm(s.q, pr.q)
    c2, c1, c0 = den, -s * den, pr * den
    eq = (f'{c2 if c2 != 1 else ""}\\cdot {a * a}^{{{func}}}' if c2 != 1 else f'{a * a}^{{{func}}}') + \
         f'{_sgn(c1)}\\cdot {a}^{{{func}}}{_sgn(c0)}=0'
    return {'eq': eq.replace('+-', '-').replace('1\\cdot ', '')}


def gen_log(rng):
    """log₂²(sin x) + k·log₂(sin x) = 0 с ОДЗ"""
    func = rng.choice(['\\sin x', '\\cos x'])
    k = rng.choice([1, 2])
    return {'eq': f'\\log_2^2({func})+{k if k != 1 else ""}\\log_2({func})=0'.replace('+1\\log', '+\\log')}


GENERATORS = [gen_quadratic, gen_quadratic, gen_quadratic, gen_factor, gen_homogeneous, gen_exp_quadratic, gen_log]


def _segment(rng):
    """Отрезок длиной 3π/2 с концами, кратными π/2, как в ЕГЭ"""
    start = rng.randint(-10, 8)
    def t(n):
        if n == 0:
            return '0'
        sign = '-' if n < 0 else ''
        n = abs(n)
        if n % 2 == 0:
            m = n // 2
            return f'{sign}{m if m != 1 else ""}\\pi'
        return f'{sign}\\frac{{{n if n != 1 else ""}\\pi}}{{2}}'
    return t(start), t(start + 3)


TEMPLATES = [Equation13()]
EXTRA = []
