"""№ 7. Вычисления и преобразования"""
import math
import random
import re
from fractions import Fraction

import sympy as sp

from app.bankgen.core import Rendered, Template, dec, frac, par, tex_frac, tex_num
from app.bankgen.texmath import equals, numeric, to_sympy

ASK = 'Найдите значение выражения'
EXPR = ASK + r' \$(.+?)\$\.?$'


def exact(tex: str, subs: dict | None = None) -> Fraction:
    """Значение выражения как Fraction (ответы № 7 — конечные дроби)"""
    v = numeric(tex, subs)
    if abs(v.imag) > 1e-9:
        raise ValueError('комплексное значение')
    f = Fraction(v.real).limit_denominator(10000)
    if abs(float(f) - v.real) > 1e-9 * max(1, abs(v.real)):
        raise ValueError(f'не рациональное: {v.real}')
    return f


class ExprTemplate(Template):
    number = 7
    family = r''  # регулярка по самому выражению

    def match(self, task):
        from app.bankgen.core import compact
        m = re.search(EXPR, compact(task['condition']).strip(), re.S)
        if not m:
            return None
        expr = m.group(1)
        f = re.fullmatch(self.family, expr)
        if not f:
            return None
        try:
            p = self.parse_expr(f)
        except (ValueError, ZeroDivisionError, KeyError):
            return None
        if p is None:
            return None
        p['expr'] = expr
        return p

    def parse_expr(self, f: re.Match) -> dict | None:
        return {}

    def solve(self, p):
        return exact(p['expr'])

    def verify(self, p, answer):
        return equals(p['expr'], answer)

    def render(self, p):
        return Rendered(f'{ASK} ${p["expr"]}$.', self.explain(p) + f'\n\n**Ответ:** {dec(self.solve(p))}.')

    def explain(self, p) -> str:
        raise NotImplementedError


DEG = r'(\d+)\^\\circ'
K = r'(\d*)'


def _k(s: str) -> int:
    return int(s) if s else 1


# ---------------------------------------------------------------------------
# Тригонометрия
# ---------------------------------------------------------------------------

class SinCosOverSinDouble(ExprTemplate):
    """K·sin a·cos a / sin 2a = K/2"""
    topic, code = 'Тригонометрические выражения', '7.trig.sin2a'
    family = r'\\frac\{' + K + r'\\sin' + DEG + r'·\\cos' + DEG + r'\}\{\\sin' + DEG + r'\}'

    def parse_expr(self, f):
        k, a, a2, b = _k(f.group(1)), int(f.group(2)), int(f.group(3)), int(f.group(4))
        if a != a2 or b != 2 * a:
            return None
        return {'k': k, 'a': a}

    def explain(self, p):
        k, a = p['k'], p['a']
        return (f'По формуле синуса двойного угла $\\sin {2 * a}^\\circ=2\\sin {a}^\\circ\\cos {a}^\\circ$, поэтому\n\n'
                f'$$\\frac{{{k}\\sin {a}^\\circ\\cdot\\cos {a}^\\circ}}{{\\sin {2 * a}^\\circ}}'
                f'=\\frac{{{k}\\sin {a}^\\circ\\cdot\\cos {a}^\\circ}}{{2\\sin {a}^\\circ\\cos {a}^\\circ}}=\\frac{{{k}}}{{2}}={tex_num(Fraction(k, 2))}.$$')

    def sample(self, rng):
        k = rng.randint(2, 40)
        a = rng.randint(11, 87)
        if 2 * a == 90 or a == 45 or a == 60 or a == 30:
            return None
        return {'k': k, 'a': a, 'expr': f'\\frac{{{k}\\sin {a}^\\circ\\cdot\\cos {a}^\\circ}}{{\\sin {2 * a}^\\circ}}'}

    def nice(self, x):
        return frac(x).denominator in (1, 2)


class SinDoubleOverProduct(ExprTemplate):
    """K·sin 2a / (sin a · sin(90°−a))  или  / (cos a · cos(90°−a)) = 2K"""
    topic, code = 'Тригонометрические выражения', '7.trig.reduce'
    family = r'\\frac\{' + K + r'\\sin' + DEG + r'\}\{\\(sin|cos)' + DEG + r'·\\(sin|cos)' + DEG + r'\}'

    def parse_expr(self, f):
        k, b = _k(f.group(1)), int(f.group(2))
        f1, a, f2, c = f.group(3), int(f.group(4)), f.group(5), int(f.group(6))
        if f1 != f2 or a + c != 90 or (b != 2 * a and b != 2 * c):
            return None
        if b != 2 * a:
            a, c = c, a
        return {'k': k, 'a': a, 'f': f1}

    def explain(self, p):
        k, a, f = p['k'], p['a'], p['f']
        c = 90 - a
        other = 'cos' if f == 'sin' else 'sin'
        return (
            f'По формуле приведения $\\{f} {c}^\\circ=\\{f} (90^\\circ-{a}^\\circ)=\\{other} {a}^\\circ$, '
            f'а по формуле двойного угла $\\sin {2 * a}^\\circ=2\\sin {a}^\\circ\\cos {a}^\\circ$. Тогда\n\n'
            f'$${p["expr"].replace("·", "\\cdot ")}'
            f'=\\frac{{{k}\\cdot 2\\sin {a}^\\circ\\cos {a}^\\circ}}{{\\sin {a}^\\circ\\cos {a}^\\circ}}={2 * k}.$$'
        )

    def sample(self, rng):
        k = rng.randint(2, 30)
        a = rng.randint(5, 85)
        if a in (30, 45, 60):
            return None
        f = rng.choice(['sin', 'cos'])
        first, second = (a, 90 - a) if rng.random() < 0.5 else (90 - a, a)
        return {'k': k, 'a': a, 'f': f,
                'expr': f'\\frac{{{k}\\sin {2 * a}^\\circ}}{{\\{f} {first}^\\circ\\cdot\\{f} {second}^\\circ}}'}


SQRT_K = r'(\d*)(?:\\sqrt\{(\d+)\})?'
ANGLE = r'\\frac\{(\d*)\\pi\}\{(\d+)\}'


def _sqrt_k(n: str, r: str | None) -> tuple[int, int | None]:
    return (int(n) if n else 1), (int(r) if r else None)


def _tex_k(n: int, r: int | None) -> str:
    return (str(n) if n != 1 or r is None else '') + (f'\\sqrt{{{r}}}' if r else '')


def _angle(num: int, den: int) -> str:
    return f'\\frac{{{num if num != 1 else ""}\\pi}}{{{den}}}'


def _cos_value(num: int, den: int) -> sp.Expr:
    return sp.nsimplify(sp.cos(sp.pi * num / den))


class DoubleAngleCos(ExprTemplate):
    """K cos²t − K sin²t,  K − 2K sin²t,  2K cos²t − K  = K cos 2t"""
    topic, code = 'Тригонометрические выражения', '7.trig.cos2t'
    family = (r'(?P<a>' + SQRT_K + r')\\cos\^2' + ANGLE + r'-(?P<b>' + SQRT_K + r')\\sin\^2' + ANGLE
              + r'|(?P<c>' + SQRT_K + r')-(?P<d>' + SQRT_K + r')\\sin\^2' + ANGLE
              + r'|(?P<e>' + SQRT_K + r')\\cos\^2' + ANGLE + r'-(?P<f>' + SQRT_K + r')')

    def parse_expr(self, f):
        g = [x for x in f.groups()]
        expr = f.group(0)
        nums = re.findall(r'(\d*)(?:\\sqrt\{(\d+)\})?\\(cos|sin)\^2\\frac\{(\d*)\\pi\}\{(\d+)\}', expr)
        angles = {(int(n or 1), int(d)) for *_, n, d in nums}
        if len(angles) != 1:
            return None
        (an, ad), = angles
        coefs = re.findall(r'(?:^|-)(\d*)(?:\\sqrt\{(\d+)\})?', expr)
        if f.group('a') is not None:
            kind = 'cos2-sin2'
            k1 = _sqrt_k(*re.match(SQRT_K, f.group('a')).groups())
            k2 = _sqrt_k(*re.match(SQRT_K, f.group('b')).groups())
            if k1 != k2:
                return None
            k = k1
        elif f.group('c') is not None:
            kind = 'one-2sin2'
            k = _sqrt_k(*re.match(SQRT_K, f.group('c')).groups())
            k2 = _sqrt_k(*re.match(SQRT_K, f.group('d')).groups())
            if (2 * k[0], k[1]) != k2:
                return None
        else:
            kind = '2cos2-one'
            k2 = _sqrt_k(*re.match(SQRT_K, f.group('e')).groups())
            k = _sqrt_k(*re.match(SQRT_K, f.group('f')).groups())
            if (2 * k[0], k[1]) != k2:
                return None
        return {'kind': kind, 'k': k, 'an': an, 'ad': ad}

    def explain(self, p):
        n, r = p['k']
        k = _tex_k(n, r)
        t = _angle(p['an'], p['ad'])
        t2 = _angle(*_reduce(2 * p['an'], p['ad']))
        formula = {
            'cos2-sin2': f'{k}(\\cos^2 t-\\sin^2 t)={k}\\cos 2t',
            'one-2sin2': f'{k}(1-2\\sin^2 t)={k}\\cos 2t',
            '2cos2-one': f'{k}(2\\cos^2 t-1)={k}\\cos 2t',
        }[p['kind']]
        cos2 = _cos_value(2 * p['an'], p['ad'])
        value = sp.nsimplify(sp.sympify(n) * (sp.sqrt(r) if r else 1) * cos2)
        return (
            f'Вынесем общий множитель и применим формулу косинуса двойного угла: $${formula}.$$\n\n'
            f'При $t={t}$ получаем $2t={t2}$, $\\cos {t2}={sp.latex(cos2)}$, поэтому значение выражения равно '
            f'$${k}\\cdot\\left({sp.latex(cos2)}\\right)={sp.latex(value)}.$$'
        ).replace('\\cdot\\left(', '\\cdot\\left(') if k else ''

    def sample(self, rng):
        # 2t даёт табличный косинус: ±1/2, ±√2/2, ±√3/2
        den = rng.choice([8, 12, 12, 8, 6])
        options = {8: (2, [1, 3, 5, 7, 9, 11, 13, 15]), 12: (3, [1, 5, 7, 11, 13, 17, 19, 23]), 6: (1, [1, 2, 4, 5, 7, 8])}
        r, nums = options[den]
        if den == 6:
            r = None
        an = rng.choice(nums)
        n = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 24])
        kind = rng.choice(['cos2-sin2', 'one-2sin2', '2cos2-one'])
        k = (n, r)
        t = _angle(an, den)
        kt, k2t = _tex_k(n, r), _tex_k(2 * n, r)
        expr = {
            'cos2-sin2': f'{kt}\\cos^2{t}-{kt}\\sin^2{t}',
            'one-2sin2': f'{kt}-{k2t}\\sin^2{t}',
            '2cos2-one': f'{k2t}\\cos^2{t}-{kt}',
        }[kind]
        return {'kind': kind, 'k': k, 'an': an, 'ad': den, 'expr': expr}

    def nice(self, x):
        return frac(x).denominator in (1, 2) and x != 0


def _reduce(num: int, den: int) -> tuple[int, int]:
    g = math.gcd(num, den)
    return num // g, den // g


class SinCosProduct(ExprTemplate):
    """K sin t · cos t = K/2 · sin 2t"""
    topic, code = 'Тригонометрические выражения', '7.trig.sincos'
    family = SQRT_K + r'\\sin' + ANGLE + r'·\\cos' + ANGLE

    def parse_expr(self, f):
        n, r = _sqrt_k(f.group(1), f.group(2))
        a1, d1, a2, d2 = int(f.group(3) or 1), int(f.group(4)), int(f.group(5) or 1), int(f.group(6))
        if (a1, d1) != (a2, d2):
            return None
        return {'k': (n, r), 'an': a1, 'ad': d1}

    def explain(self, p):
        n, r = p['k']
        k = _tex_k(n, r)
        t = _angle(p['an'], p['ad'])
        t2 = _angle(*_reduce(2 * p['an'], p['ad']))
        s2 = sp.nsimplify(sp.sin(sp.pi * 2 * p['an'] / p['ad']))
        value = sp.nsimplify(sp.Rational(n, 2) * (sp.sqrt(r) if r else 1) * s2)
        half = f'\\frac{{{k}}}{{2}}' if k else '\\frac{1}{2}'
        return (
            f'По формуле синуса двойного угла $\\sin t\\cos t=\\frac{{1}}{{2}}\\sin 2t$:\n\n'
            f'$${k}\\sin {t}\\cdot\\cos {t}={half}\\sin {t2}={half}\\cdot\\left({sp.latex(s2)}\\right)={sp.latex(value)}.$$'
        )

    def sample(self, rng):
        den = rng.choice([8, 12, 8])
        r = 2 if den == 8 else 3
        nums = [1, 3, 5, 7, 9, 11, 13, 15] if den == 8 else [1, 5, 7, 11, 13, 17, 19, 23]
        an = rng.choice(nums)
        if den == 12:
            r = rng.choice([None, None, 3])
        n = rng.choice([2, 4, 6, 8, 10, 12, 16, 20, 24, 28, 36])
        t = _angle(an, den)
        return {'k': (n, r), 'an': an, 'ad': den, 'expr': f'{_tex_k(n, r)}\\sin {t}\\cdot\\cos {t}'}

    def nice(self, x):
        return frac(x).denominator in (1, 2) and x != 0


class TableTrig(ExprTemplate):
    """Табличные значения: 18√2 tg(π/4) sin(π/4)"""
    topic, code = 'Тригонометрические выражения', '7.trig.table'
    family = SQRT_K + r'\\(tg|sin|cos)' + ANGLE + r'\\(tg|sin|cos)' + ANGLE

    VALUES = {'sin': sp.sin, 'cos': sp.cos, 'tg': sp.tan}

    def parse_expr(self, f):
        n, r = _sqrt_k(f.group(1), f.group(2))
        return {'k': (n, r), 'parts': [(f.group(3), int(f.group(4) or 1), int(f.group(5))),
                                       (f.group(6), int(f.group(7) or 1), int(f.group(8)))]}

    def explain(self, p):
        n, r = p['k']
        k = _tex_k(n, r)
        subs = []
        for fn, an, ad in p['parts']:
            v = sp.nsimplify(self.VALUES[fn](sp.pi * an / ad))
            subs.append((f'{_fn(fn)} {_angle(an, ad)}', sp.latex(v)))
        listing = ', '.join(f'${a}={b}$' for a, b in subs)
        return (f'Табличные значения: {listing}. Тогда\n\n'
                f'$${k}\\cdot {subs[0][1]}\\cdot {subs[1][1]}={tex_num(self.solve(p))}.$$')

    def sample(self, rng):
        combos = [('tg', 1, 4, 'sin', 1, 4, 2), ('tg', 1, 3, 'cos', 1, 6, 3), ('tg', 1, 6, 'sin', 1, 3, None),
                  ('tg', 1, 4, 'cos', 1, 4, 2), ('sin', 1, 4, 'cos', 1, 4, None), ('tg', 1, 3, 'sin', 1, 3, None),
                  ('tg', 1, 6, 'cos', 1, 6, None), ('sin', 1, 3, 'cos', 1, 6, None)]
        f1, a1, d1, f2, a2, d2, r = rng.choice(combos)
        n = rng.choice([2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 30])
        expr = f'{_tex_k(n, r)}{_fn(f1)} {_angle(a1, d1)}{_fn(f2)} {_angle(a2, d2)}'
        return {'k': (n, r), 'parts': [(f1, a1, d1), (f2, a2, d2)], 'expr': expr}


class Cos2AlphaGiven(Template):
    """K cos 2α, если sin α = s (или cos α = c)"""
    number, topic, code = 7, 'Тригонометрические выражения', '7.trig.cos2a-given'
    patterns = [ASK + r' \$(\d*)\\cos2\\(?:text\{α\}|alpha|α)(?:\\text)?\$, если \$\\(sin|cos)\\(?:text\{α\}|alpha|α)(?:\\text)?=(-?\d+(?:\{,\}\d+)?)\$']

    def parse(self, m, task):
        from app.bankgen.core import num
        return {'k': _k(m.group(1)), 'f': m.group(2), 'v': num(m.group(3))}

    def solve(self, p):
        v2 = p['v'] ** 2
        return p['k'] * (1 - 2 * v2 if p['f'] == 'sin' else 2 * v2 - 1)

    def verify(self, p, a):
        alpha = math.asin(float(p['v'])) if p['f'] == 'sin' else math.acos(float(p['v']))
        return math.isclose(p['k'] * math.cos(2 * alpha), float(a), abs_tol=1e-9)

    def render(self, p):
        k, f, v = p['k'], p['f'], p['v']
        kt = str(k) if k != 1 else ''
        a = self.solve(p)
        if f == 'sin':
            formula = f'\\cos 2\\alpha=1-2\\sin^2\\alpha=1-2\\cdot {par(v)}^2={tex_num(1 - 2 * v * v)}'
        else:
            formula = f'\\cos 2\\alpha=2\\cos^2\\alpha-1=2\\cdot {par(v)}^2-1={tex_num(2 * v * v - 1)}'
        sol = (f'Выразим косинус двойного угла через $\\{f}\\alpha$: $${formula}.$$\n\n'
               + (f'Тогда ${kt}\\cos 2\\alpha={k}\\cdot {par(a / k)}={tex_num(a)}$.\n\n' if k != 1 else '')
               + f'**Ответ:** {dec(a)}.')
        return Rendered(f'{ASK} ${kt}\\cos 2\\alpha$, если $\\{f}\\alpha={tex_num(v)}$.', sol)

    def sample(self, rng):
        v = Fraction(rng.choice([1, 2, 3, 4, 6, 7, 8, 9]), 10) * rng.choice([1, -1])
        return {'k': rng.choice([2, 3, 4, 5, 6, 8, 10, 25, 50]), 'f': rng.choice(['sin', 'cos']), 'v': v}


class TgFromCos(Template):
    """tg α, если cos α = ±a√b/b и α в четверти"""
    number, topic, code, difficulty = 7, 'Тригонометрические выражения', '7.trig.tg-from-cos', 2
    patterns = [r'(?:выражения )?\$\\tg\\(?:text\{α\}|alpha|α)(?:\\text)?\$, если \$\\cos\\(?:text\{α\}|alpha|α)(?:\\text)?=(-?)\\frac\{(\d*)\\sqrt\{(\d+)\}\}\{(\d+)\}\$ и \$\\(?:text\{α\}|alpha|α)\\in\((.+?)\)\$']

    def parse(self, m, task):
        sign = -1 if m.group(1) else 1
        a, b, d = _k(m.group(2)), int(m.group(3)), int(m.group(4))
        interval = m.group(5)
        quarter = {'0;\\frac{\\pi}{2}': 1, '\\frac{\\pi}{2};\\pi': 2, '\\pi;\\frac{3\\pi}{2}': 3,
                   '\\frac{3\\pi}{2};2\\pi': 4}.get(interval)
        if quarter is None:
            return None
        return {'sign': sign, 'a': a, 'b': b, 'd': d, 'q': quarter}

    def _cos(self, p):
        return p['sign'] * p['a'] * math.sqrt(p['b']) / p['d']

    def solve(self, p):
        c2 = Fraction(p['a'] ** 2 * p['b'], p['d'] ** 2)
        t2 = (1 - c2) / c2
        t = Fraction(math.isqrt(t2.numerator), math.isqrt(t2.denominator))
        if t * t != t2:
            raise ValueError('тангенс не рациональный')
        return t if p['q'] in (1, 3) else -t

    def verify(self, p, a):
        c = self._cos(p)
        s = math.sqrt(1 - c * c) * (1 if p['q'] in (1, 2) else -1)
        return math.isclose(s / c, float(a), abs_tol=1e-9)

    def render(self, p):
        a = self.solve(p)
        cos_tex = f'{"-" if p["sign"] < 0 else ""}\\frac{{{p["a"] if p["a"] != 1 else ""}\\sqrt{{{p["b"]}}}}}{{{p["d"]}}}'
        c2 = Fraction(p['a'] ** 2 * p['b'], p['d'] ** 2)
        interval = {1: '0;\\frac{\\pi}{2}', 2: '\\frac{\\pi}{2};\\pi', 3: '\\pi;\\frac{3\\pi}{2}', 4: '\\frac{3\\pi}{2};2\\pi'}[p['q']]
        sign_word = 'положителен' if a > 0 else 'отрицателен'
        sol = (
            f'Воспользуемся тождеством $1+\\operatorname{{tg}}^2\\alpha=\\frac{{1}}{{\\cos^2\\alpha}}$. '
            f'Здесь $\\cos^2\\alpha={tex_frac(c2)}$, поэтому $$\\operatorname{{tg}}^2\\alpha=\\frac{{1}}{{\\cos^2\\alpha}}-1='
            f'{tex_frac(1 / c2)}-1={tex_frac(1 / c2 - 1)}.$$\n\n'
            f'На промежутке $({interval})$ тангенс {sign_word}, значит $\\operatorname{{tg}}\\alpha={tex_num(a)}$.\n\n'
            f'**Ответ:** {dec(a)}.'
        )
        return Rendered(f'Найдите $\\operatorname{{tg}}\\alpha$, если $\\cos\\alpha={cos_tex}$ и $\\alpha\\in({interval})$.', sol)

    def sample(self, rng):
        # cos = 1/√(1+t²): t = m (целое), cos = √(1+m²)/(1+m²) · k/k
        t = rng.choice([2, 3, 4, 5, 6, 7, Fraction(1, 2), Fraction(1, 3), Fraction(3, 4), Fraction(4, 3)])
        t = Fraction(t)
        # cos² = 1/(1+t²) = q²/(q²+p²) при t = p/q
        pp, q = t.numerator, t.denominator
        n = pp * pp + q * q
        root = math.isqrt(n)
        quarter = rng.choice([1, 2, 3, 4])
        sign = 1 if quarter in (1, 4) else -1
        if root * root == n:  # cos рациональный — не наш прототип
            return None
        return {'sign': sign, 'a': q, 'b': n, 'd': n, 'q': quarter}


# ---------------------------------------------------------------------------
# Логарифмы
# ---------------------------------------------------------------------------

LOGB = r'(?:(\d)|\{([\d{},]+)\})'
LOGARG = r'(\d+(?:\{,\}\d+)?|\\frac\{\d+\}\{\d+\})'


def _logbase(a, b) -> str:
    return (a or b).replace('{,}', ',')


def _num_tex(s: str) -> Fraction:
    from app.bankgen.core import num
    m = re.fullmatch(r'\\frac\{(\d+)\}\{(\d+)\}', s)
    return Fraction(int(m.group(1)), int(m.group(2))) if m else num(s)


class LogSumDiff(ExprTemplate):
    """log_a b ± log_a c"""
    topic, code = 'Логарифмические выражения', '7.log.sum'
    family = r'\\log_' + LOGB + LOGARG + r'([+-])\\log_' + LOGB + LOGARG

    def parse_expr(self, f):
        a1, b, op, a2, c = _logbase(f.group(1), f.group(2)), f.group(3), f.group(4), _logbase(f.group(5), f.group(6)), f.group(7)
        if a1 != a2:
            return None
        return {'a': _num_tex(a1.replace(',', '{,}')), 'b': _num_tex(b), 'op': op, 'c': _num_tex(c)}

    def explain(self, p):
        a, b, c = p['a'], p['b'], p['c']
        inner = b * c if p['op'] == '+' else b / c
        rule = 'Сумма логарифмов с одинаковым основанием равна логарифму произведения' if p['op'] == '+' \
            else 'Разность логарифмов с одинаковым основанием равна логарифму частного'
        joined = f'{tex_num(b)}\\cdot {tex_num(c)}' if p['op'] == '+' else f'\\frac{{{tex_num(b)}}}{{{tex_num(c)}}}'
        val = self.solve(p)
        return (f'{rule}:\n\n$$\\log_{{{tex_num(a)}}}\\left({joined}\\right)=\\log_{{{tex_num(a)}}}{tex_num(inner)}={tex_num(val)},$$'
                f'\n\nтак как ${par(a)}^{{{tex_num(val)}}}={tex_num(inner)}$.')

    def sample(self, rng):
        a = Fraction(rng.choice([2, 3, 4, 5, 6, 7, 2, 3, 5]))
        if rng.random() < 0.15:
            a = Fraction(rng.choice([2, 3, 4, 6, 7]), 10)
        e = rng.choice([1, 2, 3, 4, 5, -1, -2]) if a > 1 else rng.choice([-1, -2, 1, 2])
        target = a ** e
        if target.denominator != 1 and a > 1:
            return None
        op = rng.choice(['+', '-'])
        if op == '-':
            c = Fraction(rng.choice([2, 3, 5, 6, 7, 11, 13, 17]))
            b = target * c
        else:
            c = Fraction(rng.choice([2, 4, 5, 8, 10, 20, 25, 50]))
            b = target / c
            if b.denominator not in (1, 2, 5, 10) or b == 1:
                return None
        if b == c or b <= 0 or not (b.denominator in (1, 2, 5, 10)) or b > 2000:
            return None
        at = tex_num(a)
        base = at if len(at) == 1 else '{' + at + '}'
        expr = f'\\log_{base}{tex_num(b)}{op}\\log_{base}{tex_num(c)}'
        return {'a': a, 'b': b, 'op': op, 'c': c, 'expr': expr.replace('_{', '_{').replace(f'\\log_{base}', f'\\log_{{{at}}}')}


class LogRootBase(ExprTemplate):
    """K·log_{ⁿ√a} a = Kn,  K·log_a ⁿ√a = K/n"""
    topic, code = 'Логарифмические выражения', '7.log.root'
    family = r'(\d*)\\log_(?:\{\\sqrt\[(\d+)\]\{(\d+)\}\}(\d+)|(\d)\\sqrt\[(\d+)\]\{(\d+)\})'

    def parse_expr(self, f):
        k = _k(f.group(1))
        if f.group(2):
            n, a, b = int(f.group(2)), int(f.group(3)), int(f.group(4))
            return {'k': k, 'n': n, 'a': a, 'kind': 'base'} if a == b else None
        a, n, b = int(f.group(5)), int(f.group(6)), int(f.group(7))
        return {'k': k, 'n': n, 'a': a, 'kind': 'arg'} if a == b else None

    def explain(self, p):
        k, n, a = p['k'], p['n'], p['a']
        if p['kind'] == 'base':
            return (f'Так как $\\sqrt[{n}]{{{a}}}={a}^{{\\frac{{1}}{{{n}}}}}$, то '
                    f'$\\log_{{\\sqrt[{n}]{{{a}}}}}{a}=\\log_{{{a}^{{1/{n}}}}}{a}={n}\\log_{{{a}}}{a}={n}$. '
                    f'Значит, значение выражения равно ${k}\\cdot {n}={k * n}$.')
        val = Fraction(k, n)
        return (f'Так как $\\sqrt[{n}]{{{a}}}={a}^{{\\frac{{1}}{{{n}}}}}$, то '
                f'$\\log_{{{a}}}\\sqrt[{n}]{{{a}}}=\\frac{{1}}{{{n}}}$. '
                f'Значит, значение выражения равно ${k}\\cdot\\frac{{1}}{{{n}}}={tex_num(val)}$.')

    def sample(self, rng):
        a = rng.choice([2, 3, 5, 6, 7, 11, 13])
        n = rng.choice([2, 3, 4, 5, 6, 8])
        kind = rng.choice(['base', 'arg'])
        if kind == 'base':
            k = rng.randint(2, 9)
            expr = f'{k}\\log_{{\\sqrt[{n}]{{{a}}}}}{a}'
        else:
            k = n * rng.randint(1, 6) if rng.random() < 0.7 else rng.randint(2, 12)
            expr = f'{k}\\log_{{{a}}}\\sqrt[{n}]{{{a}}}'
        return {'k': k, 'n': n, 'a': a, 'kind': kind, 'expr': expr}


class LogRatio(ExprTemplate):
    """log_a b / log_a c,  log_a b / log_{a^k} b,  log_a b/log_a c + log_c d"""
    topic, code = 'Логарифмические выражения', '7.log.ratio'
    family = r'\\frac\{\\log_' + LOGB + r'(\d+)\}\{\\log_' + LOGB + r'(\d+)\}(?:\+\\log_' + LOGB + LOGARG + r')?'

    def parse_expr(self, f):
        a1, b, a2, c = int(_logbase(f.group(1), f.group(2))), int(f.group(3)), int(_logbase(f.group(4), f.group(5))), int(f.group(6))
        extra = None
        if f.group(9):
            extra = (int(_logbase(f.group(7), f.group(8))), _num_tex(f.group(9)))
        if a1 == a2:
            return {'kind': 'same-base', 'a': a1, 'b': b, 'c': c, 'extra': extra}
        if b == c:
            return {'kind': 'same-arg', 'a': a1, 'a2': a2, 'b': b, 'extra': None}
        return None

    def explain(self, p):
        if p['kind'] == 'same-arg':
            a, a2, b = p['a'], p['a2'], p['b']
            k = round(math.log(a2, a))
            return (f'Так как ${a2}={a}^{{{k}}}$, то $\\log_{{{a2}}}{b}=\\frac{{1}}{{{k}}}\\log_{{{a}}}{b}$, и дробь равна '
                    f'$$\\frac{{\\log_{{{a}}}{b}}}{{\\frac{{1}}{{{k}}}\\log_{{{a}}}{b}}}={k}.$$')
        a, b, c = p['a'], p['b'], p['c']
        text = (f'По формуле перехода к новому основанию $\\frac{{\\log_{{{a}}}{b}}}{{\\log_{{{a}}}{c}}}=\\log_{{{c}}}{b}$.')
        if p['extra']:
            d = p['extra'][1]
            total = b * d
            text += (f' Тогда $$\\log_{{{c}}}{b}+\\log_{{{c}}}{tex_num(d)}=\\log_{{{c}}}\\left({b}\\cdot {tex_num(d)}\\right)'
                     f'=\\log_{{{c}}}{tex_num(total)}={tex_num(self.solve(p))}.$$')
        else:
            text += f' Так как ${c}^{{{tex_num(self.solve(p))}}}={b}$, получаем ${tex_num(self.solve(p))}$.'
        return text

    def sample(self, rng):
        kind = rng.choice(['same-base', 'same-arg', 'extra'])
        a = rng.choice([2, 3, 5, 6, 7, 9, 11])
        if kind == 'same-arg':
            base = rng.choice([2, 3, 5, 6, 7])
            k = rng.choice([2, 3])
            a2 = base ** k
            b = rng.choice([x for x in [5, 7, 11, 13, 17, 19, 23, 29] if x != base])
            return {'kind': kind, 'a': base, 'a2': a2, 'b': b, 'extra': None,
                    'expr': f'\\frac{{\\log_{{{base}}}{b}}}{{\\log_{{{a2}}}{b}}}'}
        c = rng.choice([2, 3, 5, 7])
        e = rng.choice([2, 3, 4, 5])
        if kind == 'same-base':
            b = c ** e
            if b > 1000 or a == c:
                return None
            return {'kind': kind, 'a': a, 'b': b, 'c': c, 'extra': None,
                    'expr': f'\\frac{{\\log_{{{a}}}{b}}}{{\\log_{{{a}}}{c}}}'}
        # log_c b + log_c d, где b·d = c^e
        b = c * rng.choice([2, 3, 4, 5, 6])
        d = Fraction(c ** e, b)
        if a == c or d.denominator == 1 or b > 200:
            return None
        return {'kind': 'same-base', 'a': a, 'b': b, 'c': c, 'extra': (c, d),
                'expr': f'\\frac{{\\log_{{{a}}}{b}}}{{\\log_{{{a}}}{c}}}+\\log_{{{c}}}{tex_frac(d)}'}


# ---------------------------------------------------------------------------
# Степени и корни
# ---------------------------------------------------------------------------

def _factor(n: int) -> dict[int, int]:
    out, p = {}, 2
    while p * p <= n:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
        p += 1
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


class PowerMonomial(ExprTemplate):
    """
    Произведения и частные степеней и корней: 14^{6,4}·7^{-5,4}/2^{4,4}, (4^{15})^5:4^{73},
    ∛36·⁵√36/³⁰√36. Решение: разложить основания на простые множители и сложить показатели.
    """
    topic, code = 'Степени и корни', '7.pow.monomial'
    family = r'[\d{}^,()\\frac\[\]sqrt·:\-]+'

    TERM = re.compile(r'\(?(\d+)\^\{?(-?\d+(?:\{,\}\d+)?|\\frac\{?\d+\}?\{?\d+\}?)\}?\)?(?:\^\{?(\d+)\}?\)?)?|\\sqrt\[(\d+)\]\{(\d+)\}|\\sqrt\{(\d+)\}')

    def parse_expr(self, f):
        expr = f.group(0)
        if '\\sqrt' not in expr and '^' not in expr:
            return None
        if re.search(r'\\sqrt\{\d+\}·\\sqrt|\\sqrt\{(\d+)\}-', expr):
            return None
        try:
            value = exact(expr.replace(':', '/'))
        except Exception:  # noqa: BLE001
            return None
        return {'value': value}

    def solve(self, p):
        return exact(p['expr'].replace(':', '/')) if 'expr' in p else p['value']

    def verify(self, p, answer):
        return equals(p['expr'].replace(':', '/'), answer)

    def explain(self, p):
        expr = p['expr'].replace(':', '/')
        e = to_sympy(expr)
        # разложение на простые: sympy powsimp с разложенными основаниями
        primes: dict[int, sp.Rational] = {}
        for base, exp in _collect(e):
            for q, m in _factor(int(base)).items():
                primes[q] = primes.get(q, 0) + exp * m
        parts = '\\cdot '.join(f'{q}^{{{sp.latex(sp.nsimplify(v))}}}' for q, v in sorted(primes.items()) if v != 0)
        return (f'Запишем все множители как степени простых чисел и сложим показатели при одинаковых основаниях:\n\n'
                f'$${p["expr"]}={parts}={tex_num(self.solve(p))}.$$')

    def sample(self, rng):
        kind = rng.choice(['decimal', 'decimal', 'nested', 'roots', 'roots-diff'])
        if kind == 'decimal':
            p1, p2 = rng.sample([2, 3, 5, 7], 2)
            e1, e2 = rng.choice([1, 2]), rng.choice([1, 2])
            frac_part = Fraction(rng.randint(1, 9), 10)
            x = rng.randint(2, 7) + frac_part
            # (p1·p2)^x · p2^{e2-x} / p1^{x-e1} = p1^{e1}·p2^{e2}
            num_ = p1 * p2
            expr = f'\\frac{{{num_}^{{{dec(x, True)}}}\\cdot {p2}^{{{dec(e2 - x, True)}}}}}{{{p1}^{{{dec(x - e1, True)}}}}}'
            return {'expr': expr}
        if kind == 'nested':
            b = rng.choice([2, 3, 4, 5, 7])
            m, n = rng.randint(2, 9), rng.randint(2, 9)
            d = rng.choice([1, 2, 3])
            if b ** d > 300:
                return None
            expr = f'\\left({b}^{{{m}}}\\right)^{{{n}}}:{b}^{{{m * n - d}}}'
            return {'expr': expr}
        if kind == 'roots':
            a = rng.choice([4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 8, 27, 125])
            n1, n2 = rng.sample([3, 4, 5, 6, 7], 2)
            # 1/n1 + 1/n2 - 1/n3 = 1/k, где a^{1/k} — целое
            for k in (2, 3):
                inv = Fraction(1, n1) + Fraction(1, n2) - Fraction(1, k)
                if inv > 0 and inv.numerator == 1 and inv.denominator <= 60:
                    root = round(a ** (1 / k))
                    if root ** k == a:
                        n3 = inv.denominator
                        return {'expr': f'\\frac{{\\sqrt[{n1}]{{{a}}}\\cdot\\sqrt[{n2}]{{{a}}}}}{{\\sqrt[{n3}]{{{a}}}}}'}
            return None
        # ⁿ√a·ⁿ√b/ⁿ√c, где ab/c = rⁿ
        n = rng.choice([3, 4])
        r = rng.choice([2, 3, 5]) if n == 3 else rng.choice([2, 3])
        c = rng.choice([2, 3, 5, 6, 10, 12, 15, 24])
        a = rng.choice([2, 3, 4, 5, 6, 8, 9, 10, 12, 16, 25])
        b = Fraction(r ** n * c, a)
        if b.denominator != 1 or b in (a, c) or b > 1000 or b < 2:
            return None
        return {'expr': f'\\frac{{\\sqrt[{n}]{{{a}}}\\cdot\\sqrt[{n}]{{{b}}}}}{{\\sqrt[{n}]{{{c}}}}}'}


def _collect(e: sp.Expr) -> list[tuple[int, sp.Rational]]:
    """Произведение степеней → [(основание, показатель)]"""
    out = []
    for factor in sp.Mul.make_args(e):
        b, x = factor.as_base_exp()
        if isinstance(b, sp.Pow):
            b2, x2 = b.as_base_exp()
            b, x = b2, x * x2
        if b.is_Integer:
            out.append((int(b), sp.nsimplify(x)))
        elif b.is_Rational:
            out.append((int(b.p), sp.nsimplify(x)))
            out.append((int(b.q), -sp.nsimplify(x)))
        else:
            raise ValueError(f'не степень числа: {factor}')
    return out


class RootArithmetic(ExprTemplate):
    """(k√m)²/n,  (√a − √b)·√c"""
    topic, code = 'Степени и корни', '7.pow.sqrt'
    family = r'\\frac\{\(?(\d*)\\sqrt\{(\d+)\}\)\^2\}\{?(\d+)\}?|\(\\sqrt\{(\d+)\}([+-])\\sqrt\{(\d+)\}\)·\\sqrt\{(\d+)\}'

    def parse_expr(self, f):
        if f.group(2):
            return {'kind': 'square', 'k': _k(f.group(1)), 'm': int(f.group(2)), 'n': int(f.group(3))}
        return {'kind': 'dist', 'a': int(f.group(4)), 'op': f.group(5), 'b': int(f.group(6)), 'c': int(f.group(7))}

    def explain(self, p):
        if p['kind'] == 'square':
            k, m, n = p['k'], p['m'], p['n']
            return (f'$$\\frac{{({k if k != 1 else ""}\\sqrt{{{m}}})^2}}{{{n}}}=\\frac{{{k}^2\\cdot {m}}}{{{n}}}'
                    f'=\\frac{{{k * k * m}}}{{{n}}}={tex_num(Fraction(k * k * m, n))}.$$')
        a, b, c, op = p['a'], p['b'], p['c'], p['op']
        ra, rb = math.isqrt(a * c), math.isqrt(b * c)
        return (f'Раскроем скобки: $$\\sqrt{{{a}}}\\cdot\\sqrt{{{c}}}{op}\\sqrt{{{b}}}\\cdot\\sqrt{{{c}}}'
                f'=\\sqrt{{{a * c}}}{op}\\sqrt{{{b * c}}}={ra}{op}{rb}={tex_num(self.solve(p))}.$$')

    def sample(self, rng):
        if rng.random() < 0.5:
            k = rng.randint(2, 9)
            m = rng.choice([2, 3, 5, 6, 7, 8, 10, 11])
            n = rng.choice([d for d in range(2, 30) if (k * k * m) % d == 0 and d not in (k, m)] or [1])
            if n == 1:
                return None
            return {'kind': 'square', 'k': k, 'm': m, 'n': n,
                    'expr': f'\\frac{{({k}\\sqrt{{{m}}})^2}}{{{n}}}'}
        c = rng.choice([2, 3, 5, 6, 7, 10])
        x, y = rng.sample(range(1, 13), 2)
        a, b = c * x * x, c * y * y
        op = rng.choice(['+', '-'])
        if op == '-' and a < b:
            a, b = b, a
        return {'kind': 'dist', 'a': a, 'op': op, 'b': b, 'c': c,
                'expr': f'(\\sqrt{{{a}}}{op}\\sqrt{{{b}}})\\cdot\\sqrt{{{c}}}'}


TEMPLATES = [
    SinCosOverSinDouble(), SinDoubleOverProduct(), DoubleAngleCos(), SinCosProduct(), TableTrig(),
    Cos2AlphaGiven(), TgFromCos(), LogSumDiff(), LogRootBase(), LogRatio(), RootArithmetic(), PowerMonomial(),
]
EXTRA = []


def _fn(name: str) -> str:
    """tg и ctg в KaTeX — только через \\operatorname"""
    return f'\\operatorname{{{name}}}' if name in ('tg', 'ctg') else f'\\{name}'
