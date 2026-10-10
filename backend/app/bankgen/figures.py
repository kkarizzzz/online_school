"""
Наши чертежи к заданиям (SVG). Фигура задаётся в своих координатах, Figure сама
масштабирует её в рамку, ставит подписи вершин снаружи и рисует отметки углов.

Стиль как в ЕГЭ: чёрные линии, курсивные подписи вершин, без цвета. Фон прозрачный: в тёмной теме
фронтенд инвертирует картинку, и линии становятся белыми.
"""
import math
import re
from dataclasses import dataclass, field

FONT = "font-family='Times New Roman, serif'"
Point = tuple[float, float]
DISPLAY = 1.35            # во сколько раз картинка показывается крупнее своих координат (вектор — без потери чёткости)


def _fmt(x: float) -> str:
    return f'{x:.1f}'.rstrip('0').rstrip('.')


@dataclass
class Figure:
    width: int = 320          # максимальная ширина в px
    height: int = 240
    pad: int = 28
    items: list = field(default_factory=list)
    points: dict[str, Point] = field(default_factory=dict)
    extra_bounds: list[Point] = field(default_factory=list)

    # --- построение (в координатах задачи, ось y вверх)
    def point(self, name: str, p: Point) -> Point:
        self.points[name] = p
        return p

    def polygon(self, *names: str, dashed: bool = False):
        self.items.append(('poly', [self.points[n] for n in names], dashed))

    def segment(self, a, b, dashed: bool = False, width: float = 1.6):
        pa = self.points[a] if isinstance(a, str) else a
        pb = self.points[b] if isinstance(b, str) else b
        self.items.append(('seg', pa, pb, dashed, width))

    def circle(self, c, r: float, dashed: bool = False):
        pc = self.points[c] if isinstance(c, str) else c
        self.items.append(('circle', pc, r, dashed))
        self.extra_bounds += [(pc[0] - r, pc[1] - r), (pc[0] + r, pc[1] + r)]

    def dot(self, name: str):
        self.items.append(('dot', self.points[name]))

    def label(self, name: str, text: str | None = None, at: Point | None = None, away_from: Point | None = None):
        """Подпись вершины: по умолчанию — снаружи от центра всех точек"""
        self.items.append(('label', name, text or name, at, away_from))

    def text(self, p: Point, s: str, size: int = 15, italic: bool = False):
        self.items.append(('text', p, s, size, italic))

    def right_angle(self, vertex: str, a: str, b: str, size: float = 0.12):
        self.items.append(('right', vertex, a, b, size))

    def angle_arc(self, vertex: str, a: str, b: str, r: float = 0.18, count: int = 1):
        self.items.append(('arc', vertex, a, b, r, count))

    def tick(self, a: str, b: str, count: int = 1):
        """Чёрточки равенства отрезков"""
        self.items.append(('tick', a, b, count))

    def ellipse(self, c, rx: float, ry: float, back: str = 'dashed', front: str = 'solid'):
        """Горизонтальный эллипс (основание тела вращения): дальняя половина пунктиром"""
        pc = self.points[c] if isinstance(c, str) else c
        self.items.append(('ellipse', pc, rx, ry, back, front))
        self.extra_bounds += [(pc[0] - rx, pc[1] - ry), (pc[0] + rx, pc[1] + ry)]

    def grid(self, x0: int, y0: int, x1: int, y1: int):
        self.items.insert(0, ('grid', x0, y0, x1, y1))
        self.extra_bounds += [(x0, y0), (x1, y1)]

    def curve(self, pts: list[Point], width: float = 2.2, dashed: bool = False, ylim: tuple[float, float] | None = None):
        """Ломаная по точкам; с ylim — обрезаем по высоте, разрывая линию, а не соединяя куски"""
        if ylim is None:
            self.items.append(('curve', pts, width, dashed))
            return
        run: list[Point] = []
        for p in pts:
            if ylim[0] <= p[1] <= ylim[1]:
                run.append(p)
            else:
                if len(run) > 1:
                    self.items.append(('curve', run, width, dashed))
                run = []
        if len(run) > 1:
            self.items.append(('curve', run, width, dashed))

    def hollow(self, p: Point):
        """Выколотая точка на конце графика"""
        self.items.append(('hollow', p))

    def arrow(self, a: Point, b: Point, name: str | None = None):
        self.items.append(('arrow', a, b, name))
        self.extra_bounds += [a, b]

    # --- вывод
    def _place_labels(self, tr, scale: float, W: float, H: float, center: Point) -> dict[int, tuple[float, float]]:
        """
        Подписи вершин: для каждой перебираем направления вокруг точки и берём то, где подпись дальше всего
        от линий, окружностей, других точек и уже поставленных подписей; при равенстве — наружу от центра фигуры
        """
        segs: list[tuple[tuple[float, float], tuple[float, float]]] = []
        circles: list[tuple[tuple[float, float], float]] = []
        for item in self.items:
            kind = item[0]
            if kind == 'poly':
                ps = [tr(q) for q in item[1]]
                segs += list(zip(ps, ps[1:] + ps[:1]))
            elif kind == 'seg':
                segs.append((tr(item[1]), tr(item[2])))
            elif kind == 'curve':
                ps = [tr(q) for q in item[1]][::4] + [tr(item[1][-1])]
                segs += list(zip(ps, ps[1:]))
            elif kind == 'circle':
                circles.append((tr(item[1]), item[2] * scale))
        dots = [tr(q) for q in self.points.values()]
        done: list[tuple[float, float, float]] = []      # центр подписи и её «радиус»
        out: dict[int, tuple[float, float]] = {}
        for item in self.items:
            if item[0] != 'label' or item[3] is not None:
                continue
            _, name, text, _, away = item
            p = self.points[name]
            q0 = tr(p)
            ox, oy = away if away is not None else center
            base = math.atan2(-(p[1] - oy), p[0] - ox)           # «наружу» в экранных координатах
            r_lab = 6 + 3.5 * len(re.sub(r'<[^>]+>', '', text))
            best = None
            for k in range(24):
                ang = base + k * math.pi / 12
                for dist in (15, 20):
                    q = (q0[0] + dist * math.cos(ang), q0[1] + dist * math.sin(ang))
                    clear = 40.0
                    for a, b in segs:
                        clear = min(clear, _pdist(q, a, b) - r_lab + 3)
                    for c, r in circles:
                        clear = min(clear, abs(math.dist(q, c) - r) - r_lab + 3)
                    for d in dots:
                        if d != q0:
                            clear = min(clear, math.dist(q, d) - r_lab)
                    for x, y, r in done:
                        clear = min(clear, math.dist(q, (x, y)) - r - r_lab)
                    if not (r_lab < q[0] < W - r_lab and 12 < q[1] < H - 4):
                        clear -= 15
                    score = clear + 3 * math.cos(ang - base) - (dist - 15) * 0.2
                    if best is None or score > best[0]:
                        best = (score, q)
            out[id(item)] = best[1]
            done.append((best[1][0], best[1][1], r_lab))
        return out

    def svg(self) -> str:
        pts = list(self.points.values()) + self.extra_bounds
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
        w, h = max(maxx - minx, 1e-6), max(maxy - miny, 1e-6)
        scale = min((self.width - 2 * self.pad) / w, (self.height - 2 * self.pad) / h)
        W = w * scale + 2 * self.pad
        H = h * scale + 2 * self.pad
        self._unit = scale * max(w, h)

        def tr(p: Point) -> tuple[float, float]:
            return (self.pad + (p[0] - minx) * scale, self.pad + (maxy - p[1]) * scale)

        cx = sum(p[0] for p in self.points.values()) / max(len(self.points), 1)
        cy = sum(p[1] for p in self.points.values()) / max(len(self.points), 1)

        out = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {_fmt(W)} {_fmt(H)}' "
               f"width='{_fmt(W * DISPLAY)}' height='{_fmt(H * DISPLAY)}'>",
               "<defs><marker id='ar' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' "
               "orient='auto-start-reverse'><path d='M0,0 L10,5 L0,10 z' fill='black'/></marker></defs>"]
        stroke = "stroke='black' fill='none'"
        placed = self._place_labels(tr, scale, W, H, (cx, cy))
        for item in self.items:
            kind = item[0]
            if kind == 'grid':
                _, x0, y0, x1, y1 = item
                for x in range(x0, x1 + 1):
                    a, b = tr((x, y0)), tr((x, y1))
                    out.append(f"<line x1='{_fmt(a[0])}' y1='{_fmt(a[1])}' x2='{_fmt(b[0])}' y2='{_fmt(b[1])}' stroke='#bbb' stroke-width='0.8'/>")
                for y in range(y0, y1 + 1):
                    a, b = tr((x0, y)), tr((x1, y))
                    out.append(f"<line x1='{_fmt(a[0])}' y1='{_fmt(a[1])}' x2='{_fmt(b[0])}' y2='{_fmt(b[1])}' stroke='#bbb' stroke-width='0.8'/>")
            elif kind == 'poly':
                _, ps, dashed = item
                d = ' '.join(f'{_fmt(x)},{_fmt(y)}' for x, y in map(tr, ps))
                out.append(f"<polygon points='{d}' {stroke} stroke-width='1.8'{_dash(dashed)}/>")
            elif kind == 'fill':
                d = ' '.join(f'{_fmt(x)},{_fmt(y)}' for x, y in map(tr, item[1]))
                out.append(f"<polygon points='{d}' fill='#d9d9d9' fill-opacity='0.7' stroke='none'/>")
            elif kind == 'seg':
                _, a, b, dashed, width = item
                a, b = tr(a), tr(b)
                out.append(f"<line x1='{_fmt(a[0])}' y1='{_fmt(a[1])}' x2='{_fmt(b[0])}' y2='{_fmt(b[1])}' "
                           f"{stroke} stroke-width='{width}'{_dash(dashed)}/>")
            elif kind == 'circle':
                _, c, r, dashed = item
                c = tr(c)
                out.append(f"<circle cx='{_fmt(c[0])}' cy='{_fmt(c[1])}' r='{_fmt(r * scale)}' {stroke} stroke-width='1.8'{_dash(dashed)}/>")
            elif kind == 'ellipse':
                _, c, rx, ry, back, front = item
                c = tr(c)
                rx, ry = rx * scale, ry * scale
                left, right = f'{_fmt(c[0] - rx)},{_fmt(c[1])}', f'{_fmt(c[0] + rx)},{_fmt(c[1])}'
                for half, style in (('back', back), ('front', front)):
                    if style == 'none':
                        continue
                    sweep = 1 if half == 'back' else 0
                    out.append(f"<path d='M{left} A{_fmt(rx)},{_fmt(ry)} 0 0 {sweep} {right}' {stroke} stroke-width='1.6'"
                               f"{_dash(style == 'dashed')}/>")
            elif kind == 'axisarrow':
                _, p, direction = item
                q = tr(p)
                if direction == 'x':
                    out.append(f"<path d='M{_fmt(q[0])},{_fmt(q[1])} l-9,-4 l0,8 z' fill='black'/>")
                else:
                    out.append(f"<path d='M{_fmt(q[0])},{_fmt(q[1])} l-4,9 l8,0 z' fill='black'/>")
            elif kind == 'curve':
                _, ps, width, dashed = item
                d = ' '.join(f'{_fmt(x)},{_fmt(y)}' for x, y in map(tr, ps))
                out.append(f"<polyline points='{d}' {stroke} stroke-width='{width}' stroke-linejoin='round'{_dash(dashed)}/>")
            elif kind == 'hollow':
                c = tr(item[1])
                out.append(f"<circle cx='{_fmt(c[0])}' cy='{_fmt(c[1])}' r='3.5' fill='white' stroke='black' stroke-width='1.5'/>")
            elif kind == 'dot':
                c = tr(item[1])
                out.append(f"<circle cx='{_fmt(c[0])}' cy='{_fmt(c[1])}' r='2.6' fill='black'/>")
            elif kind == 'label':
                _, name, text, at, away = item
                p = self.points[name]
                q = tr(at) if at is not None else placed[id(item)]
                out.append(f"<text x='{_fmt(q[0])}' y='{_fmt(q[1] + 6)}' font-size='18' font-style='italic' "
                           f"text-anchor='middle' {FONT}>{text}</text>")
            elif kind == 'text':
                _, p, s, size, italic = item
                q = tr(p)
                st = " font-style='italic'" if italic else ''
                out.append(f"<text x='{_fmt(q[0])}' y='{_fmt(q[1] + size / 3)}' font-size='{size}'{st} "
                           f"text-anchor='middle' {FONT}>{s}</text>")
            elif kind == 'right':
                _, v, a, b, size = item
                pv, pa, pb = (tr(self.points[k]) for k in (v, a, b))
                s = 12
                ua, ub = _unit(pv, pa), _unit(pv, pb)
                p1 = (pv[0] + ua[0] * s, pv[1] + ua[1] * s)
                p2 = (p1[0] + ub[0] * s, p1[1] + ub[1] * s)
                p3 = (pv[0] + ub[0] * s, pv[1] + ub[1] * s)
                out.append(f"<polyline points='{_fmt(p1[0])},{_fmt(p1[1])} {_fmt(p2[0])},{_fmt(p2[1])} "
                           f"{_fmt(p3[0])},{_fmt(p3[1])}' {stroke} stroke-width='1.2'/>")
            elif kind == 'arc':
                _, v, a, b, r, count = item
                pv, pa, pb = (tr(self.points[k]) for k in (v, a, b))
                for i in range(count):
                    rr = 16 + 5 * i
                    ua, ub = _unit(pv, pa), _unit(pv, pb)
                    s = (pv[0] + ua[0] * rr, pv[1] + ua[1] * rr)
                    e = (pv[0] + ub[0] * rr, pv[1] + ub[1] * rr)
                    cross = ua[0] * ub[1] - ua[1] * ub[0]
                    sweep = 1 if cross > 0 else 0
                    out.append(f"<path d='M{_fmt(s[0])},{_fmt(s[1])} A{rr},{rr} 0 0 {sweep} {_fmt(e[0])},{_fmt(e[1])}' "
                               f"{stroke} stroke-width='1.2'/>")
            elif kind == 'tick':
                _, a, b, count = item
                pa, pb = tr(self.points[a]), tr(self.points[b])
                mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
                ux, uy = _unit(pa, pb)
                nx, ny = -uy, ux
                for i in range(count):
                    off = (i - (count - 1) / 2) * 4
                    x, y = mx + ux * off, my + uy * off
                    out.append(f"<line x1='{_fmt(x - nx * 6)}' y1='{_fmt(y - ny * 6)}' x2='{_fmt(x + nx * 6)}' "
                               f"y2='{_fmt(y + ny * 6)}' stroke='black' stroke-width='1.4'/>")
            elif kind == 'arrow':
                _, a, b, name = item
                pa, pb = tr(a), tr(b)
                out.append(f"<line x1='{_fmt(pa[0])}' y1='{_fmt(pa[1])}' x2='{_fmt(pb[0])}' y2='{_fmt(pb[1])}' "
                           f"stroke='black' stroke-width='2' marker-end='url(#ar)'/>")
                if name:
                    mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
                    ux, uy = _unit(pa, pb)
                    tx, ty = mx - uy * 14, my + ux * 14 + 6
                    out.append(f"<text x='{_fmt(tx)}' y='{_fmt(ty)}' font-size='18' "
                               f"font-style='italic' font-weight='bold' text-anchor='middle' {FONT}>{name}</text>")
                    # стрелка над буквой — обозначение вектора
                    out.append(f"<line x1='{_fmt(tx - 6)}' y1='{_fmt(ty - 16)}' x2='{_fmt(tx + 7)}' y2='{_fmt(ty - 16)}' "
                               f"stroke='black' stroke-width='1.1' marker-end='url(#ar)'/>")
        out.append('</svg>')
        return '\n'.join(out)


def _pdist(p, a, b) -> float:
    """Расстояние от точки до отрезка"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1e-9)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def _dash(dashed: bool) -> str:
    return " stroke-dasharray='5 4'" if dashed else ''


def _unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1
    return dx / n, dy / n


# ---------------------------------------------------------------------------
# Геометрия для построений
# ---------------------------------------------------------------------------

def polar(c: Point, r: float, deg: float) -> Point:
    return (c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg)))


def mid(a: Point, b: Point) -> Point:
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def lerp(a: Point, b: Point, t: float) -> Point:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def foot(p: Point, a: Point, b: Point) -> Point:
    """Основание перпендикуляра из p на прямую ab"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)
    return (a[0] + t * dx, a[1] + t * dy)


def bisector_foot(v: Point, a: Point, b: Point) -> Point:
    """Точка на ab, куда приходит биссектриса угла v"""
    la, lb = math.dist(v, a), math.dist(v, b)
    return lerp(a, b, la / (la + lb))


def hermite(knots: list[tuple[float, float, float]]):
    """Кубический сплайн Эрмита по узлам (x, y, y'). Между узлами с нулевыми наклонами функция монотонна"""
    knots = sorted(knots)

    def f(x: float) -> float:
        for (x0, y0, m0), (x1, y1, m1) in zip(knots, knots[1:]):
            if x0 <= x <= x1:
                h = x1 - x0
                t = (x - x0) / h
                h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
                h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
                return h00 * y0 + h10 * h * m0 + h01 * y1 + h11 * h * m1
        raise ValueError(f'x={x} вне графика')
    return f


def sample_curve(f, x0: float, x1: float, n: int = 240) -> list[Point]:
    return [(x0 + (x1 - x0) * i / n, f(x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


def axes(fig: 'Figure', x0: int, x1: int, y0: int, y1: int, ticks: bool = True, y_name: str = 'y'):
    """Клетчатая сетка, оси со стрелками, подписи x, y, 0 и единичных отрезков"""
    fig.grid(x0, y0, x1, y1)
    fig.items.append(('seg', (x0, 0), (x1 + 0.6, 0), False, 1.4))
    fig.items.append(('seg', (0, y0), (0, y1 + 0.6), False, 1.4))
    fig.items.append(('axisarrow', (x1 + 0.6, 0), 'x'))
    fig.items.append(('axisarrow', (0, y1 + 0.6), 'y'))
    fig.extra_bounds += [(x1 + 0.9, 0), (0, y1 + 0.9)]
    fig.text((x1 + 0.55, -0.5), 'x', 16, italic=True)
    fig.text((-0.45, y1 + 0.55), y_name, 16, italic=True)
    if ticks:
        fig.text((-0.35, -0.45), '0', 14)
        fig.text((1, -0.45), '1', 14)
        fig.text((-0.35, 1), '1', 14)


def proj(x: float, y: float, z: float, k: float = 0.45, deg: float = 35) -> Point:
    """Косоугольная проекция: x — вправо, y — вглубь (укорачивается и уходит вверх-вправо), z — вверх"""
    a = math.radians(deg)
    return (x + k * y * math.cos(a), z + k * y * math.sin(a))


def box(fig: 'Figure', a: float, b: float, c: float, names: str = 'ABCD', top_suffix: str = '_1',
        labels: bool = True) -> dict[str, Point]:
    """Прямоугольный параллелепипед ABCDA₁B₁C₁D₁: AB вдоль x, AD вглубь, AA₁ вверх. Невидимые рёбра пунктиром"""
    A, B, C, D = names
    base = {A: (0, 0, 0), B: (a, 0, 0), C: (a, b, 0), D: (0, b, 0)}
    pts = {}
    for n, (x, y, z) in base.items():
        pts[n] = fig.point(n, proj(x, y, z))
        pts[n + '1'] = fig.point(n + '1', proj(x, y, z + c))
    solid = [(A, B), (B, C), (A + '1', B + '1'), (B + '1', C + '1'), (C + '1', D + '1'), (D + '1', A + '1'),
             (A, A + '1'), (B, B + '1'), (C, C + '1')]
    hidden = [(C, D), (D, A), (D, D + '1')]
    for u, v in solid:
        fig.segment(u, v)
    for u, v in hidden:
        fig.segment(u, v, dashed=True)
    if labels:
        center = proj(a / 2, b / 2, c / 2)
        for n in pts:
            text = n if len(n) == 1 else f"{n[0]}<tspan baseline-shift='sub' font-size='12'>1</tspan>"
            fig.label(n, text=text, away_from=center)
    return pts


def tri_from_angles(alpha: float, beta: float, base: float = 1.0) -> tuple[Point, Point, Point]:
    """Треугольник ABC: AB на оси x, углы при A и B в градусах"""
    A, B = (0.0, 0.0), (base, 0.0)
    gamma = 180 - alpha - beta
    ac = base * math.sin(math.radians(beta)) / math.sin(math.radians(gamma))
    C = polar(A, ac, alpha)
    return A, B, C
