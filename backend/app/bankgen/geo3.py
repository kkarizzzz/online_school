"""
Стереометрия в координатах — независимая проверка ответов № 14 и чертежи многогранников.

Всё численно (float): ответ задания пишется точной формулой в решении, а здесь тот же ответ
получается «в лоб» из координат вершин — сечение, объёмы частей, расстояния, углы.
"""
import math
from itertools import combinations

from app.bankgen.figures import Figure

Vec = tuple[float, float, float]
EPS = 1e-9


# ---------------------------------------------------------------------------
# Векторы
# ---------------------------------------------------------------------------

def add(a, b) -> Vec:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, k: float) -> Vec:
    return (a[0] * k, a[1] * k, a[2] * k)


def dot(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b) -> Vec:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a) -> float:
    return math.sqrt(dot(a, a))


def unit(a) -> Vec:
    return mul(a, 1 / norm(a))


def lerp(a, b, t: float) -> Vec:
    """Точка, делящая AB в отношении t : (1 − t) от A"""
    return add(a, mul(sub(b, a), t))


def ratio(a, b, m: float, n: float) -> Vec:
    """Точка X на AB с AX : XB = m : n"""
    return lerp(a, b, m / (m + n))


def mid(a, b) -> Vec:
    return lerp(a, b, 0.5)


def centroid(*ps) -> Vec:
    return tuple(sum(p[i] for p in ps) / len(ps) for i in range(3))


def dist(a, b) -> float:
    return norm(sub(a, b))


# ---------------------------------------------------------------------------
# Плоскости, прямые
# ---------------------------------------------------------------------------

Plane = tuple[Vec, float]   # (n, d): n·X = d


def plane(a, b, c) -> Plane:
    n = cross(sub(b, a), sub(c, a))
    if norm(n) < EPS:
        raise ValueError('точки на одной прямой')
    n = unit(n)
    return n, dot(n, a)


def plane_nd(point, normal) -> Plane:
    n = unit(normal)
    return n, dot(n, point)


def plane_pv(point, u, v) -> Plane:
    """Плоскость через точку параллельно векторам u, v"""
    return plane_nd(point, cross(u, v))


def side(pl: Plane, p) -> float:
    return dot(pl[0], p) - pl[1]


def on_plane(pl: Plane, p) -> bool:
    return abs(side(pl, p)) < 1e-7


def dist_point_plane(p, pl: Plane) -> float:
    return abs(side(pl, p))


def dist_point_line(p, a, b) -> float:
    return norm(cross(sub(p, a), sub(b, a))) / dist(a, b)


def dist_lines(a, b, c, d) -> float:
    """Расстояние между скрещивающимися прямыми AB и CD"""
    n = cross(sub(b, a), sub(d, c))
    if norm(n) < EPS:
        return dist_point_line(c, a, b)
    return abs(dot(sub(c, a), n)) / norm(n)


def line_plane(a, b, pl: Plane) -> Vec:
    """Точка пересечения прямой AB с плоскостью"""
    sa, sb = side(pl, a), side(pl, b)
    if abs(sa - sb) < EPS:
        raise ValueError('прямая параллельна плоскости')
    return lerp(a, b, sa / (sa - sb))


def angle_lines(u, v) -> float:
    """Угол между прямыми с направлениями u, v (радианы, 0..π/2)"""
    return math.acos(min(1.0, abs(dot(u, v)) / norm(u) / norm(v)))


def angle_line_plane(u, pl: Plane) -> float:
    return math.asin(min(1.0, abs(dot(u, pl[0])) / norm(u)))


def angle_planes(p1: Plane, p2: Plane) -> float:
    return math.acos(min(1.0, abs(dot(p1[0], p2[0]))))


def parallel(u, v) -> bool:
    return norm(cross(unit(u), unit(v))) < 1e-7


def perpendicular(u, v) -> bool:
    return abs(dot(unit(u), unit(v))) < 1e-7


# ---------------------------------------------------------------------------
# Выпуклые многогранники: грани, сечение, объёмы
# ---------------------------------------------------------------------------

def hull_faces(points: list) -> list[tuple[Plane, list[int]]]:
    """Грани выпуклой оболочки: (внешняя плоскость, индексы вершин грани в порядке обхода)"""
    faces, seen = [], []
    for i, j, k in combinations(range(len(points)), 3):
        try:
            n, d = plane(points[i], points[j], points[k])
        except ValueError:
            continue
        s = [dot(n, p) - d for p in points]
        if all(v <= 1e-7 for v in s):
            pl = (n, d)
        elif all(v >= -1e-7 for v in s):
            pl = (mul(n, -1), -d)
        else:
            continue
        if any(norm(sub(pl[0], q[0])) < 1e-7 and abs(pl[1] - q[1]) < 1e-7 for q in seen):
            continue
        seen.append(pl)
        idx = [m for m, v in enumerate(s) if abs(v) < 1e-7]
        faces.append((pl, _order([points[m] for m in idx], pl[0], idx)))
    return faces


def _order(ps, normal, idx):
    c = centroid(*ps)
    e1 = unit(sub(ps[0], c)) if norm(sub(ps[0], c)) > EPS else unit(sub(ps[1], c))
    e2 = cross(normal, e1)
    ang = [math.atan2(dot(sub(p, c), e2), dot(sub(p, c), e1)) for p in ps]
    return [i for _, i in sorted(zip(ang, idx))]


def hull_edges(points: list) -> set[tuple[int, int]]:
    edges = set()
    for _, idx in hull_faces(points):
        for a, b in zip(idx, idx[1:] + idx[:1]):
            edges.add((min(a, b), max(a, b)))
    return edges


def volume(points: list) -> float:
    """Объём выпуклой оболочки точек"""
    c = centroid(*points)
    v = 0.0
    for pl, idx in hull_faces(points):
        area = polygon_area([points[i] for i in idx])
        v += area * dist_point_plane(c, pl) / 3
    return v


def polygon_area(ps: list) -> float:
    """Площадь плоского многоугольника (вершины в порядке обхода)"""
    s = (0.0, 0.0, 0.0)
    for a, b in zip(ps, ps[1:] + ps[:1]):
        s = add(s, cross(a, b))
    return norm(s) / 2


def section(points: list, pl: Plane) -> list[Vec]:
    """Сечение выпуклого многогранника плоскостью: вершины многоугольника по порядку"""
    res = []
    for i, j in hull_edges(points):
        a, b = points[i], points[j]
        sa, sb = side(pl, a), side(pl, b)
        if abs(sa) < 1e-7:
            res.append(a)
        if abs(sb) < 1e-7:
            res.append(b)
        if sa * sb < 0 and abs(sa) > 1e-7 and abs(sb) > 1e-7:
            res.append(lerp(a, b, sa / (sa - sb)))
    uniq = []
    for p in res:
        if all(dist(p, q) > 1e-7 for q in uniq):
            uniq.append(p)
    if len(uniq) < 3:
        return uniq
    order = _order(uniq, pl[0], list(range(len(uniq))))
    return [uniq[i] for i in order]


def split_volumes(points: list, pl: Plane) -> tuple[float, float]:
    """Объёмы частей, на которые плоскость делит выпуклый многогранник"""
    sec = section(points, pl)
    pos = [p for p in points if side(pl, p) > 1e-7] + sec
    neg = [p for p in points if side(pl, p) < -1e-7] + sec
    return (volume(pos) if len(pos) >= 4 else 0.0), (volume(neg) if len(neg) >= 4 else 0.0)


def close(a: float, b: float, eps: float = 1e-7) -> bool:
    return abs(a - b) <= eps * max(1.0, abs(a), abs(b))


def deg(rad: float) -> float:
    return math.degrees(rad)


# ---------------------------------------------------------------------------
# Чертёж
# ---------------------------------------------------------------------------

SUB = str.maketrans('0123456789', '₀₁₂₃₄₅₆₇₈₉')


def pretty(name: str) -> str:
    """A1 → A₁ для подписи"""
    return name[0] + name[1:].translate(SUB)


def view(p, azim: float = -62, elev: float = 18) -> tuple[float, float]:
    """Ортогональная проекция: поворот вокруг z на azim, наклон на elev (z — вверх)"""
    a, e = math.radians(azim), math.radians(elev)
    x, y, z = p
    x1 = x * math.cos(a) - y * math.sin(a)
    y1 = x * math.sin(a) + y * math.cos(a)
    return (-x1, z * math.cos(e) - y1 * math.sin(e))   # минус: правая тройка (вправо × вверх = на зрителя)


def _eye(azim: float, elev: float) -> Vec:
    """Направление на зрителя в исходных координатах"""
    a, e = math.radians(azim), math.radians(elev)
    # на экране ниже — ближе к зрителю: зритель смотрит сверху со стороны +y1, y1 = x sin a + y cos a
    return (math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e))


def draw_round(R: float, h: float, *, apex: bool = False, points: dict[str, Vec] | None = None,
               segments: list[tuple[str, str, bool]] = (), polygons: list[list[str]] = (), elev: float = 22,
               width: int = 340, height: int = 280) -> str:
    """
    Цилиндр (apex=False) или конус (apex=True) с осью z, основание — окружность радиуса R в плоскости z = 0.
    points — точки (на окружностях, на оси), segments — (a, b, пунктир), polygons — закрашенные многоугольники.
    """
    points = points or {}
    fig = Figure(width=width, height=height)
    e = math.radians(elev)
    v = lambda p: view(p, 0, elev)   # noqa: E731
    c0, c1 = v((0, 0, 0)), v((0, 0, h))
    fig.ellipse(c0, R, R * math.sin(e), back='dashed', front='solid')
    if apex:
        top = fig.point('_apex', c1)
        fig.segment((c0[0] - R, c0[1]), top)
        fig.segment((c0[0] + R, c0[1]), top)
    else:
        fig.ellipse(c1, R, R * math.sin(e), back='solid', front='solid')
        fig.segment((c0[0] - R, c0[1]), (c1[0] - R, c1[1]))
        fig.segment((c0[0] + R, c0[1]), (c1[0] + R, c1[1]))
    for n, p in points.items():
        fig.point(n, v(p))
    for poly in polygons:
        fig.items.append(('fill', [fig.points[n] for n in poly]))
    for a, b, dashed in segments:
        fig.segment(a, b, dashed=dashed, width=1.8)
    cen = v((0, 0, h / 2))
    for n in points:
        fig.dot(n)
        fig.label(n, pretty(n), away_from=cen)
    return fig.svg()


def draw(solid: dict[str, Vec], *, extra: dict[str, Vec] | None = None, segments: list[tuple[str, str]] = (),
         section_names: list[str] = (), labels: list[str] | None = None, azim: float = 160, elev: float = 18,
         width: int = 340, height: int = 280) -> str:
    """
    SVG выпуклого многогранника solid (имя → точка). Невидимые рёбра — пунктиром.
    extra — дополнительные точки (на рёбрах, внутри), segments — отрезки между любыми точками,
    section_names — вершины сечения (по порядку): закрашиваем и обводим.
    """
    extra = extra or {}
    names = list(solid)
    pts = [solid[n] for n in names]
    allp = {**solid, **extra}
    fig = Figure(width=width, height=height)
    # слишком вытянутое вверх тело на чертеже чуть сжимаем по вертикали (видимость считаем по настоящему)
    flat = [view(p, azim, elev) for p in allp.values()]
    w = max(q[0] for q in flat) - min(q[0] for q in flat)
    hgt = max(q[1] for q in flat) - min(q[1] for q in flat)
    kz = min(1.0, 1.4 * w / hgt) if hgt > 0 else 1.0
    for n, p in allp.items():
        fig.point(n, view((p[0], p[1], p[2] * kz), azim, elev))
    eye = _eye(azim, elev)
    faces = hull_faces(pts)
    visible_faces = [(pl, idx) for pl, idx in faces if dot(pl[0], eye) > 1e-6]

    def visible(p, q) -> bool:
        """Отрезок на поверхности виден, если лежит в видимой грани"""
        return any(on_plane(pl, p) and on_plane(pl, q) for pl, _ in visible_faces)

    if section_names:
        fig.items.append(('fill', [fig.points[n] for n in section_names]))
    for i, j in sorted(hull_edges(pts)):
        fig.segment(names[i], names[j], dashed=not visible(pts[i], pts[j]))
    ring = list(section_names) + list(section_names[:1])
    for a, b in list(zip(ring, ring[1:])) + list(segments):
        fig.segment(a, b, dashed=not visible(allp[a], allp[b]), width=1.8)
    c2 = view(centroid(*pts), azim, elev)
    for n in (labels if labels is not None else list(allp)):
        fig.label(n, pretty(n), away_from=c2)
    for n in extra:
        fig.dot(n)
    return fig.svg()
