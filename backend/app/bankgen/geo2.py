"""
Планиметрия в координатах — независимая проверка ответов № 17 и чертежи.

Численно (float): ответ в решении пишется точной формулой, а здесь он получается заново из координат.
"""
import math

from app.bankgen.figures import Figure

P = tuple[float, float]


def add(a, b) -> P:
    return (a[0] + b[0], a[1] + b[1])


def sub(a, b) -> P:
    return (a[0] - b[0], a[1] - b[1])


def mul(a, k) -> P:
    return (a[0] * k, a[1] * k)


def dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1]


def cross(a, b) -> float:
    return a[0] * b[1] - a[1] * b[0]


def norm(a) -> float:
    return math.hypot(a[0], a[1])


def dist(a, b) -> float:
    return norm(sub(a, b))


def lerp(a, b, t) -> P:
    return add(a, mul(sub(b, a), t))


def ratio(a, b, m, n) -> P:
    """X на AB, AX : XB = m : n"""
    return lerp(a, b, m / (m + n))


def mid(a, b) -> P:
    return lerp(a, b, 0.5)


def polar(r, deg, c=(0.0, 0.0)) -> P:
    return (c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg)))


def rot(v, deg) -> P:
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def intersect(a, b, c, d) -> P:
    """Точка пересечения прямых AB и CD"""
    r, s = sub(b, a), sub(d, c)
    den = cross(r, s)
    if abs(den) < 1e-12:
        raise ValueError('прямые параллельны')
    t = cross(sub(c, a), s) / den
    return add(a, mul(r, t))


def foot(p, a, b) -> P:
    """Основание перпендикуляра из P на прямую AB"""
    d = sub(b, a)
    return add(a, mul(d, dot(sub(p, a), d) / dot(d, d)))


def dist_line(p, a, b) -> float:
    return abs(cross(sub(b, a), sub(p, a))) / dist(a, b)


def angle(a, o, b) -> float:
    """∠AOB в градусах"""
    u, v = sub(a, o), sub(b, o)
    return math.degrees(math.acos(max(-1.0, min(1.0, dot(u, v) / norm(u) / norm(v)))))


def area(*ps) -> float:
    s = 0.0
    for a, b in zip(ps, ps[1:] + ps[:1]):
        s += cross(a, b)
    return abs(s) / 2


def circumcenter(a, b, c) -> P:
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    ux = ((a[0] ** 2 + a[1] ** 2) * (b[1] - c[1]) + (b[0] ** 2 + b[1] ** 2) * (c[1] - a[1]) + (c[0] ** 2 + c[1] ** 2) * (a[1] - b[1])) / d
    uy = ((a[0] ** 2 + a[1] ** 2) * (c[0] - b[0]) + (b[0] ** 2 + b[1] ** 2) * (a[0] - c[0]) + (c[0] ** 2 + c[1] ** 2) * (b[0] - a[0])) / d
    return (ux, uy)


def circumradius(a, b, c) -> float:
    return dist(circumcenter(a, b, c), a)


def incenter(a, b, c) -> P:
    la, lb, lc = dist(b, c), dist(a, c), dist(a, b)
    s = la + lb + lc
    return ((la * a[0] + lb * b[0] + lc * c[0]) / s, (la * a[1] + lb * b[1] + lc * c[1]) / s)


def inradius(a, b, c) -> float:
    return 2 * area(a, b, c) / (dist(a, b) + dist(b, c) + dist(c, a))


def orthocenter(a, b, c) -> P:
    return intersect(a, foot(a, b, c), b, foot(b, a, c))


def line_circle(a, b, o, r) -> list[P]:
    """Точки пересечения прямой AB с окружностью (O, r)"""
    d = sub(b, a)
    f = sub(a, o)
    A, B, C = dot(d, d), 2 * dot(f, d), dot(f, f) - r * r
    disc = B * B - 4 * A * C
    if disc < -1e-12:
        return []
    disc = math.sqrt(max(disc, 0.0))
    return [add(a, mul(d, (-B - disc) / (2 * A))), add(a, mul(d, (-B + disc) / (2 * A)))]


def second(a, b, o, r, known) -> P:
    """Вторая (кроме known) точка пересечения прямой AB с окружностью"""
    pts = line_circle(a, b, o, r)
    return max(pts, key=lambda q: dist(q, known))


def concyclic(*ps) -> bool:
    o = circumcenter(*ps[:3])
    r = dist(o, ps[0])
    return all(abs(dist(o, q) - r) < 1e-7 * max(1, r) for q in ps)


def parallel(u, v) -> bool:
    return abs(cross(u, v)) < 1e-9 * max(1.0, norm(u) * norm(v))


def perpendicular(u, v) -> bool:
    return abs(dot(u, v)) < 1e-9 * max(1.0, norm(u) * norm(v))


def close(a, b, eps=1e-7) -> bool:
    return abs(a - b) <= eps * max(1.0, abs(a), abs(b))


def triangle(a, b, c) -> tuple[P, P, P]:
    """Треугольник по сторонам a = BC, b = CA, c = AB: B в начале, C на оси x, A сверху"""
    B, C = (0.0, 0.0), (a, 0.0)
    x = (a * a + c * c - b * b) / (2 * a)
    return (x, math.sqrt(max(c * c - x * x, 0.0))), B, C


def triangle_angles(B_deg, C_deg, a=1.0) -> tuple[P, P, P]:
    """Треугольник по углам B, C и стороне BC = a"""
    A_deg = 180 - B_deg - C_deg
    c = a * math.sin(math.radians(C_deg)) / math.sin(math.radians(A_deg))
    return polar(c, B_deg), (0.0, 0.0), (a, 0.0)


# ---------------------------------------------------------------------------
# Чертёж
# ---------------------------------------------------------------------------

SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')


def pretty(name: str) -> str:
    return name[0] + name[1:].translate(SUB)


LAST_SCORE = 1.0   # читаемость последнего чертежа draw() — по ней Solved.render решает, перерисовать ли «удобными» числами


def _seg_dist(p: P, a: P, b: P) -> float:
    ab = sub(b, a)
    t = max(0.0, min(1.0, dot(sub(p, a), ab) / (dot(ab, ab) or 1e-12)))
    return math.dist(p, add(a, mul(ab, t)))


def readability(points: dict[str, P], polygons=(), segments=(), circles=(), labels=None) -> float:
    """
    Насколько чертёж читается, в долях размера рисунка (больше — лучше):
    наименьшее из расстояний между подписанными точками и от точки до отрезка, на котором она не лежит.
    Окружности входят в размер рисунка: огромная окружность вокруг маленького треугольника даёт низкую оценку.
    """
    named = {n: q for n, q in points.items() if not n.startswith('_') and (labels is None or n in labels)}
    xs = [q[0] for q in points.values()]
    ys = [q[1] for q in points.values()]
    for c, r in circles:
        c = points[c] if isinstance(c, str) else c
        xs += [c[0] - r, c[0] + r]
        ys += [c[1] - r, c[1] + r]
    size = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    pos = lambda v: points[v] if isinstance(v, str) else v  # noqa: E731
    segs = [(pos(a), pos(b)) for a, b in segments]
    for poly in polygons:
        segs += [(points[a], points[b]) for a, b in zip(poly, poly[1:] + poly[:1])]
    worst = 1.0
    qs = list(named.values())
    for i, a in enumerate(qs):
        for b in qs[i + 1:]:
            worst = min(worst, math.dist(a, b) / size)
        for u, v in segs:
            d = _seg_dist(a, u, v)
            if d > 1e-6 * size and math.dist(a, u) > 1e-6 * size and math.dist(a, v) > 1e-6 * size:
                worst = min(worst, d / size)
    return worst


def draw(points: dict[str, P], *, polygons: list[list[str]] = (), segments: list = (), circles: list = (),
         dashed: list = (), right: list = (), dots: list[str] | None = None, labels: list[str] | None = None,
         width: int = 340, height: int = 260) -> str:
    """
    polygons — замкнутые ломаные по именам, segments — отрезки (имя/точка), dashed — пунктирные отрезки,
    circles — (центр (имя/точка), радиус), right — прямые углы (вершина, a, b).
    """
    global LAST_SCORE
    LAST_SCORE = readability(points, polygons, segments, circles, labels)
    fig = Figure(width=width, height=height)
    for n, p in points.items():
        fig.point(n, p)
    for poly in polygons:
        fig.polygon(*poly)
    for a, b in segments:
        fig.segment(a, b)
    for a, b in dashed:
        fig.segment(a, b, dashed=True)
    for c, r in circles:
        fig.circle(c, r)
    for v, a, b in right:
        fig.right_angle(v, a, b)
    cx = sum(p[0] for p in points.values()) / len(points)
    cy = sum(p[1] for p in points.values()) / len(points)
    for n in (labels if labels is not None else [k for k in points if not k.startswith('_')]):
        fig.label(n, pretty(n), away_from=(cx, cy))
    for n in (dots or []):
        fig.dot(n)
    return fig.svg()
