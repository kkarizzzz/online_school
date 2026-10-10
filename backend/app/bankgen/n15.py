"""
№ 15. Неравенства (вторая часть).

Решение пишет ineq.solve_inequality (ОДЗ, замена, метод интервалов), ответ проверяется ineq.check:
знак выражения в тысячах точек сравнивается с найденным множеством.
"""
import random
import re

import sympy as sp

from app.bankgen.core import Rendered, Template, compact
from app.bankgen.ineq import check, latex_set, solve_inequality

PATTERN = r'Решите неравенство\s*\$(.+?)\$\.?\s*$'


class Inequality15(Template):
    number, topic, code, detailed, difficulty = 15, 'Неравенства', '15.inequality', True, 2

    def match(self, task):
        m = re.search(PATTERN, compact(task['condition']).strip(), re.S)
        return {'ineq': m.group(1).rstrip('.,')} if m else None

    def _full(self, p):
        if '_res' not in p:
            p['_res'] = solve_inequality(p['ineq'])
        return p['_res']

    def solve(self, p):
        steps, ans, expr, rel, logs = self._full(p)
        if ans is sp.S.EmptySet:
            raise ValueError('пустое множество')
        return {'accepted': [], 'display': f'$x\\in {latex_set(ans)}$'}

    def verify(self, p, answer):
        steps, ans, expr, rel, logs = self._full(p)
        return check(expr, rel, ans, logs)

    def render(self, p):
        steps, ans, *_ = self._full(p)
        cond = f'Решите неравенство $${p["ineq"]}.$$'
        return Rendered(cond, '\n\n'.join(steps) + f'\n\n**Ответ:** $x\\in {latex_set(ans)}$.')

    def sample(self, rng):
        return rng.choice(GENERATORS)(rng)

    def nice(self, answer):
        return 'sqrt' not in answer['display'] or True


def _sgn(v) -> str:
    v = sp.nsimplify(v)
    return ('-' if v < 0 else '+') + sp.latex(abs(v))


def gen_exp_quadratic(rng):
    """a^{2x} − (p+q)·a^{x} + pq (≤|≥) 0"""
    a = rng.choice([2, 3, 5])
    e1, e2 = sorted(rng.sample(range(-1, 5), 2))
    p_, q_ = sp.Integer(a) ** e1, sp.Integer(a) ** e2
    rel = rng.choice(['\\le', '\\ge'])
    s, pr = p_ + q_, p_ * q_
    den = sp.ilcm(s.q, pr.q)
    c2, c1, c0 = den, -s * den, pr * den
    lead = f'{c2}\\cdot ' if c2 != 1 else ''
    return {'ineq': f'{lead}{a * a}^x{_sgn(c1)}\\cdot {a}^x{_sgn(c0)}{rel}0'.replace('+1\\cdot', '+').replace('-1\\cdot', '-')}


def gen_log_quadratic(rng):
    """log_a²(f) − (p+q)·log_a(f) + pq ≥ 0, f = x² − c или x"""
    a = rng.choice([2, 3])
    t1, t2 = sorted(rng.sample(range(0, 5), 2))
    c = rng.choice([0, 0, 4, 9, 16])
    f = 'x' if c == 0 else f'(x^2-{c})'
    rel = rng.choice(['\\ge', '\\le'])
    return {'ineq': f'\\log_{a}^2{f}{_sgn(-(t1 + t2))}\\log_{a}{f}{_sgn(t1 * t2)}{rel}0'.replace('+0{', '{').replace('+0\\ge', '\\ge').replace('+0\\le', '\\le')}


def gen_exp_fraction(rng):
    """k/(a^x + m) ≥ 1/(a^x − n)"""
    a = rng.choice([2, 3])
    n = sp.Integer(a) ** rng.randint(2, 4)
    m = sp.Integer(a) ** rng.randint(1, 3)
    k = rng.choice([2, 3, 4])
    rel = rng.choice(['\\ge', '\\le'])
    return {'ineq': f'\\frac{{{k}}}{{{a}^x+{m}}}{rel}\\frac{{1}}{{{a}^x-{n}}}'}


def gen_prime_split(rng):
    """(a^x − b)(c^x − d) / ((x − u)(x − v)) ≥ 0 с разложением по простым основаниям"""
    a, c = rng.sample([2, 3, 5], 2)
    b, d = rng.choice([c, c * c]), rng.choice([a, a * a])
    u, v = sorted(rng.sample(range(-1, 5), 2))
    num = f'{a * c}^x{_sgn(-d)}\\cdot {a}^x{_sgn(-b)}\\cdot {c}^x{_sgn(b * d)}'
    den = sp.latex(sp.expand((sp.Symbol('x') - u) * (sp.Symbol('x') - v)))
    rel = rng.choice(['\\ge', '\\le'])
    return {'ineq': f'\\frac{{{num}}}{{{den}}}{rel}0'.replace('1\\cdot ', '')}


def gen_log_base(rng):
    """log_{a²}(x + k) + log_{(x+k)²} a ≥ 5/4: t/2 + 1/(2t) ≥ 5/4, t = log_a(x + k)"""
    a = rng.choice([2, 3])
    k = rng.randint(1, 6)
    sq = f'x^2+{2 * k}x+{k * k}'
    return {'ineq': f'\\log_{{{a * a}}}(x+{k})+\\log_{{{sq}}}{a}\\ge\\frac{{5}}{{4}}'}


GENERATORS = [gen_exp_quadratic, gen_log_quadratic, gen_exp_fraction, gen_prime_split, gen_log_base]

TEMPLATES = [Inequality15()]
EXTRA = []
