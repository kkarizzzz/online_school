"""
№ 8. Производная и первообразная.

Данные этих заданий — график на рисунке. Аналоги рисуем сами: график строится сплайном Эрмита по узлам,
в которых заданы значения и наклоны, поэтому знаки производной и точки экстремума известны точно.
Числа с рисунков ФИПИ переписаны вручную в data/fipi/manual.json и проверены ответом ФИПИ.
"""
import math
import random
from fractions import Fraction

from app.bankgen.core import Rendered, Template, dec, frac, lin, par, poly, signed, tex_frac, tex_num
from app.bankgen.figures import Figure, axes, hermite, sample_curve

COUNT_WORDS = {5: 'пять', 6: 'шесть', 7: 'семь', 8: 'восемь', 9: 'девять', 10: 'десять', 11: 'одиннадцать', 12: 'двенадцать'}


def _xs_list(n: int) -> str:
    return ', '.join(f'$x_{{{i}}}$' if i > 9 else f'$x_{i}$' for i in range(1, n + 1))


class GraphTemplate(Template):
    number = 8
    topic = 'Производная по графику'

    def render(self, p):
        cond, sol, fig = self.build(p)
        if fig is None and (drawn := self.complete(p)) is not None:
            # оригинал ФИПИ: по снятым с рисунка данным строим свой график (complete проверяет, что данные те же)
            fig = self.build(drawn)[2]
        figures = {}
        if fig is not None:
            cond += '\n\n![](figure://graph)'
            figures['graph'] = fig.svg()
        return Rendered(cond, sol + f'\n\n**Ответ:** {dec(self.solve(p)) if not isinstance(self.solve(p), str) else self.solve(p)}.',
                        figures)

    def match(self, task):
        return None  # оригиналы — только через manual.json

    def complete(self, p) -> dict | None:
        """Параметры рисунка для оригинала ФИПИ (там известны только данные с картинки); None — не умеем"""
        return None


def _rng(p) -> random.Random:
    return random.Random(repr(sorted((k, v) for k, v in p.items() if not callable(v))))


def _slope(f, x: float, h: float = 1e-4) -> float:
    return (f(x + h) - f(x - h)) / (2 * h)


def _roots(f, a: float, b: float, step: float = 0.01) -> list[float]:
    """Точки смены знака f на [a; b]"""
    out, x, prev = [], a, f(a)
    while x < b:
        x2 = min(x + step, b)
        cur = f(x2)
        if (prev == 0 or (prev < 0) != (cur < 0)) and not (out and x2 - out[-1] < 0.05):   # шум у нуля — одна точка
            out.append(x2)
        x, prev = x2, cur
    return out


def _grid(a: float, b: float, n: int = 400) -> list[float]:
    return [a + (b - a) * i / n for i in range(n + 1)]


def _pieces_knots(xs: list[float], dirs: list[int], ys: tuple[float, float]) -> list[tuple[float, float, float]]:
    """
    Узлы графика f, монотонного на кусках [xs[i]; xs[i+1]] в направлении dirs[i] (соседние направления разные):
    нулевые наклоны во всех узлах — тогда кубический сплайн Эрмита строго монотонен на каждом куске
    """
    lo, hi = ys
    y = lo + 1 if dirs[0] > 0 else hi - 1
    knots = [(xs[0], y, 0.0)]
    for i, d in enumerate(dirs):
        y = min(max(y + d * (2.5 if i % 2 == 0 else 3), lo + 0.5), hi - 0.5)
        knots.append((xs[i + 1], y, 0.0))
    return knots


def _extrema_knots(rng: random.Random, x0: int, x1: int, y0: int, y1: int, n_ext: int) -> list[tuple[float, float, float]]:
    """Узлы графика f: концы и n_ext экстремумов в целых точках, значения чередуются (максимум/минимум)"""
    xs = sorted(rng.sample(range(x0 + 1, x1), n_ext))
    if any(b - a < 2 for a, b in zip(xs, xs[1:])):
        return []
    up = rng.random() < 0.5
    knots = []
    for i, x in enumerate(xs):
        is_max = (i % 2 == 0) == up
        y = rng.randint(1, y1 - 1) if is_max else rng.randint(y0 + 1, -1 if rng.random() < 0.6 else 1)
        knots.append((x, y, 0.0))
    for a, b in zip(knots, knots[1:]):
        if a[1] == b[1]:
            return []
    # концы: продолжаем монотонность за крайними экстремумами
    first, last = knots[0], knots[-1]
    first_is_max = first[1] > knots[1][1] if len(knots) > 1 else up
    y_start = first[1] - rng.randint(1, 3) if first_is_max else first[1] + rng.randint(1, 3)
    last_is_max = last[1] > knots[-2][1] if len(knots) > 1 else not up
    y_end = last[1] - rng.randint(1, 3) if last_is_max else last[1] + rng.randint(1, 3)
    if not (y0 <= y_start <= y1 and y0 <= y_end <= y1):
        return []
    s0 = (first[1] - y_start) / (first[0] - x0) * 0.8
    s1 = (y_end - last[1]) / (x1 - last[0]) * 0.8
    return [(x0, y_start, s0)] + knots + [(x1, y_end, s1)]


def _df_knots(rng: random.Random, X0: int, X1: int, zeros_x: list[int], start_sign: int):
    """
    Узлы графика f': нули (с наклоном нужного знака) и пики посередине между нулями.
    Возвращает (функция g, [(ноль, +2 — минимум f / -2 — максимум f)]).
    """
    pts = [X0] + zeros_x + [X1]
    knots, zeros = [], []
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        s = start_sign * (-1) ** i
        knots.append(((a + b) / 2, s * (rng.randint(1, 3) + 0.5), 0.0))
    for i, z in enumerate(zeros_x):
        left = start_sign * (-1) ** i          # знак f' слева от нуля
        knots.append((z, 0.0, -left * 1.6))    # справа знак противоположный — наклон в его сторону
        zeros.append((z, -2 * left))
    knots.append((X0, knots[0][1] * 0.6, 0.0))
    knots.append((X1, knots[len(pts) - 2][1] * 0.6, 0.0))
    return hermite(knots), zeros


def _zeros(rng: random.Random, X0: int, X1: int, count: int) -> list[int]:
    """Целые нули f' не ближе 2 друг к другу и к концам"""
    xs = sorted(rng.sample(range(X0 + 2, X1 - 1), count))
    return [] if any(b - a < 2 for a, b in zip(xs, xs[1:])) else xs


def _zx(z) -> str:
    """Абсцисса нуля: целая — как есть, снятая с рисунка между узлами сетки — приближённо"""
    if float(z).is_integer():
        return f'x={int(z)}'
    return 'x\\approx ' + str(z).replace('.', '{,}')


def _sign_on(knots, x: float) -> int:
    """Знак f' в точке x для сплайна по узлам с нулевыми наклонами в экстремумах"""
    for (a, ya, _), (b, yb, _) in zip(knots, knots[1:]):
        if a < x < b:
            return 1 if yb > ya else -1
    raise ValueError('точка вне графика или в узле')


# ---------------------------------------------------------------------------

class Tangent(GraphTemplate):
    """f'(x₀) — угловой коэффициент касательной через две точки сетки"""
    topic, code = 'Касательная и производная', '8.tangent'

    def solve(self, p):
        (x1, y1), (x2, y2) = p['A'], p['B']
        return Fraction(y2 - y1, x2 - x1)

    def build(self, p):
        (x1, y1), (x2, y2) = p['A'], p['B']
        k = self.solve(p)
        cond = ('На рисунке изображены график функции $y=f(x)$ и касательная к нему в точке с абсциссой $x_0$. '
                'Найдите значение производной функции $f(x)$ в точке $x_0$.')
        sol = (f'Значение производной в точке касания равно угловому коэффициенту касательной. Касательная проходит через точки сетки '
               f'$({x1};{y1})$ и $({x2};{y2})$, поэтому $$f\'(x_0)=k=\\frac{{{y2}-{par(y1)}}}{{{x2}-{par(x1)}}}=\\frac{{{y2 - y1}}}{{{x2 - x1}}}={tex_num(k)}.$$')
        fig = self.figure(p) if 'window' in p else None
        return cond, sol, fig

    def figure(self, p):
        (x1, y1), (x2, y2) = p['A'], p['B']
        k = (y2 - y1) / (x2 - x1)
        x0, a, c = p['x0'], p['a'], p.get('c', 0.0)
        line = lambda x: y1 + k * (x - x1)
        f = lambda x: line(x) + a * (x - x0) ** 2 + c * (x - x0) ** 3
        X0, X1, Y0, Y1 = p['window']
        fig = Figure(width=420, height=320, pad=16)
        axes(fig, X0, X1, Y0, Y1)
        fig.curve(sample_curve(f, X0 + 0.2, X1 - 0.2), ylim=(Y0 + 0.1, Y1 - 0.1))
        fig.curve(sample_curve(line, X0, X1), width=1.4, ylim=(Y0, Y1))
        fig.items.append(('seg', (x0, 0), (x0, line(x0)), True, 1.0))
        # подпись x₀ ниже, если рядом подписи «0» и «1»
        fig.text((x0, -1.1 if min(abs(x0), abs(x0 - 1)) < 0.8 else -0.5),
                 'x<tspan baseline-shift=\'sub\' font-size=\'11\'>0</tspan>', 15, italic=True)
        # узлы сетки, через которые проходит касательная, — по ним находят угловой коэффициент
        for name, pt in (('A', (x1, y1)), ('B', (x2, y2))):
            fig.point(name, pt)
            fig.dot(name)
        return fig

    def complete(self, p):
        if 'window' in p:
            return None
        (x1, y1), (x2, y2) = p['A'], p['B']
        k = (y2 - y1) / (x2 - x1)
        X0, X1 = min(x1, x2, 0) - 2, max(x1, x2, 0) + 2
        Y0, Y1 = min(y1, y2, 0) - 2, max(y1, y2, 0) + 2
        mid = (x1 + x2) / 2
        x0 = round(mid) if min(x1, x2) < round(mid) < max(x1, x2) else mid
        yc = y1 + k * (x0 - x1)
        a = -0.3 if yc > (Y0 + Y1) / 2 else 0.3      # парабола уходит туда, где больше места
        return {**p, 'x0': x0, 'a': a, 'c': 0.0, 'window': (X0, X1, Y0, Y1)}

    def sample(self, rng):
        # касательная через две точки сетки, точка касания между ними или рядом
        X0, X1, Y0, Y1 = -6, 8, -4, 7
        x1 = rng.randint(X0 + 1, 1)
        x2 = x1 + rng.choice([2, 3, 4, 5, 6, 8])
        y1 = rng.randint(Y0 + 1, Y1 - 1)
        y2 = y1 + rng.choice([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5])
        if not (Y0 < y2 < Y1) or x2 >= X1:
            return None
        x0 = rng.choice([x for x in range(X0 + 2, X1 - 2) if x not in (x1, x2)] or [x1 + 1])
        a = rng.choice([-0.35, -0.25, 0.25, 0.35])
        p = {'A': (x1, y1), 'B': (x2, y2), 'x0': x0, 'a': a, 'c': rng.choice([0, 0.03, -0.03]), 'window': (X0, X1, Y0, Y1)}
        # график должен остаться в окне на заметном отрезке вокруг x0
        k = (y2 - y1) / (x2 - x1)
        if not (Y0 + 1 < y1 + k * (x0 - x1) < Y1 - 1):
            return None
        return p

    def nice(self, x):
        return frac(x).denominator in (1, 2, 4, 5) and x != 0


class MarkedPoints(GraphTemplate):
    """Отмеченные точки на графике f или f': сколько из них, где f' > 0 / f' < 0 / f возрастает / убывает"""
    topic, code = 'Производная по графику', '8.marked'

    def solve(self, p):
        if 'answer' in p:
            return p['answer']
        want = 1 if p['ask'] in ('positive', 'increasing') else -1
        return sum(1 for s in self._signs(p) if s == want)

    def _signs(self, p) -> list[int]:
        if 'signs' in p:  # оригинал ФИПИ: знаки производной в отмеченных точках сняты с рисунка
            return [1 if c == '+' else -1 for c in p['signs']]
        return [self._sign(p, x) for x in p['marks']]

    def _sign(self, p, x):
        if p['graph'] == 'f':
            return _sign_on(p['knots'], x)
        return 1 if p['g'](x) > 0 else -1

    def build(self, p):
        signs = self._signs(p)
        n = len(signs)
        if p['graph'] == 'f':
            ask = 'положительна' if p['ask'] == 'positive' else 'отрицательна'
            cond = (f'На рисунке изображён график функции $y=f(x)$. На оси абсцисс отмечено {COUNT_WORDS[n]} точек: {_xs_list(n)}. '
                    f'Найдите количество отмеченных точек, в которых производная функции $f(x)$ {ask}.')
            rule = ('Производная положительна там, где функция возрастает, и отрицательна там, где убывает. '
                    if True else '')
            pos = [f'x_{{{i + 1}}}' for i, sg in enumerate(signs) if sg > 0]
            neg = [f'x_{{{i + 1}}}' for i, sg in enumerate(signs) if sg < 0]
            chosen = pos if p['ask'] == 'positive' else neg
            sol = rule + (f'Функция {"возрастает" if p["ask"] == "positive" else "убывает"} в точках ${", ".join(chosen)}$ — '
                          f'их {len(chosen)}.')
        else:
            ask = 'возрастания' if p['ask'] == 'increasing' else 'убывания'
            cond = (f'На рисунке изображён график $y=f\'(x)$ — производной функции $f(x)$. На оси абсцисс отмечено {COUNT_WORDS[n]} точек: '
                    f'{_xs_list(n)}. Сколько из этих точек принадлежит промежуткам {ask} функции $f(x)$?')
            pos = [f'x_{{{i + 1}}}' for i, sg in enumerate(signs) if sg > 0]
            neg = [f'x_{{{i + 1}}}' for i, sg in enumerate(signs) if sg < 0]
            chosen = pos if p['ask'] == 'increasing' else neg
            sol = (f'Функция {"возрастает" if p["ask"] == "increasing" else "убывает"} там, где производная '
                   f'{"положительна (график $f\'$ выше оси абсцисс)" if p["ask"] == "increasing" else "отрицательна (график $f\'$ ниже оси абсцисс)"}. '
                   f'Таких отмеченных точек {len(chosen)}: ${", ".join(chosen)}$.')
        if 'marks' not in p:
            return cond, sol, None
        fig = Figure(width=440, height=280, pad=16)
        X0, X1, Y0, Y1 = p['window']
        axes(fig, X0, X1, Y0, Y1, ticks=False)
        f = p['g'] if p['graph'] == 'df' else hermite(p['knots'])
        fig.curve(sample_curve(f, p['span'][0], p['span'][1]))
        for i, x in enumerate(p['marks']):
            fig.items.append(('seg', (x, 0), (x, f(x)), True, 0.9))
            fig.items.append(('seg', (x, -0.12), (x, 0.12), False, 1.6))
            label = f"x<tspan baseline-shift='sub' font-size='11'>{i + 1}</tspan>"
            fig.text((x, 0.45 if f(x) < 0 else -0.5), label, 14, italic=True)
        fig.text((p['span'][0] + 1.2, Y1 - 0.4), "y = f(x)" if p['graph'] == 'f' else "y = f ′(x)", 15, italic=True)
        return cond, sol, fig

    def complete(self, p):
        if 'marks' in p or 'signs' not in p:
            return None
        signs = self._signs(p)
        n = len(signs)
        shift = 1 if n % 2 else 0
        marks = [2 * i - (n - 1) + shift for i in range(n)]       # через 2, ни одна не в нуле
        X0, X1, Y0, Y1 = marks[0] - 2, marks[-1] + 2, -4, 5
        cuts = [(a + b) / 2 for a, b, sa, sb in zip(marks, marks[1:], signs, signs[1:]) if sa != sb]
        if p['graph'] == 'f':
            xs = [X0 + 0.5] + cuts + [X1 - 0.5]
            dirs = [signs[0] * (-1) ** i for i in range(len(xs) - 1)]
            knots = _pieces_knots(xs, dirs, (Y0, Y1))
            if [_sign_on(knots, x) for x in marks] != signs:
                return None
            return {**p, 'knots': knots, 'marks': marks, 'window': (X0, X1, Y0, Y1), 'span': (X0 + 0.5, X1 - 0.5)}
        g, _ = _df_knots(_rng(p), X0 + 0.5, X1 - 0.5, cuts, signs[0])
        if [1 if g(x) > 0 else -1 for x in marks] != signs or any(abs(g(x)) < 0.3 for x in marks):
            return None
        return {**p, 'g': g, 'marks': marks, 'window': (X0, X1, Y0, Y1), 'span': (X0 + 0.5, X1 - 0.5)}

    def sample(self, rng):
        X0, X1, Y0, Y1 = -8, 8, -4, 5
        graph = rng.choice(['f', 'df'])
        n = rng.choice([7, 8, 9, 10])
        if graph == 'f':
            knots = _extrema_knots(rng, X0 + 1, X1 - 1, Y0, Y1, rng.choice([3, 4, 5]))
            if not knots:
                return None
            ext = [k[0] for k in knots]
            cand = [x / 2 for x in range(2 * (X0 + 1) + 1, 2 * (X1 - 1)) if all(abs(x / 2 - e) >= 0.5 for e in ext)]
            if len(cand) < n:
                return None
            marks = sorted(rng.sample(cand, n))
            if any(b - a < 1 for a, b in zip(marks, marks[1:])):
                return None
            return {'graph': 'f', 'knots': knots, 'marks': marks, 'ask': rng.choice(['positive', 'negative']),
                    'window': (X0, X1, Y0, Y1), 'span': (X0 + 1, X1 - 1)}
        # f' — сплайн через нули (с наклоном) и пики между ними
        zeros = _zeros(rng, X0 + 1, X1 - 1, rng.choice([3, 4, 5]))
        if not zeros:
            return None
        g, _ = _df_knots(rng, X0 + 1, X1 - 1, zeros, rng.choice([1, -1]))
        cand = [x / 2 for x in range(2 * (X0 + 1) + 1, 2 * (X1 - 1)) if all(abs(x / 2 - z) >= 0.5 for z in zeros)]
        marks = sorted(rng.sample(cand, n)) if len(cand) >= n else []
        if not marks or any(b - a < 1 for a, b in zip(marks, marks[1:])):
            return None
        # проверим, что знак g между нулями действительно чередуется
        for x in marks:
            if abs(g(x)) < 0.15:
                return None
        return {'graph': 'df', 'g': g, 'marks': marks, 'ask': rng.choice(['increasing', 'decreasing']),
                'window': (X0, X1, Y0, Y1), 'span': (X0 + 1, X1 - 1)}

    def nice(self, x):
        return isinstance(x, int) and x > 0


class DerivativeGraph(GraphTemplate):
    """По графику f' на интервале: точки экстремума, максимума, минимума, наибольшее/наименьшее значение f на отрезке"""
    topic, code = 'Производная по графику', '8.df-graph'

    def solve(self, p):
        if 'answer' in p:
            return p['answer']
        a, b = p['seg']
        zs = [(z, s) for z, s in p['zeros'] if a <= z <= b]   # s: знак f' справа минус знак слева: +2 → минимум, -2 → максимум
        ask = p['ask']
        if ask == 'extrema':
            return len(zs)
        if ask == 'max-count':
            return sum(1 for _, s in zs if s < 0)
        if ask == 'min-count':
            return sum(1 for _, s in zs if s > 0)
        if ask == 'extremum-point':
            return zs[0][0]
        if ask in ('max-point', 'min-point'):
            want = -2 if ask == 'max-point' else 2
            found = [z for z, s in p['zeros'] if s == want]
            if len(found) != 1:
                raise ValueError('не одна точка')
            return found[0]
        if ask in ('argmax', 'argmin'):
            # на отрезке без смены знака f' — конец отрезка
            sign = p['sign_on_seg']
            if ask == 'argmax':
                return b if sign > 0 else a
            return a if sign > 0 else b
        raise ValueError(ask)

    def build(self, p):
        X0, X1 = p['domain']
        a, b = p.get('seg', (X0, X1))
        head = (f'На рисунке изображён график $y=f\'(x)$ — производной функции $f(x)$, определённой на интервале $({X0};{X1})$. ')
        ask = p['ask']
        q = {'extrema': f'Найдите количество точек экстремума функции $f(x)$, принадлежащих отрезку $[{a};{b}]$.',
             'max-count': f'Найдите количество точек максимума функции $f(x)$, принадлежащих отрезку $[{a};{b}]$.',
             'min-count': f'Найдите количество точек минимума функции $f(x)$, принадлежащих отрезку $[{a};{b}]$.',
             'extremum-point': f'Найдите точку экстремума функции $f(x)$, принадлежащую отрезку $[{a};{b}]$.',
             'argmax': f'В какой точке отрезка $[{a};{b}]$ функция $f(x)$ принимает наибольшее значение?',
             'argmin': f'В какой точке отрезка $[{a};{b}]$ функция $f(x)$ принимает наименьшее значение?',
             'max-point': 'Найдите точку максимума функции $f(x)$.',
             'min-point': 'Найдите точку минимума функции $f(x)$.'}[ask]
        cond = head + q
        zs = [(z, s) for z, s in p['zeros'] if a <= z <= b]
        if ask in ('argmax', 'argmin'):
            sign = p['sign_on_seg']
            sol = (f'На отрезке $[{a};{b}]$ производная {"положительна" if sign > 0 else "отрицательна"} (график $f\'$ '
                   f'{"выше" if sign > 0 else "ниже"} оси абсцисс), значит, функция {"возрастает" if sign > 0 else "убывает"}. '
                   f'{"Наибольшее" if ask == "argmax" else "Наименьшее"} значение достигается на конце отрезка: $x={self.solve(p)}$.')
        else:
            kinds = ', '.join(f'${_zx(z)}$ ({"максимум: $f\'$ меняет знак с «+» на «−»" if s < 0 else "минимум: $f\'$ меняет знак с «−» на «+»"})' for z, s in zs)
            sol = ('В точках экстремума производная обращается в ноль и меняет знак: график $f\'$ пересекает ось абсцисс. '
                   + (f'На отрезке $[{a};{b}]$' if ask not in ('max-point', 'min-point') else 'На всём интервале') + f' это точки {kinds}.')
            sol += {'extrema': f' Всего {len(zs)}.', 'max-count': f' Точек максимума: {self.solve(p)}.',
                    'min-count': f' Точек минимума: {self.solve(p)}.', 'extremum-point': '',
                    'max-point': f' Точка максимума: $x={self.solve(p)}$.', 'min-point': f' Точка минимума: $x={self.solve(p)}$.'}[ask]
        if 'g' not in p:
            return cond, sol, None
        fig = Figure(width=460, height=280, pad=16)
        Y0, Y1 = p['yrange']
        axes(fig, X0, X1, Y0, Y1, ticks=True)
        fig.curve(sample_curve(p['g'], X0, X1))
        fig.hollow((X0, p['g'](X0))), fig.hollow((X1, p['g'](X1)))
        fig.text((X0 + 0.0, -0.5), str(X0), 13)
        fig.text((X1 + 0.0, -0.5), str(X1), 13)
        fig.text(((X0 + X1) / 2, Y1 - 0.4), 'y = f ′(x)', 15, italic=True)
        return cond, sol, fig

    def complete(self, p):
        if 'g' in p:
            return None
        X0, X1 = p['domain']
        zeros = [z for z, _ in p['zeros']]
        if zeros:
            start = -1 if p['zeros'][0][1] > 0 else 1
        else:
            # нулей в данных нет (наибольшее/наименьшее значение на отрезке, где f' не меняет знак):
            # один ноль ставим вне отрезка, на большем из оставшихся кусков
            a, b = p['seg']
            lo, hi = max([(X0, a), (b, X1)], key=lambda r: r[1] - r[0])
            if hi - lo < 2:
                return None
            zeros = [(lo + hi) / 2]
            start = p['sign_on_seg'] if lo == b else -p['sign_on_seg']
        g, made = _df_knots(_rng(p), X0, X1, zeros, start)
        found = _roots(g, X0 + 0.05, X1 - 0.05)
        if len(found) != len(zeros) or any(abs(f - z) > 0.05 for f, z in zip(found, zeros)):
            return None
        if p['zeros'] and [s for _, s in made] != [s for _, s in p['zeros']]:
            return None
        if 'sign_on_seg' in p and any((g(x) > 0) != (p['sign_on_seg'] > 0) for x in _grid(*p['seg'])):
            return None
        values = [g(x) for x in _grid(X0, X1)]
        return {**p, 'g': g, 'yrange': (math.floor(min(min(values), -1)) - 1, math.ceil(max(max(values), 1)) + 1)}

    def sample(self, rng):
        X0 = -rng.randint(5, 9)
        X1 = rng.randint(4, 8)
        zeros_x = _zeros(rng, X0, X1, rng.choice([3, 4, 5]))
        if not zeros_x:
            return None
        start_sign = rng.choice([1, -1])
        pts = [X0] + zeros_x + [X1]
        g, zeros = _df_knots(rng, X0, X1, zeros_x, start_sign)
        ask = rng.choice(['extrema', 'max-count', 'min-count', 'extremum-point', 'argmax', 'argmin'])
        if ask in ('argmax', 'argmin'):
            # отрезок внутри промежутка знакопостоянства
            gaps = [(a, b) for a, b in zip(pts, pts[1:]) if b - a >= 3]
            if not gaps:
                return None
            a, b = rng.choice(gaps)
            seg = (a + 1, b - 1) if b - a >= 4 else (a + 1, b - 1)
            if seg[0] >= seg[1]:
                return None
            i = pts.index(a)
            sign = start_sign * (-1) ** i
            return {'domain': (X0, X1), 'zeros': zeros, 'seg': seg, 'ask': ask, 'g': g, 'yrange': (-4, 4), 'sign_on_seg': sign}
        a = rng.randint(X0 + 1, zeros_x[0])
        b = rng.randint(zeros_x[-1], X1 - 1)
        if ask == 'extremum-point':
            z = rng.choice(zeros_x)
            i = zeros_x.index(z)
            a = (zeros_x[i - 1] + 1) if i > 0 else X0 + 1
            b = (zeros_x[i + 1] - 1) if i + 1 < len(zeros_x) else X1 - 1
            a, b = rng.randint(a, z), rng.randint(z, b)
        p = {'domain': (X0, X1), 'zeros': zeros, 'seg': (a, b), 'ask': ask, 'g': g, 'yrange': (-4, 4)}
        return p if self.solve(p) else None

    def nice(self, x):
        return isinstance(x, int)


class FunctionGraphRoots(GraphTemplate):
    """График f на интервале: число корней f'(x) = 0 на отрезке (= экстремумы f)"""
    topic, code = 'Производная по графику', '8.f-roots'

    def solve(self, p):
        if 'answer' in p:
            return p['answer']
        ext = p['extrema'] if 'extrema' in p else [x for x, _, _ in p['knots'][1:-1]]
        if p.get('ask') == 'root':
            return ext[0]
        a, b = p['seg']
        return sum(1 for x in ext if a <= x <= b)

    def build(self, p):
        X0, X1 = p['domain']
        ext = p['extrema'] if 'extrema' in p else [x for x, _, _ in p['knots'][1:-1]]
        if p.get('ask') == 'root':
            cond = (f'На рисунке изображён график функции $y=f(x)$, определённой на интервале $({X0};{X1})$. '
                    f"Найдите корень уравнения $f'(x)=0$.")
            sol = f'Производная равна нулю там, где касательная к графику горизонтальна, — в точке экстремума. На графике она одна: $x={ext[0]}$.'
        else:
            a, b = p['seg']
            cond = (f'На рисунке изображён график функции $y=f(x)$, определённой на интервале $({X0};{X1})$. Найдите количество корней '
                    f'уравнения $f\'(x)=0$, принадлежащих отрезку $[{a};{b}]$.')
            pts = [x for x in ext if a <= x <= b]
            sol = (f'Производная равна нулю в точках, где касательная горизонтальна, — в точках максимума и минимума. На отрезке $[{a};{b}]$ '
                   f'это точки ${"; ".join(str(x) for x in pts)}$ — всего {len(pts)}.')
        if 'knots' not in p:
            return cond, sol, None
        fig = Figure(width=460, height=280, pad=16)
        axes(fig, X0, X1, -4, 5)
        f = hermite(p['knots'])
        fig.curve(sample_curve(f, X0, X1))
        fig.hollow((X0, f(X0))), fig.hollow((X1, f(X1)))
        fig.text((X0, -0.5), str(X0), 13), fig.text((X1, -0.5), str(X1), 13)
        return cond, sol, fig

    def complete(self, p):
        if 'knots' in p or 'extrema' not in p:
            return None
        X0, X1 = p['domain']
        ext = sorted(p['extrema'])
        rng = _rng(p)
        up = rng.random() < 0.5
        # размах колебаний не больше расстояния до соседних экстремумов — иначе при шаге 1 получаются «иголки»
        gaps = [min([b - a for a, b in zip(ext, ext[1:])][max(i - 1, 0):i + 1] or [3]) for i in range(len(ext))]
        inner = [(x, (rng.choice([2, 3, 4]) if (i % 2 == 0) == up else rng.choice([-3, -2, -1])) * min(1, 0.6 * gaps[i]), 0.0)
                 for i, x in enumerate(ext)]
        y_start = inner[0][1] + (-1.5 if inner[0][1] > 0 else 1.5)
        y_end = inner[-1][1] + (-1.5 if inner[-1][1] > 0 else 1.5)
        knots = ([(X0, y_start, (inner[0][1] - y_start) / (ext[0] - X0) * 0.8)] + inner
                 + [(X1, y_end, (y_end - inner[-1][1]) / (X1 - ext[-1]) * 0.8)])
        f = hermite(knots)
        found = _roots(lambda x: _slope(f, x), X0 + 0.02, X1 - 0.02, 0.005)
        if len(found) != len(ext) or any(abs(a - b) > 0.02 for a, b in zip(found, ext)):
            return None
        return {**p, 'knots': knots}

    def sample(self, rng):
        X0, X1 = -rng.randint(6, 9), rng.randint(4, 8)
        knots = _extrema_knots(rng, X0, X1, -4, 5, rng.choice([4, 5, 6]))
        if not knots:
            return None
        ext = [x for x, _, _ in knots[1:-1]]
        a, b = rng.randint(X0 + 1, ext[1]), rng.randint(ext[-2], X1 - 1)
        if a > b:
            return None
        p = {'domain': (X0, X1), 'knots': knots, 'seg': (a, b)}
        return p if self.solve(p) else None

    def nice(self, x):
        return isinstance(x, int)


class FourPoints(GraphTemplate):
    """На оси отмечены точки: в какой из них производная наибольшая / наименьшая (сравниваем наклоны касательных)"""
    topic, code = 'Производная по графику', '8.four-points'
    variants = False

    def solve(self, p):
        return p['answer']

    def build(self, p):
        pts, ask, trend = p['pts'], p['ask'], p['trend']
        listing = ', '.join(f'${x}$' for x in pts)
        word = 'наибольшее' if ask == 'max' else 'наименьшее'
        cond = (f'На рисунке изображён график функции $y=f(x)$. На оси абсцисс отмечены точки {listing}. В какой из этих точек значение '
                f'производной функции $f(x)$ {word}? В ответе укажите эту точку.')
        inc = [str(x) for x, t in zip(pts, trend) if t == '+']
        dec_ = [str(x) for x, t in zip(pts, trend) if t == '-']
        parts = []
        if dec_:
            parts.append(f'в точках ${", ".join(dec_)}$ функция убывает — там $f\'(x)<0$' if len(dec_) > 1 else f'в точке ${dec_[0]}$ функция убывает — $f\'<0$')
        if inc:
            parts.append(f'в точках ${", ".join(inc)}$ функция возрастает — там $f\'(x)>0$' if len(inc) > 1 else f'в точке ${inc[0]}$ функция возрастает — $f\'>0$')
        steep = ('Из точек возрастания график круче всего поднимается' if ask == 'max' else 'Из точек убывания график круче всего опускается')
        sol = ('Значение производной равно угловому коэффициенту касательной к графику. По рисунку: ' + '; '.join(parts) + '. '
               + (f'{steep} в точке $x={p["answer"]}$ — там касательная наклонена сильнее всего.'
                  if (ask == 'max' and len(inc) > 1) or (ask == 'min' and len(dec_) > 1)
                  else f'Поэтому {word} значение производной — в точке $x={p["answer"]}$.'))
        if 'knots' not in p:
            return cond, sol, None
        X0, X1, Y0, Y1 = p['window']
        fig = Figure(width=440, height=300, pad=16)
        axes(fig, X0, X1, Y0, Y1)
        f = hermite(p['knots'])
        fig.curve(sample_curve(f, p['knots'][0][0], p['knots'][-1][0]), ylim=(Y0, Y1))
        for x in pts:
            fig.items.append(('seg', (x, 0), (x, f(x)), True, 0.9))
            if x not in (0, 1):
                fig.text((x, 0.45 if f(x) < 0 else -0.5), str(x), 14)
        fig.text((p['knots'][-1][0] - 1, Y1 - 0.4), 'y = f(x)', 15, italic=True)
        return cond, sol, fig

    def complete(self, p):
        if 'knots' in p:
            return None
        pts, trend, ask, ans = p['pts'], p['trend'], p['ask'], p['answer']
        others = iter([0.5, 0.8, 1.1])
        slopes = []
        for x, t in zip(pts, trend):
            if t == '0':
                slopes.append(0.0)
            elif x == ans:
                slopes.append(2.2 if ask == 'max' else -2.2)
            else:
                slopes.append((1 if t == '+' else -1) * next(others))
        ys = [0.0]
        for i in range(1, len(pts)):
            ys.append(ys[-1] + (slopes[i - 1] + slopes[i]) / 2 * (pts[i] - pts[i - 1]))
        shift = 1 - (max(ys) + min(ys)) / 2
        knots = [(x, y + shift, m) for x, y, m in zip(pts, ys, slopes)]
        first, last = knots[0], knots[-1]
        knots = ([(first[0] - 1.5, first[1] - first[2] * 1.5, first[2])] + knots
                 + [(last[0] + 1.5, last[1] + last[2] * 1.5, last[2])])
        f = hermite(knots)
        d = [_slope(f, x) for x in pts]
        signs = ''.join('0' if abs(v) < 1e-3 else '+' if v > 0 else '-' for v in d)
        best = pts[d.index(max(d) if ask == 'max' else min(d))]
        if signs != trend or best != ans:
            return None
        values = [f(x) for x in _grid(knots[0][0], knots[-1][0])]
        window = (min(math.floor(knots[0][0]) - 1, -1), max(math.ceil(knots[-1][0]) + 1, 2),
                  min(math.floor(min(values)) - 1, -1), max(math.ceil(max(values)) + 1, 2))
        return {**p, 'knots': knots, 'window': window}

    def sample(self, rng):
        return None  # аналоги этого типа строятся вместе с рисунком отдельно


# ---------------------------------------------------------------------------
# Аналитические прототипы (без рисунка) — встречаются в банках подготовки
# ---------------------------------------------------------------------------

class MotionVelocity(Template):
    """x(t) — многочлен: скорость в момент t₀ или момент, когда скорость равна v"""
    number, topic, code = 8, 'Физический смысл производной', '8.motion'

    def solve(self, p):
        a, b, c, d = p['coefs']
        if p['ask'] == 'v':
            t = p['t']
            return 3 * a * t * t + 2 * b * t + c
        # 3a t² + 2b t + c = v → положительный корень
        A, B, C = 3 * a, 2 * b, c - p['v']
        D = B * B - 4 * A * C
        r = math.isqrt(int(D)) if D >= 0 and frac(D).denominator == 1 else -1
        if r < 0 or r * r != D:
            raise ValueError('нецелое время')
        roots = sorted({Fraction(-B + r, 2 * A), Fraction(-B - r, 2 * A)})
        pos = [x for x in roots if x > 0]
        if len(pos) != 1:
            raise ValueError('не один положительный корень')
        return pos[0]

    def verify(self, p, ans):
        a, b, c, d = p['coefs']
        h = 1e-6
        x = lambda t: a * t ** 3 + b * t ** 2 + c * t + d
        if p['ask'] == 'v':
            t = float(p['t'])
            return math.isclose((x(t + h) - x(t - h)) / (2 * h), float(ans), abs_tol=1e-4)
        t = float(ans)
        return math.isclose((x(t + h) - x(t - h)) / (2 * h), float(p['v']), abs_tol=1e-4)

    def render(self, p):
        a, b, c, d = p['coefs']
        law = poly([a, b, c, d], 't')
        v = poly([3 * a, 2 * b, c], 't')
        head = (f'Материальная точка движется прямолинейно по закону $x(t)={law}$, где $x$ — расстояние от точки отсчёта в метрах, '
                f'$t$ — время в секундах, измеренное с начала движения. ')
        if p['ask'] == 'v':
            t = p['t']
            cond = head + f'Найдите её скорость (в метрах в секунду) в момент времени $t={t}$ с.'
            sol = (f'Скорость — производная координаты по времени: $$v(t)=x\'(t)={v}.$$ '
                   f'$$v({t})={poly([3 * a, 2 * b, c], str(t)).replace(str(t) + "^2", f"{3 * a if 3 * a != 1 else ""}\\cdot {t}^2")}={tex_num(self.solve(p))}.$$')
            sol = (f'Скорость — производная координаты по времени: $$v(t)=x\'(t)={v}.$$ Подставим $t={t}$: '
                   f'$$v({t})={tex_num(3 * a)}\\cdot {t}^2{signed(2 * b)}\\cdot {t}{signed(c) if c else ""}={tex_num(self.solve(p))}.$$')
        else:
            cond = head + f'В какой момент времени (в секундах) её скорость была равна ${p["v"]}$ м/с?'
            sol = (f'Скорость — производная координаты: $v(t)=x\'(t)={v}$. Решим уравнение $${v}={p["v"]}.$$ '
                   f'Подходит положительный корень $t={tex_num(self.solve(p))}$.')
        return Rendered(cond, sol + f'\n\n**Ответ:** {dec(self.solve(p))}.')

    def sample(self, rng):
        a = Fraction(rng.choice([1, 1, -1, 2])) if rng.random() < 0.3 else Fraction(0)
        b = Fraction(rng.choice([1, 2, 3, -1, Fraction(1, 2), -2]))
        c = Fraction(rng.randint(-12, 12))
        d = Fraction(rng.randint(-20, 20))
        if a == 0 and b < 0:
            b = -b
        ask = rng.choice(['v', 't'])
        if ask == 'v':
            return {'coefs': [a, b, c, d], 'ask': ask, 't': rng.randint(1, 8)}
        t = rng.randint(1, 9)
        v = 3 * a * t * t + 2 * b * t + c
        return {'coefs': [a, b, c, d], 'ask': ask, 'v': v}

    def nice(self, x):
        return frac(x).denominator == 1 and x > 0


class TangentParabola(Template):
    """Прямая y = kx + m касается параболы y = ax² + bx + c: найти c (или абсциссу точки касания)"""
    number, topic, code, difficulty = 8, 'Касательная и производная', '8.tangent-line', 2

    def solve(self, p):
        a, b, k, m, x0 = p['a'], p['b'], p['k'], p['m'], p['x0']
        if p['ask'] == 'x0':
            return x0
        # касание: 2a x0 + b = k, a x0² + b x0 + c = k x0 + m
        return k * x0 + m - a * x0 * x0 - b * x0

    def _c(self, p):
        a, b, k, m, x0 = p['a'], p['b'], p['k'], p['m'], p['x0']
        return k * x0 + m - a * x0 * x0 - b * x0

    def verify(self, p, ans):
        a, b, k, m = p['a'], p['b'], p['k'], p['m']
        c = self._c(p)
        # дискриминант уравнения ax² + (b−k)x + (c−m) = 0 равен нулю
        return (b - k) ** 2 - 4 * a * (c - m) == 0

    def render(self, p):
        a, b, k, m, x0 = p['a'], p['b'], p['k'], p['m'], p['x0']
        c = self._c(p)
        line = lin(k, m)
        if p['ask'] == 'c':
            cond = f'Прямая $y={line}$ является касательной к графику функции $y={poly([a, b, 0])}+c$. Найдите $c$.'
            sol = (f'В точке касания $x_0$ производная равна угловому коэффициенту прямой: $$y\'={poly([2 * a, b])}={tex_num(k)}'
                   f'\\ \\Rightarrow\\ x_0={tex_num(x0)}.$$ Значения функций в точке касания совпадают: '
                   f'$${tex_num(a)}\\cdot {par(x0)}^2{signed(b)}\\cdot {par(x0)}+c={tex_num(k)}\\cdot {par(x0)}{signed(m)},$$ откуда $c={tex_num(c)}$.')
        else:
            cond = f'Прямая $y={line}$ является касательной к графику функции $y={poly([a, b, c])}$. Найдите абсциссу точки касания.'
            sol = (f'В точке касания производная функции равна угловому коэффициенту касательной: $${poly([2 * a, b])}={tex_num(k)},\\quad x_0={tex_num(x0)}.$$ '
                   f'Проверка: $y({tex_num(x0)})={tex_num(a * x0 * x0 + b * x0 + c)}$ и на прямой ${tex_num(k * x0 + m)}$ — совпадает.')
        return Rendered(cond.replace('1x', 'x'), sol + f'\n\n**Ответ:** {dec(self.solve(p))}.')

    def sample(self, rng):
        a = Fraction(rng.choice([1, 1, 2, 3, -1, -2]))
        x0 = Fraction(rng.randint(-6, 6))
        b = Fraction(rng.randint(-10, 10))
        k = 2 * a * x0 + b
        m = Fraction(rng.randint(-12, 12))
        if k == 0:
            return None
        return {'a': a, 'b': b, 'k': k, 'm': m, 'x0': x0, 'ask': rng.choice(['c', 'x0'])}

    def nice(self, x):
        return frac(x).denominator == 1 and x != 0


TEMPLATES = [Tangent(), MarkedPoints(), DerivativeGraph(), FunctionGraphRoots(), FourPoints()]
EXTRA = [(Tangent(), 20), (MarkedPoints(), 20), (DerivativeGraph(), 20), (FunctionGraphRoots(), 8),
         (MotionVelocity(), 12), (TangentParabola(), 12)]
