"""№ 6. Простейшие уравнения"""
import math
import random
import re
from fractions import Fraction

from app.bankgen.core import (
    NUM, Rendered, Template, close, dec, frac, isqrt_exact, lin, lin_parse, linear_steps, num, par, poly, signed,
    tex_frac, tex_num,
)

ASK = 'Найдите корень уравнения'
LOG_BASE = r'(?:(\d)|\{(\d+)\})'


def _prime_power(x: Fraction) -> tuple[int, Fraction] | None:
    """x = g^e с наименьшим натуральным g > 1 (e целое). 1/49 → (7, -2), 9 → (3, 2), 36 → (6, 2)"""
    if x <= 0 or x == 1:
        return None
    n, d = x.numerator, x.denominator
    if n != 1 and d != 1:
        return None
    m = n if d == 1 else d
    sign = 1 if d == 1 else -1
    for g in range(2, m + 1):
        e, r = 0, m
        while r % g == 0:
            r //= g
            e += 1
        if r == 1:
            return g, Fraction(sign * e)
    return None


def _tex_base(a: Fraction) -> str:
    return f'\\left({tex_frac(a)}\\right)' if a.denominator != 1 else str(a.numerator)


def _parse_value(s: str) -> Fraction:
    m = re.fullmatch(r'\\frac\{(\d+)\}\{(\d+)\}', s)
    if m:
        return Fraction(int(m.group(1)), int(m.group(2)))
    return num(s)


# ---------------------------------------------------------------------------

class ExpEq(Template):
    """a^{kx+b} = c  или  a^{kx+b} = d^{mx+n}"""
    number, topic, code = 6, 'Показательные уравнения', '6.exp'
    patterns = [
        ASK + r' \$(\(\\frac\{\d+\}\{\d+\}\)|\d+)\^\{?([^{}=]+?)\}?=(\(\\frac\{\d+\}\{\d+\}\)|\\frac\{\d+\}\{\d+\}|-?\d+)(?:\^\{?([^{}$]+?)\}?)?\$',
    ]

    def parse(self, m, task):
        a = _parse_value(m.group(1).strip('()'))
        k1, b1 = lin_parse(m.group(2))
        c = _parse_value(m.group(3).strip('()'))
        k2, b2 = lin_parse(m.group(4)) if m.group(4) else (Fraction(0), Fraction(1))
        return {'a': a, 'k1': k1, 'b1': b1, 'c': c, 'k2': k2, 'b2': b2}

    @staticmethod
    def _sides(p):
        pa, pc = _prime_power(p['a']), _prime_power(p['c'])
        if not pa or not pc or pa[0] != pc[0]:
            raise ValueError('разные основания')
        return pa[0], pa[1], pc[1]

    def solve(self, p):
        base, ea, ec = self._sides(p)
        # ea·(k1x+b1) = ec·(k2x+b2)
        k = ea * p['k1'] - ec * p['k2']
        if k == 0:
            raise ValueError('нет единственного корня')
        return (ec * p['b2'] - ea * p['b1']) / k

    def verify(self, p, x):
        left = float(p['a']) ** float(p['k1'] * x + p['b1'])
        right = float(p['c']) ** float(p['k2'] * x + p['b2'])
        return close(left, right, 1e-9)

    @staticmethod
    def _check_value(p, x) -> str:
        e = p['k1'] * x + p['b1']
        if e.denominator != 1:
            raise ValueError('дробный показатель')
        return tex_num(p['a'] ** int(e))

    def _rhs(self, p) -> str:
        if p['k2'] == 0 and p['b2'] == 1:
            return tex_frac(p['c'])
        return f'{_tex_base(p["c"])}^{{{lin(p["k2"], p["b2"])}}}'

    def render(self, p):
        base, ea, ec = self._sides(p)
        x = self.solve(p)
        eq = f'{_tex_base(p["a"])}^{{{lin(p["k1"], p["b1"])}}}={self._rhs(p)}'
        left = f'{base}^{{{_mul(ea, p["k1"], p["b1"])}}}'
        if p['k2'] == 0 and p['b2'] == 1:
            right = f'{base}^{{{tex_num(ec)}}}'
            linear = f'{_mul(ea, p["k1"], p["b1"], bare=True)}={tex_num(ec)}'
        else:
            right = f'{base}^{{{_mul(ec, p["k2"], p["b2"])}}}'
            linear = f'{_mul(ea, p["k1"], p["b1"], bare=True)}={_mul(ec, p["k2"], p["b2"], bare=True)}'
        solution = (
            f'Приведём обе части к основанию ${base}$: '
            f'$${left}={right}.$$\n\n'
            f'Степени с одинаковым основанием равны, когда равны показатели: '
            f'$${linear},$$ откуда $x={tex_num(x)}$.\n\n'
            f'Проверка: при $x={tex_num(x)}$ показатель слева равен ${tex_num(p["k1"] * x + p["b1"])}$, '
            f'${_tex_base(p["a"])}^{{{tex_num(p["k1"] * x + p["b1"])}}}={self._check_value(p, x)}$ — верно.\n\n'
            f'**Ответ:** {dec(x)}.'
        )
        return Rendered(f'{ASK} ${eq}$.', solution)

    def sample(self, rng):
        prime = rng.choice([2, 3, 5, 6, 7])
        sa = rng.choice([1, 1, 2, -1]) if prime in (2, 3) else rng.choice([1, -1])
        a = Fraction(prime) ** sa
        if a.denominator == 1 and a.numerator > 49:
            return None
        k1 = rng.choice([1, 1, -1])
        b1 = rng.randint(-12, 12)
        x = rng.randint(-10, 15)
        if rng.random() < 0.25:
            k2 = rng.choice([1, 2])
            b2 = rng.randint(-5, 5)
            sc = rng.choice([1, 2, -1]) if prime in (2, 3) else 1
            c = Fraction(prime) ** sc
            # подбираем b1 так, чтобы корень был целым
            b1 = Fraction(sc * (k2 * x + b2) - sa * k1 * x, sa)
            if b1.denominator != 1 or abs(b1) > 15 or sc * k2 == sa * k1:
                return None
            return {'a': a, 'k1': Fraction(k1), 'b1': b1, 'c': c, 'k2': Fraction(k2), 'b2': Fraction(b2)}
        e = sa * (k1 * x + b1)
        if e == 0 or abs(e) > 4 or prime ** abs(e) > 625:
            return None
        return {'a': a, 'k1': Fraction(k1), 'b1': Fraction(b1), 'c': Fraction(prime) ** e,
                'k2': Fraction(0), 'b2': Fraction(1)}

    def nice(self, x):
        return frac(x).denominator == 1


def _mul(e: Fraction, k, b, bare: bool = False) -> str:
    """e·(kx+b) как показатель: при e = 1 — просто kx+b, иначе со скобкой"""
    inner = lin(k, b)
    if e == 1:
        return inner
    if e == -1:
        return f'-({inner})'
    return f'{tex_num(e)}({inner})'


class RootEq(Template):
    """√(kx+b) = c,  ∛(kx+b) = c"""
    number, topic, code = 6, 'Иррациональные уравнения', '6.root'
    patterns = [ASK + r' \$\\sqrt(?:\[(\d)\])?\{([^{}]+)\}=(' + NUM + r')\$']

    def parse(self, m, task):
        k, b = lin_parse(m.group(2))
        return {'n': int(m.group(1) or 2), 'k': k, 'b': b, 'c': num(m.group(3))}

    def solve(self, p):
        if p['n'] % 2 == 0 and p['c'] < 0:
            raise ValueError('корень не может быть отрицательным')
        return (p['c'] ** p['n'] - p['b']) / p['k']

    def verify(self, p, x):
        v = p['k'] * x + p['b']
        return v == p['c'] ** p['n'] and (p['n'] % 2 or v >= 0)

    def render(self, p):
        x = self.solve(p)
        root = '\\sqrt' + (f'[{p["n"]}]' if p['n'] != 2 else '') + '{' + lin(p['k'], p['b']) + '}'
        power = 'квадрат' if p['n'] == 2 else 'куб'
        rhs = tex_num(p['c'] ** p['n'])
        note = '' if p['n'] % 2 else '\n\nПравая часть исходного уравнения положительна, поэтому посторонних корней возведение в квадрат не дало.'
        solution = (
            f'Возведём обе части в {power}: {linear_steps(p["k"], p["b"], p["c"] ** p["n"])}'
            f'{note}\n\n**Ответ:** {dec(x)}.'
        )
        return Rendered(f'{ASK} ${root}={tex_num(p["c"])}$.', solution)

    def sample(self, rng):
        n = rng.choice([2, 2, 2, 3])
        k = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, -1, -2, -3, -4, -5, -7])
        c = rng.randint(1, 10) if n == 2 else rng.randint(-5, 5)
        x = Fraction(rng.randint(-15, 25), rng.choice([1, 1, 1, 2]))
        b = c ** n - k * x
        if b.denominator != 1 or abs(b) > 120 or b == 0:
            return None
        return {'n': n, 'k': Fraction(k), 'b': b, 'c': Fraction(c)}


class LogEq(Template):
    """log_a(kx+b) = log_a c  или  log_a(kx+b) = c"""
    number, topic, code = 6, 'Логарифмические уравнения', '6.log'
    patterns = [ASK + r' \$\\log_' + LOG_BASE + r'\(([^()]+)\)=(?:\\log_' + LOG_BASE + r'(\d+)|(' + NUM + r'))\$']

    def parse(self, m, task):
        a = int(m.group(1) or m.group(2))
        k, b = lin_parse(m.group(3))
        if m.group(6):
            base2 = int(m.group(4) or m.group(5))
            if base2 != a:
                return None
            return {'a': a, 'k': k, 'b': b, 'same': True, 'c': num(m.group(6))}
        return {'a': a, 'k': k, 'b': b, 'same': False, 'c': num(m.group(7))}

    def _value(self, p) -> Fraction:
        return p['c'] if p['same'] else Fraction(p['a']) ** p['c']

    def solve(self, p):
        return (self._value(p) - p['b']) / p['k']

    def verify(self, p, x):
        v = p['k'] * x + p['b']
        if v <= 0:
            return False
        lhs = math.log(float(v), p['a'])
        rhs = math.log(float(p['c']), p['a']) if p['same'] else float(p['c'])
        return close(lhs, rhs)

    def render(self, p):
        x = self.solve(p)
        a, arg = p['a'], lin(p['k'], p['b'])
        value = self._value(p)
        if p['same']:
            eq = f'\\log_{{{a}}}({arg})=\\log_{{{a}}}{tex_num(p["c"])}'
            step = 'Логарифмы по одному основанию равны, когда равны их аргументы:'
        else:
            eq = f'\\log_{{{a}}}({arg})={tex_num(p["c"])}'
            step = f'По определению логарифма ${arg}={a}^{{{tex_num(p["c"])}}}$, то есть'
        solution = (
            f'{step} {linear_steps(p["k"], p["b"], value)}\n\n'
            f'Проверка: при $x={tex_num(x)}$ аргумент логарифма равен ${tex_num(value)}>0$.\n\n'
            f'**Ответ:** {dec(x)}.'
        )
        return Rendered(f'{ASK} ${eq}$.', solution)

    def sample(self, rng):
        a = rng.choice([2, 3, 4, 5, 6, 7, 8, 9])
        k = rng.choice([1, 1, -1, 2, -2, 3])
        same = rng.random() < 0.5
        x = rng.randint(-20, 30)
        if same:
            c = Fraction(rng.randint(2, 25))
            value = c
        else:
            c = Fraction(rng.choice([1, 2, 2, 3, -1]))
            value = Fraction(a) ** c
            if value > 250:
                return None
        b = value - k * x
        if b == 0 or abs(b) > 80:
            return None
        return {'a': a, 'k': Fraction(k), 'b': b, 'same': same, 'c': c}

    def nice(self, x):
        return frac(x).denominator in (1, 2)


class CubeEq(Template):
    """(x+b)^3 = c"""
    number, topic, code = 6, 'Степенные и рациональные уравнения', '6.cube'
    patterns = [ASK + r' \$\(([^()]+)\)\^3=(' + NUM + r')\$']

    def parse(self, m, task):
        k, b = lin_parse(m.group(1))
        return {'k': k, 'b': b, 'c': num(m.group(2))}

    @staticmethod
    def _cbrt(c: Fraction) -> Fraction:
        r = round(abs(float(c)) ** (1 / 3))
        r = Fraction(r if c >= 0 else -r)
        if r ** 3 != c:
            raise ValueError('не куб')
        return r

    def solve(self, p):
        return (self._cbrt(p['c']) - p['b']) / p['k']

    def verify(self, p, x):
        return (p['k'] * x + p['b']) ** 3 == p['c']

    def render(self, p):
        x, r = self.solve(p), self._cbrt(p['c'])
        solution = (
            f'Кубический корень извлекается из любого числа единственным образом: '
            f'$${lin(p["k"], p["b"])}=\\sqrt[3]{{{tex_num(p["c"])}}}={tex_num(r)},$$ откуда $x={tex_num(x)}$.\n\n'
            f'**Ответ:** {dec(x)}.'
        )
        return Rendered(f'{ASK} $({lin(p["k"], p["b"])})^3={tex_num(p["c"])}$.', solution)

    def sample(self, rng):
        r = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])
        x = rng.randint(-12, 12)
        b = rng.randint(-12, 12)
        if b == 0 or x + b != r:
            b = r - x
        if b == 0:
            return None
        return {'k': Fraction(1), 'b': Fraction(b), 'c': Fraction(r) ** 3}


class ReciprocalEq(Template):
    """1/(kx+b) = c"""
    number, topic, code = 6, 'Степенные и рациональные уравнения', '6.recip'
    patterns = [ASK + r' \$\\frac\{(\d+)\}\{([^{}]+)\}=(' + NUM + r')\$']

    def parse(self, m, task):
        k, b = lin_parse(m.group(2))
        return {'n': num(m.group(1)), 'k': k, 'b': b, 'c': num(m.group(3))}

    def solve(self, p):
        return (p['n'] / p['c'] - p['b']) / p['k']

    def verify(self, p, x):
        d = p['k'] * x + p['b']
        return d != 0 and p['n'] / d == p['c']

    def render(self, p):
        x = self.solve(p)
        value = p['n'] / p['c']
        solution = (
            f'Знаменатель не равен нулю, поэтому ${lin(p["k"], p["b"])}=\\frac{{{tex_num(p["n"])}}}{{{tex_num(p["c"])}}}$: '
            f'{linear_steps(p["k"], p["b"], value)}\n\n**Ответ:** {dec(x)}.'
        )
        return Rendered(f'{ASK} $\\frac{{{tex_num(p["n"])}}}{{{lin(p["k"], p["b"])}}}={tex_num(p["c"])}$.', solution)

    def sample(self, rng):
        n = rng.choice([1, 1, 1, 2, 3])
        c = Fraction(rng.choice([1, 2, 4, 5, 8, 10, -2, -4]))
        k = rng.choice([1, 2, 3, 4, 5, -2])
        b = rng.randint(-12, 12)
        if b == 0:
            return None
        return {'n': Fraction(n), 'k': Fraction(k), 'b': Fraction(b), 'c': c}


# ---------------------------------------------------------------------------
# Прототипы, которых нет в открытом банке ФИПИ (встречаются в банках подготовки).
# Формулировки и решения наши, числа подбираются генератором.
# ---------------------------------------------------------------------------

class QuadraticEq(Template):
    """x² + px + q = 0, в ответ — меньший или больший корень"""
    number, topic, code = 6, 'Квадратные уравнения', '6.quad'

    def solve(self, p):
        return min(p['roots']) if p['which'] == 'меньший' else max(p['roots'])

    def verify(self, p, x):
        a, b, c = p['coefs']
        return a * x * x + b * x + c == 0

    def render(self, p):
        a, b, c = p['coefs']
        x1, x2 = sorted(p['roots'])
        d = b * b - 4 * a * c
        sq = isqrt_exact(int(d)) if d.denominator == 1 else None
        solution = (
            f'Дискриминант: $D={par(b)}^2-4\\cdot {par(a)}\\cdot {par(c)}={tex_num(d)}$'.replace('-4\\cdot 1\\cdot', '-4\\cdot')
            + (f', $\\sqrt{{D}}={sq}$.' if sq is not None else '.')
            + f'\n\n$$x_{{1,2}}=\\frac{{{tex_num(-b)}\\pm {sq}}}{{{tex_num(2 * a)}}},\\quad x_1={tex_num(x1)},\\ x_2={tex_num(x2)}.$$\n\n'
            f'В ответ записываем {p["which"]} корень.\n\n**Ответ:** {dec(self.solve(p))}.'
        )
        cond = (f'Решите уравнение ${poly(p["coefs"])}=0$. Если уравнение имеет более одного корня, '
                f'в ответе запишите {p["which"]} из корней.')
        return Rendered(cond, solution)

    def sample(self, rng):
        x1, x2 = rng.sample(range(-12, 13), 2)
        a = rng.choice([1, 1, 1, 2, 3, -1])
        coefs = [Fraction(a), Fraction(-a * (x1 + x2)), Fraction(a * x1 * x2)]
        if coefs[2] == 0 or coefs[1] == 0:
            return None
        return {'coefs': coefs, 'roots': [Fraction(x1), Fraction(x2)], 'which': rng.choice(['меньший', 'больший'])}


class SqrtEqualsX(Template):
    """√(ax+b) = x: два кандидата, посторонний отбрасываем"""
    number, topic, code, difficulty = 6, 'Иррациональные уравнения', '6.sqrt-x', 2

    def solve(self, p):
        return p['root']

    def verify(self, p, x):
        v = p['a'] * x + p['b']
        return x >= 0 and v >= 0 and isqrt_exact(int(v)) == x

    def render(self, p):
        a, b, r, s = p['a'], p['b'], p['root'], p['other']
        solution = (
            f'Правая часть должна быть неотрицательной: $x\\ge 0$. Возведём в квадрат: '
            f'$${lin(a, b)}=x^2,\\qquad {poly([1, -a, -b])}=0.$$\n\n'
            f'По теореме Виета корни $x={tex_num(r)}$ и $x={tex_num(s)}$. '
            f'Условию $x\\ge 0$ удовлетворяет только $x={tex_num(r)}$.\n\n**Ответ:** {dec(r)}.'
        )
        return Rendered(f'{ASK} $\\sqrt{{{lin(a, b)}}}=x$.', solution)

    def sample(self, rng):
        r = rng.randint(2, 12)
        s = -rng.randint(1, 9)
        # x² - (r+s)x + rs = 0  ⇔  x² = (r+s)x - rs
        a, b = Fraction(r + s), Fraction(-r * s)
        if a == 0:
            return None
        return {'a': a, 'b': b, 'root': Fraction(r), 'other': Fraction(s)}


class LogTwoSides(Template):
    """log_a(kx+b) = log_a(mx+n): равенство аргументов и проверка ОДЗ"""
    number, topic, code, difficulty = 6, 'Логарифмические уравнения', '6.log-two', 2

    def solve(self, p):
        return (p['n'] - p['b']) / (p['k'] - p['m'])

    def verify(self, p, x):
        return p['k'] * x + p['b'] > 0 and p['m'] * x + p['n'] > 0

    def render(self, p):
        x = self.solve(p)
        left, right = lin(p['k'], p['b']), lin(p['m'], p['n'])
        value = p['k'] * x + p['b']
        solution = (
            f'Приравняем аргументы: $${left}={right},$$ откуда $x={tex_num(x)}$.\n\n'
            f'Проверка ОДЗ: при $x={tex_num(x)}$ оба аргумента равны ${tex_num(value)}>0$.\n\n**Ответ:** {dec(x)}.'
        )
        return Rendered(f'{ASK} $\\log_{{{p["a"]}}}({left})=\\log_{{{p["a"]}}}({right})$.', solution)

    def sample(self, rng):
        a = rng.choice([2, 3, 5, 7, 0.5])
        if a == 0.5:
            a = '\\frac{1}{2}'
        x = rng.randint(-8, 15)
        k, m = rng.sample([1, 2, 3, 4, 5, -1, -2], 2)
        value = rng.randint(1, 30)
        b, n = value - k * x, value - m * x
        if b == 0 or n == 0:
            return None
        return {'a': a, 'k': Fraction(k), 'b': Fraction(b), 'm': Fraction(m), 'n': Fraction(n)}


class RationalEq(Template):
    """c/(x+a) = d/(x+b)"""
    number, topic, code = 6, 'Степенные и рациональные уравнения', '6.rational'

    def solve(self, p):
        # c(x+b) = d(x+a) → (c-d)x = da - cb
        return (p['d'] * p['a'] - p['c'] * p['b']) / (p['c'] - p['d'])

    def verify(self, p, x):
        return x + p['a'] != 0 and x + p['b'] != 0 and p['c'] / (x + p['a']) == p['d'] / (x + p['b'])

    def render(self, p):
        x = self.solve(p)
        c, d, a, b = (tex_num(p[k]) for k in 'cdab')
        solution = (
            f'При $x\\ne {tex_num(-p["a"])}$ и $x\\ne {tex_num(-p["b"])}$ воспользуемся основным свойством пропорции: '
            f'$${c}({lin(1, p["b"])})={d}({lin(1, p["a"])}),\\quad '
            f'{lin(p["c"] - p["d"], 0)}={tex_num(p["d"] * p["a"] - p["c"] * p["b"])},\\quad x={tex_num(x)}.$$ '
            f'Знаменатели при этом не обращаются в ноль.\n\n**Ответ:** {dec(x)}.'
        )
        return Rendered(f'{ASK} $\\frac{{{c}}}{{{lin(1, p["a"])}}}=\\frac{{{d}}}{{{lin(1, p["b"])}}}$.', solution)

    def sample(self, rng):
        c, d = rng.sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 13], 2)
        a, b = rng.sample(range(-12, 13), 2)
        if a == 0 or b == 0:
            return None
        return {'c': Fraction(c), 'd': Fraction(d), 'a': Fraction(a), 'b': Fraction(b)}

    def nice(self, x):
        return frac(x).denominator in (1, 2, 4, 5)


TEMPLATES = [ExpEq(), RootEq(), LogEq(), CubeEq(), ReciprocalEq()]
EXTRA = [(QuadraticEq(), 12), (SqrtEqualsX(), 8), (LogTwoSides(), 8), (RationalEq(), 8)]
