"""№ 2. Векторы"""
import math
import random
import re
from fractions import Fraction

from app.bankgen.core import Rendered, Template, dec, isqrt_exact, par, tex_num
from app.bankgen.figures import Figure

VEC = r'\\overrightarrow\{(\w)\}'
COORDS = r'\((-?\d+);(-?\d+)\)'


def _v(name: str) -> str:
    return f'\\overrightarrow{{{name}}}'


def _combo(k: int, m: int) -> str:
    """k·a + m·b в LaTeX"""
    def term(c, name, first):
        if c == 0:
            return ''
        sign = '-' if c < 0 else ('' if first else '+')
        return sign + (str(abs(c)) if abs(c) != 1 else '') + _v(name)
    s = term(k, 'a', True)
    return s + term(m, 'b', not s)


def _parse_combo(s: str) -> tuple[int, int]:
    """'\\overrightarrow{a}-4\\overrightarrow{b}' → (1, -4)"""
    k = {'a': 0, 'b': 0}
    for sign, c, name in re.findall(r'([+-]?)(\d*)\\overrightarrow\{([ab])\}', s):
        k[name] += (-1 if sign == '-' else 1) * (int(c) if c else 1)
    return k['a'], k['b']


class VectorTemplate(Template):
    number = 2
    topic = 'Векторы на плоскости'

    def render(self, p):
        cond, sol, fig = self.build(p)
        figures = {}
        if fig is not None:
            cond += '\n\n![](figure://fig)'
            figures['fig'] = fig.svg()
        return Rendered(cond, sol + f'\n\n**Ответ:** {dec(self.solve(p))}.', figures)

    def given(self, p) -> str:
        a, b = p['a'], p['b']
        return f'Даны векторы ${_v("a")}({a[0]};{a[1]})$ и ${_v("b")}({b[0]};{b[1]})$.'


class DotProduct(VectorTemplate):
    code = '2.dot'
    patterns = [r'Даны векторы \$' + VEC + COORDS + r'\$ и \$' + VEC + COORDS + r'\$\. Найдите скалярное произведение \$\\overrightarrow\{a\}·\\overrightarrow\{b\}\$']

    def parse(self, m, task):
        return {'a': (int(m.group(2)), int(m.group(3))), 'b': (int(m.group(5)), int(m.group(6)))}

    def solve(self, p):
        return p['a'][0] * p['b'][0] + p['a'][1] * p['b'][1]

    def build(self, p):
        a, b = p['a'], p['b']
        cond = self.given(p) + f' Найдите скалярное произведение ${_v("a")}\\cdot {_v("b")}$.'
        sol = (f'Скалярное произведение равно сумме произведений соответствующих координат: '
               f'$${_v("a")}\\cdot {_v("b")}={par(a[0])}\\cdot {par(b[0])}+{par(a[1])}\\cdot {par(b[1])}={self.solve(p)}.$$')
        return cond, sol, None

    def sample(self, rng):
        return {'a': (rng.randint(-15, 15), rng.randint(-15, 15)), 'b': (rng.randint(-15, 15), rng.randint(-15, 15))}


class ComboLength(VectorTemplate):
    code = '2.length'
    patterns = [r'Даны векторы \$' + VEC + COORDS + r'\$ и \$' + VEC + COORDS + r'\$\. Найдите длину вектора \$([^$]+)\$']

    def parse(self, m, task):
        k, n = _parse_combo(m.group(7))
        return {'a': (int(m.group(2)), int(m.group(3))), 'b': (int(m.group(5)), int(m.group(6))), 'k': k, 'm': n}

    def _c(self, p):
        return (p['k'] * p['a'][0] + p['m'] * p['b'][0], p['k'] * p['a'][1] + p['m'] * p['b'][1])

    def solve(self, p):
        c = self._c(p)
        r = isqrt_exact(c[0] ** 2 + c[1] ** 2)
        if r is None:
            raise ValueError('длина иррациональная')
        return r

    def verify(self, p, a):
        c = self._c(p)
        return math.isclose(math.hypot(*c), a)

    def build(self, p):
        c = self._c(p)
        expr = _combo(p['k'], p['m'])
        cond = self.given(p) + f' Найдите длину вектора ${expr}$.'
        sol = (f'Найдём координаты вектора $\\vec c={expr}$: '
               f'$$\\vec c\\,({p["k"]}\\cdot {par(p["a"][0])}{"+" if p["m"] >= 0 else "-"}{abs(p["m"])}\\cdot {par(p["b"][0])};\\ '
               f'{p["k"]}\\cdot {par(p["a"][1])}{"+" if p["m"] >= 0 else "-"}{abs(p["m"])}\\cdot {par(p["b"][1])})=\\vec c\\,({c[0]};{c[1]}).$$\n\n'
               f'Длина: $|\\vec c|=\\sqrt{{{par(c[0])}^2+{par(c[1])}^2}}=\\sqrt{{{c[0] ** 2 + c[1] ** 2}}}={self.solve(p)}$.')
        return cond, sol, None

    def sample(self, rng):
        a = (rng.randint(-6, 8), rng.randint(-6, 8))
        b = (rng.randint(-6, 8), rng.randint(-6, 8))
        k, m = rng.choice([1, 2, 3, 4, 5, 6, 7, 8]), rng.choice([1, 2, 3, 4, -1, -2, -3, -4, 5, -5])
        if a == (0, 0) or b == (0, 0):
            return None
        p = {'a': a, 'b': b, 'k': k, 'm': m}
        c = self._c(p)
        if c == (0, 0) or 0 in c and abs(sum(c)) < 3:
            return None
        return p


class ComboDot(VectorTemplate):
    code = '2.combo-dot'
    patterns = [r'Даны векторы \$' + VEC + COORDS + r'\$ и \$' + VEC + COORDS + r'\$\. Найдите скалярное произведение векторов \$([^$]+)\$ и \$([^$]+)\$']

    def parse(self, m, task):
        return {'a': (int(m.group(2)), int(m.group(3))), 'b': (int(m.group(5)), int(m.group(6))),
                'u': _parse_combo(m.group(7)), 'w': _parse_combo(m.group(8))}

    def _vec(self, p, k):
        return (k[0] * p['a'][0] + k[1] * p['b'][0], k[0] * p['a'][1] + k[1] * p['b'][1])

    def solve(self, p):
        u, w = self._vec(p, p['u']), self._vec(p, p['w'])
        return u[0] * w[0] + u[1] * w[1]

    def build(self, p):
        u, w = self._vec(p, p['u']), self._vec(p, p['w'])
        eu, ew = _combo(*p['u']), _combo(*p['w'])
        cond = self.given(p) + f' Найдите скалярное произведение векторов ${eu}$ и ${ew}$.'
        sol = (f'Координаты векторов: ${eu}=({u[0]};{u[1]})$, ${ew}=({w[0]};{w[1]})$.\n\n'
               f'Скалярное произведение: $${par(u[0])}\\cdot {par(w[0])}+{par(u[1])}\\cdot {par(w[1])}={self.solve(p)}.$$')
        return cond, sol, None

    def sample(self, rng):
        a = (rng.randint(-5, 6), rng.randint(-5, 6))
        b = (rng.randint(-5, 6), rng.randint(-5, 6))
        return {'a': a, 'b': b, 'u': (1, rng.choice([1, -1, 2])), 'w': (rng.choice([2, 3, 5, 7]), rng.choice([-1, 1, -2]))}


class DotByAngle(VectorTemplate):
    code = '2.dot-angle'
    patterns = [r'Длины векторов \$' + VEC + r'\$ и \$' + VEC + r'\$ равны (\d+) и (\d+), а угол между ними равен \$(\d+)\^\\circ\$']

    COS = {60: Fraction(1, 2), 120: Fraction(-1, 2), 90: Fraction(0), 0: Fraction(1), 180: Fraction(-1)}

    def parse(self, m, task):
        return {'la': int(m.group(3)), 'lb': int(m.group(4)), 'phi': int(m.group(5))}

    def solve(self, p):
        return p['la'] * p['lb'] * self.COS[p['phi']]

    def build(self, p):
        cond = (f'Длины векторов ${_v("a")}$ и ${_v("b")}$ равны {p["la"]} и {p["lb"]}, а угол между ними равен '
                f'${p["phi"]}^\\circ$. Найдите скалярное произведение ${_v("a")}\\cdot {_v("b")}$.')
        sol = (f'По определению $${_v("a")}\\cdot {_v("b")}=|{_v("a")}|\\cdot|{_v("b")}|\\cdot\\cos\\varphi='
               f'{p["la"]}\\cdot {p["lb"]}\\cdot\\cos {p["phi"]}^\\circ={p["la"]}\\cdot {p["lb"]}\\cdot {par(self.COS[p["phi"]])}'
               f'={tex_num(self.solve(p))}.$$')
        return cond, sol, None

    def sample(self, rng):
        return {'la': rng.randint(2, 12), 'lb': rng.randint(2, 12), 'phi': rng.choice([60, 120, 60])}


class GridVectors(VectorTemplate):
    """Векторы на клетчатой плоскости: координаты по рисунку"""
    code = '2.grid'
    patterns = []  # оригиналы ФИПИ — рисунком, их координаты переписаны вручную (manual.json)

    def solve(self, p):
        a, b = p['a'], p['b']
        if p['ask'] == 'dot':
            return a[0] * b[0] + a[1] * b[1]
        c = (a[0] + p['m'] * b[0], a[1] + p['m'] * b[1])
        r = isqrt_exact(c[0] ** 2 + c[1] ** 2)
        if r is None:
            raise ValueError('длина иррациональная')
        return r

    def build(self, p):
        a, b = p['a'], p['b']
        head = (f'На координатной плоскости изображены векторы ${_v("a")}$ и ${_v("b")}$, координатами которых являются '
                f'целые числа.')
        coords = (f'По рисунку (считаем клетки от начала до конца каждого вектора): '
                  f'${_v("a")}({a[0]};{a[1]})$, ${_v("b")}({b[0]};{b[1]})$.\n\n')
        if p['ask'] == 'dot':
            cond = head + f' Найдите скалярное произведение ${_v("a")}\\cdot {_v("b")}$.'
            sol = coords + f'$${_v("a")}\\cdot {_v("b")}={par(a[0])}\\cdot {par(b[0])}+{par(a[1])}\\cdot {par(b[1])}={self.solve(p)}.$$'
        else:
            m = p['m']
            expr = _combo(1, m)
            c = (a[0] + m * b[0], a[1] + m * b[1])
            cond = head + f' Найдите длину вектора ${expr}$.'
            sol = coords + (f'${expr}=({c[0]};{c[1]})$, его длина $\\sqrt{{{par(c[0])}^2+{par(c[1])}^2}}='
                            f'\\sqrt{{{c[0] ** 2 + c[1] ** 2}}}={self.solve(p)}$.')
        fig = Figure(width=300, height=300, pad=14)
        if 'start_a' in p:
            sa, sb = p['start_a'], p['start_b']
        else:  # оригинал ФИПИ: координаты сняты с рисунка, векторы ставим рядом, не пересекая
            sa = (0, 0)
            sb = (max(0, a[0]) + 1 - min(0, b[0]), 0)
        ea, eb = (sa[0] + a[0], sa[1] + a[1]), (sb[0] + b[0], sb[1] + b[1])
        xs = [sa[0], sb[0], ea[0], eb[0]]
        ys = [sa[1], sb[1], ea[1], eb[1]]
        fig.grid(min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1)
        fig.arrow(sa, ea, '<tspan>a</tspan>')
        fig.arrow(sb, eb, '<tspan>b</tspan>')
        return cond, sol, fig

    def sample(self, rng):
        a = (rng.randint(-5, 6), rng.randint(-5, 6))
        b = (rng.randint(-5, 6), rng.randint(-5, 6))
        if 0 in a and 0 in b or a == (0, 0) or b == (0, 0):
            return None
        ask = rng.choice(['dot', 'length'])
        # векторы рядом, но не пересекаются: b начинается правее самой правой точки a
        start_a = (-min(0, a[0]), -min(0, a[1]) + rng.randint(0, 2))
        start_b = (start_a[0] + max(0, a[0]) + 2 - min(0, b[0]), -min(0, b[1]) + rng.randint(0, 2))
        p = {'a': a, 'b': b, 'ask': ask, 'm': rng.choice([1, 2, 3, -1, -2]), 'start_a': start_a, 'start_b': start_b}
        return p


TEMPLATES = [DotProduct(), ComboDot(), ComboLength(), DotByAngle()]
EXTRA = [(GridVectors(), 16)]
