"""
№ 11. Графики функций: по точкам сетки восстановить формулу и найти значение или абсциссу точки пересечения.

Параметры — точки с целыми координатами, через которые проходят графики (для оригиналов ФИПИ сняты с рисунка
вручную, data/fipi/manual.json, и проверены ответом ФИПИ). Аналоги рисуем сами по тем же точкам.
"""
import math
import random
from fractions import Fraction

import sympy as sp

from app.bankgen.core import Rendered, Template, dec, frac, lin, nice_number, par, poly, tex_frac, tex_num
from app.bankgen.figures import Figure, axes, sample_curve

F = Fraction


def _pt(p) -> str:
    return f'({tex_num(F(p[0]))};{tex_num(F(p[1]))})'


class Graphs(Template):
    number, topic, code = 11, 'Графики функций', '11.graph'

    def match(self, task):
        return None  # оригиналы — через manual.json

    # --- восстановление формул по точкам
    @staticmethod
    def _line(p, q):
        k = F(q[1] - p[1], q[0] - p[0])
        return k, F(p[1]) - k * p[0]

    @staticmethod
    def _parabola(p, q, r):
        a, b, c = sp.symbols('a b c')
        sol = sp.solve([a * x ** 2 + b * x + c - y for x, y in (p, q, r)], [a, b, c])
        return tuple(F(int(sp.Rational(sol[v]).p), int(sp.Rational(sol[v]).q)) for v in (a, b, c))

    def _func(self, p):
        """(формула-описание, функция Fraction → значение) по параметрам"""
        k = p['kind']
        P = p['pts']
        if k == 'log':
            (x0, y0), = P
            a = sp.nsimplify(sp.Integer(x0) ** sp.Rational(1, y0))
            return a, lambda x: F(sp.Rational(sp.nsimplify(sp.log(x, a))))
        if k == 'exp':
            (x0, y0), = P
            a = sp.nsimplify(sp.Rational(*F(y0).as_integer_ratio()) ** sp.Rational(1, x0))
            return a, lambda x: F(sp.Rational(sp.nsimplify(a ** x)))
        if k == 'hyper':
            (x0, y0), = P
            kk = F(x0) * y0
            return kk, lambda x: kk / x
        if k == 'sqrt':
            (x0, y0), = P
            a = F(y0) / F(math.isqrt(x0))
            return a, lambda x: a * F(math.isqrt(int(x)))
        if k == 'line':
            kk, b = self._line(*P)
            return (kk, b), lambda x: kk * x + b
        if k == 'parabola':
            a, b, c = self._parabola(*P)
            return (a, b, c), lambda x: a * x * x + b * x + c
        raise ValueError(k)

    def solve(self, p):
        k = p['kind']
        if k in ('log', 'exp', 'hyper', 'sqrt', 'line', 'parabola'):
            _, f = self._func(p)
            return f(F(p['at']))
        if k == 'two-lines':
            k1, b1 = self._line(*p['pts'][:2])
            k2, b2 = self._line(*p['pts'][2:])
            return (b2 - b1) / (k1 - k2)
        if k == 'hyper-line':
            kk = F(p['pts'][0][0]) * p['pts'][0][1]
            m, b = self._line(*p['pts'][1:3])
            # kk/x = mx + b → m x² + b x − kk = 0; один корень — абсцисса A
            xA = F(p['A'])
            other = -b / m - xA
            return other
        if k == 'parab-line':
            a, b, c = self._parabola(*p['pts'][:3])
            m = F(p['pts'][3][1], p['pts'][3][0])
            # ax² + (b − m)x + c = 0, сумма корней −(b − m)/a
            return -(b - m) / a - F(p['A'])
        if k == 'sqrt-line':
            (x0, y0), (x1, y1) = p['pts']
            a = F(y0) / F(math.isqrt(x0))
            m = F(y1, x1)
            # a√x = m x → √x = a/m
            return (a / m) ** 2
        raise ValueError(k)

    def verify(self, p, ans):
        return ans is not None

    def nice(self, x):
        return nice_number(x, 2) and abs(x) < 1000

    # --- текст
    def render(self, p):
        k = p['kind']
        ans = self.solve(p)
        P = p['pts']
        if k == 'log':
            a, _ = self._func(p)
            cond = f'На рисунке изображён график функции вида $f(x)=\\log_a x$. Найдите значение $f({p["at"]})$.'
            sol = (f'График проходит через точку ${_pt(P[0])}$: $\\log_a {P[0][0]}={P[0][1]}$, откуда $a={sp.latex(a)}$. '
                   f'$$f({p["at"]})=\\log_{{{sp.latex(a)}}} {p["at"]}={tex_num(ans)}.$$')
        elif k == 'exp':
            a, _ = self._func(p)
            cond = f'На рисунке изображён график функции вида $f(x)=a^x$. Найдите значение $f({p["at"]})$.'
            sol = (f'График проходит через точку ${_pt(P[0])}$: $a^{{{P[0][0]}}}={tex_num(F(P[0][1]))}$, откуда $a={sp.latex(a)}$. '
                   f'$$f({p["at"]})=\\left({sp.latex(a)}\\right)^{{{p["at"]}}}={tex_num(ans)}.$$')
        elif k == 'hyper':
            kk, _ = self._func(p)
            cond = f'На рисунке изображён график функции вида $f(x)=\\frac{{k}}{{x}}$. Найдите значение $f({p["at"]})$.'
            sol = (f'График проходит через точку ${_pt(P[0])}$: $k={P[0][0]}\\cdot {par(P[0][1])}={tex_num(kk)}$. '
                   f'$$f({p["at"]})=\\frac{{{tex_num(kk)}}}{{{p["at"]}}}={tex_num(ans)}.$$')
        elif k == 'sqrt':
            a, _ = self._func(p)
            cond = f'На рисунке изображён график функции вида $f(x)=a\\sqrt{{x}}$. Найдите значение $f({p["at"]})$.'
            sol = (f'График проходит через точку ${_pt(P[0])}$: $a\\sqrt{{{P[0][0]}}}={P[0][1]}$, откуда $a={tex_num(a)}$. '
                   f'$$f({p["at"]})={tex_num(a)}\\cdot\\sqrt{{{p["at"]}}}={tex_num(ans)}.$$')
        elif k == 'line':
            (kk, b), _ = self._func(p)
            cond = f'На рисунке изображён график функции вида $f(x)=kx+b$. Найдите значение $f({p["at"]})$.'
            sol = (f'График проходит через точки ${_pt(P[0])}$ и ${_pt(P[1])}$: $k=\\frac{{{P[1][1]}-{par(P[0][1])}}}{{{P[1][0]}-{par(P[0][0])}}}={tex_num(kk)}$, '
                   f'$b={tex_num(b)}$, то есть $f(x)={lin(kk, b)}$. $$f({p["at"]})={tex_num(ans)}.$$')
        elif k == 'parabola':
            (a, b, c), _ = self._func(p)
            cond = f'На рисунке изображён график функции вида $f(x)=ax^2+bx+c$. Найдите значение $f({p["at"]})$.'
            sol = (f'График проходит через точки {", ".join(f"${_pt(q)}$" for q in P)}. Подставив их в $f(x)=ax^2+bx+c$, получим систему, '
                   f'откуда $a={tex_num(a)}$, $b={tex_num(b)}$, $c={tex_num(c)}$: $f(x)={poly([a, b, c])}$. $$f({p["at"]})={tex_num(ans)}.$$')
        elif k == 'two-lines':
            k1, b1 = self._line(*P[:2])
            k2, b2 = self._line(*P[2:])
            cond = 'На рисунке изображены графики двух линейных функций, пересекающиеся в точке $A$. Найдите абсциссу точки $A$.'
            sol = (f'Первая прямая проходит через ${_pt(P[0])}$ и ${_pt(P[1])}$: $y={lin(k1, b1)}$. Вторая — через ${_pt(P[2])}$ и ${_pt(P[3])}$: '
                   f'$y={lin(k2, b2)}$. $${lin(k1, b1)}={lin(k2, b2)}\\ \\Rightarrow\\ x={tex_num(ans)}.$$')
        elif k == 'hyper-line':
            kk = F(P[0][0]) * P[0][1]
            m, b = self._line(*P[1:3])
            cond = ('На рисунке изображены графики функций видов $f(x)=\\frac{k}{x}$ и $g(x)=ax+b$, пересекающиеся в точках $A$ и $B$. '
                    'Найдите абсциссу точки $B$.')
            sol = (f'Гипербола проходит через ${_pt(P[0])}$: $k={tex_num(kk)}$. Прямая — через ${_pt(P[1])}$ и ${_pt(P[2])}$: $g(x)={lin(m, b)}$. '
                   f'$$\\frac{{{tex_num(kk)}}}{{x}}={lin(m, b)}\\ \\Rightarrow\\ {poly([m, b, -kk])}=0.$$ Один корень — абсцисса точки $A$, $x={p["A"]}$; '
                   f'по теореме Виета второй корень $x={tex_num(ans)}$.')
        elif k == 'parab-line':
            a, b, c = self._parabola(*P[:3])
            m = F(P[3][1], P[3][0])
            cond = ('На рисунке изображены графики функций $f(x)=ax^2+bx+c$ и $g(x)=kx$, пересекающиеся в точках $A$ и $B$. '
                    'Найдите абсциссу точки $B$.')
            sol = (f'Парабола проходит через {", ".join(f"${_pt(q)}$" for q in P[:3])}: $f(x)={poly([a, b, c])}$. Прямая $g(x)=kx$ проходит через '
                   f'${_pt(P[3])}$: $k={tex_num(m)}$. $${poly([a, b, c])}={lin(m, 0)}\\ \\Rightarrow\\ {poly([a, b - m, c])}=0.$$ '
                   f'Один корень — абсцисса $A$, $x={p["A"]}$; второй (по теореме Виета) $x={tex_num(ans)}$.')
        else:  # sqrt-line
            (x0, y0), (x1, y1) = P
            a = F(y0) / F(math.isqrt(x0))
            m = F(y1, x1)
            cond = ('На рисунке изображены графики функций видов $f(x)=a\\sqrt{x}$ и $g(x)=kx$, пересекающиеся в точках $A$ и $B$. '
                    'Найдите абсциссу точки $B$.')
            sol = (f'$f$ проходит через ${_pt(P[0])}$: $a={tex_num(a)}$; $g$ — через ${_pt(P[1])}$: $k={tex_num(m)}$. '
                   f'$${tex_num(a)}\\sqrt{{x}}={tex_num(m)}x\\ \\Rightarrow\\ x=0\\ \\text{{или}}\\ \\sqrt{{x}}={tex_num(a / m)}.$$ '
                   f'Точка $A$ — начало координат, абсцисса $B$: $x={tex_num(ans)}$.')
        return Rendered(cond + '\n\n![](figure://graph)', sol + f'\n\n**Ответ:** {dec(ans)}.', {'graph': self.figure(p)})

    def figure(self, p) -> str:
        k = p['kind']
        P = p['pts']
        X0, X1, Y0, Y1 = p.get('window', (-6, 6, -5, 6))
        fig = Figure(width=360, height=320, pad=14)
        axes(fig, X0, X1, Y0, Y1)
        ylim = (Y0, Y1)
        if k in ('log', 'exp', 'hyper', 'sqrt', 'line', 'parabola'):
            _, f = self._func(p)
            if k == 'log':
                a = float(self._func(p)[0])
                g = lambda x: math.log(x, a)
                fig.curve(sample_curve(g, 0.02, X1 - 0.1), ylim=ylim)
            elif k == 'exp':
                a = float(self._func(p)[0])
                fig.curve(sample_curve(lambda x: a ** x, X0, X1), ylim=ylim)
            elif k == 'hyper':
                kk = float(self._func(p)[0])
                fig.curve(sample_curve(lambda x: kk / x, X0, -0.05), ylim=ylim)
                fig.curve(sample_curve(lambda x: kk / x, 0.05, X1), ylim=ylim)
            elif k == 'sqrt':
                a = float(self._func(p)[0])
                fig.curve(sample_curve(lambda x: a * math.sqrt(max(x, 0)), 0, X1), ylim=ylim)
            else:
                fig.curve(sample_curve(lambda x: float(f(F(x).limit_denominator(1000))), X0, X1), ylim=ylim)
        if k == 'two-lines':
            for a_, b_ in (P[:2], P[2:]):
                kk, b = self._line(a_, b_)
                fig.curve(sample_curve(lambda x, kk=kk, b=b: float(kk) * x + float(b), X0, X1), ylim=ylim)
        if k == 'hyper-line':
            kk = float(F(P[0][0]) * P[0][1])
            m, b = self._line(*P[1:3])
            fig.curve(sample_curve(lambda x: kk / x, X0, -0.05), ylim=ylim)
            fig.curve(sample_curve(lambda x: kk / x, 0.05, X1), ylim=ylim)
            fig.curve(sample_curve(lambda x: float(m) * x + float(b), X0, X1), ylim=ylim)
        if k == 'parab-line':
            a, b, c = (float(v) for v in self._parabola(*P[:3]))
            m = P[3][1] / P[3][0]
            fig.curve(sample_curve(lambda x: a * x * x + b * x + c, X0, X1), ylim=ylim)
            fig.curve(sample_curve(lambda x: m * x, X0, X1), ylim=ylim)
        if k == 'sqrt-line':
            (x0, y0), (x1, y1) = P
            a = y0 / math.sqrt(x0)
            m = y1 / x1
            fig.curve(sample_curve(lambda x: a * math.sqrt(max(x, 0)), 0, X1), ylim=ylim)
            fig.curve(sample_curve(lambda x: m * x, X0, X1), ylim=ylim)
        # узлы сетки, по которым восстанавливаются формулы, отмечены точками — как на рисунках ЕГЭ
        for i, q in enumerate(dict.fromkeys(tuple(map(float, q)) for q in P)):
            if X0 <= q[0] <= X1 and Y0 <= q[1] <= Y1:
                fig.items.append(('dot', q))
        if k in ('hyper-line', 'parab-line', 'two-lines'):
            xa = float(p.get('A', 0)) if k != 'two-lines' else float(self.solve(p))
            fA = self._value_at(p, xa)
            if X0 <= xa <= X1 and Y0 <= fA <= Y1:
                fig.point('A', (xa, fA))
                fig.dot('A')
                fig.label('A', at=(xa + 0.4, fA + 0.4))
        return fig.svg()

    def _value_at(self, p, x):
        P = p['pts']
        if p['kind'] == 'hyper-line':
            return P[0][0] * P[0][1] / x
        if p['kind'] == 'parab-line':
            return P[3][1] / P[3][0] * x
        k1, b1 = self._line(*P[:2])
        return float(k1) * x + float(b1)

    # --- аналоги
    def sample(self, rng):
        kind = rng.choice(['log', 'exp', 'hyper', 'sqrt', 'line', 'parabola', 'two-lines', 'hyper-line', 'parab-line', 'sqrt-line'])
        if kind == 'log':
            a = rng.choice([2, 3, sp.Rational(1, 2), sp.Rational(1, 3)])
            x0 = a ** rng.choice([1, 2]) if a > 1 else a ** -1
            y0 = int(sp.log(x0, a))
            if not (0 < x0 <= 5):
                return None
            at = int(a ** rng.choice([3, 4, 5])) if a > 1 else int(a ** -rng.choice([3, 4, 5]))
            return {'kind': kind, 'pts': [(int(x0), y0)], 'at': at, 'window': (-2, 6, -4, 5)}
        if kind == 'exp':
            a = rng.choice([2, 3, sp.Rational(1, 2), sp.Rational(1, 3)])
            x0 = rng.choice([1, 2]) if a > 1 else rng.choice([-1, -2])
            y0 = a ** x0
            if y0 > 5:
                return None
            at = rng.choice([3, 4, 5, -2, -3, -4])
            return {'kind': kind, 'pts': [(x0, int(y0))], 'at': at, 'window': (-5, 5, -2, 6)}
        if kind == 'hyper':
            x0, y0 = rng.choice([(1, 2), (1, 3), (2, 2), (1, -3), (2, -2), (-1, 4), (2, 1), (1, 4), (3, 1), (-2, 2)])
            return {'kind': kind, 'pts': [(x0, y0)], 'at': rng.choice([10, 20, 30, 40, 50, 8, 16]), 'window': (-6, 6, -5, 5)}
        if kind == 'sqrt':
            x0, y0 = rng.choice([(1, 2), (4, 2), (4, 3), (1, 1), (4, 1), (1, 3), (4, 4)])
            return {'kind': kind, 'pts': [(x0, y0)], 'at': rng.choice([9, 16, 25, 36, 49, 64, 81, 100]), 'window': (-1, 7, -1, 6)}
        if kind == 'line':
            x1, y1 = rng.randint(-4, 0), rng.randint(-3, 4)
            x2, y2 = rng.randint(1, 4), rng.randint(-3, 4)
            if y1 == y2:
                return None
            return {'kind': kind, 'pts': [(x1, y1), (x2, y2)], 'at': rng.choice([7, 8, 10, -8, 12, 15, -10])}
        if kind == 'parabola':
            xv, yv = rng.randint(-3, 3), rng.randint(-3, 3)
            a = rng.choice([1, -1, 2, -2, F(1, 2)])
            pts = [(xv, yv), (xv - 1, yv + a), (xv + 2, yv + 4 * a)]
            if any(abs(y) > 5 for _, y in pts) or any(F(y).denominator != 1 for _, y in pts):
                return None
            return {'kind': kind, 'pts': [(x, int(y)) for x, y in pts], 'at': rng.choice([-5, -4, 5, 6, 7, 8])}
        if kind == 'two-lines':
            pts = [(rng.randint(-5, -1), rng.randint(-3, 4)), (rng.randint(1, 4), rng.randint(-3, 4)),
                   (rng.randint(-5, -1), rng.randint(-3, 4)), (rng.randint(1, 4), rng.randint(-3, 4))]
            k1, _ = self._line(*pts[:2])
            k2, _ = self._line(*pts[2:])
            if k1 == k2:
                return None
            p = {'kind': kind, 'pts': pts}
            x = self.solve(p)
            return p if abs(x) > 6 else None  # точка пересечения за пределами рисунка — иначе её видно сразу
        if kind == 'hyper-line':
            kk = rng.choice([2, 3, 4, 6, -2, -3, -4, -6])
            xa = rng.choice([d for d in range(-4, 5) if d and kk % d == 0])
            xb = rng.choice([-8, -6, -5, -4, 4, 5, 6, 8, F(1, 2), F(-1, 2)])
            if xb == xa:
                return None
            # прямая через A(xa, kk/xa) и B(xb, kk/xb): m = −kk/(xa·xb)
            m = F(-kk) / (xa * xb)
            b = F(kk) / xa - m * xa
            p1 = (xa, F(kk) / xa)
            # вторая точка прямой с целыми координатами
            for x in range(-5, 6):
                y = m * x + b
                if y.denominator == 1 and x != xa:
                    return {'kind': kind, 'pts': [(xa, int(F(kk) / xa)), (xa, int(p1[1])), (x, int(y))], 'A': xa}
            return None
        if kind == 'parab-line':
            xa = rng.randint(-3, 3)
            m = rng.choice([1, -1, 2, -2])
            a = rng.choice([1, -1, F(1, 2)])
            xb = rng.choice([5, 6, 7, -5, -6, 8])
            # f(x) − mx = a(x − xa)(x − xb)
            f = lambda x: a * (x - xa) * (x - xb) + m * x
            pts = [(x, f(x)) for x in (xa - 1, xa, xa + 1)]
            if any(F(y).denominator != 1 or abs(y) > 6 for _, y in pts) or xa == 0:
                return None
            return {'kind': kind, 'pts': [(x, int(y)) for x, y in pts] + [(1, m)], 'A': xa}
        x0, y0 = rng.choice([(1, 2), (4, 2), (4, 3), (1, 1), (1, 3)])
        x1, y1 = rng.choice([(2, 1), (3, 1), (4, 1), (1, 1), (3, 2), (4, 3)])
        return {'kind': 'sqrt-line', 'pts': [(x0, y0), (x1, y1)], 'window': (-1, 7, -1, 6)}


TEMPLATES = [Graphs()]
EXTRA = [(Graphs(), 40)]
