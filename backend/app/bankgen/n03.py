"""№ 3. Стереометрия"""
import itertools
import math
import random
import re
from fractions import Fraction

from app.bankgen.core import Rendered, Template, dec, frac, tex_frac, tex_num
from app.bankgen.figures import Figure, box, proj


def hull_volume(points: list[tuple]) -> Fraction:
    """Объём выпуклой оболочки точек (точно, в Fraction)"""
    pts = [tuple(Fraction(c) for c in p) for p in points]
    n = len(pts)
    c = tuple(sum(p[i] for p in pts) / n for i in range(3))

    def sub(a, b):
        return tuple(x - y for x, y in zip(a, b))

    def cross(a, b):
        return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))

    faces = {}
    for i, j, k in itertools.combinations(range(n), 3):
        normal = cross(sub(pts[j], pts[i]), sub(pts[k], pts[i]))
        if normal == (0, 0, 0):
            continue
        signs = {(dot(normal, sub(p, pts[i])) > 0) - (dot(normal, sub(p, pts[i])) < 0) for p in pts}
        if 1 in signs and -1 in signs:
            continue
        on = frozenset(m for m, p in enumerate(pts) if dot(normal, sub(p, pts[i])) == 0)
        faces[on] = normal
    volume = Fraction(0)
    for on, normal in faces.items():
        face = [pts[m] for m in on]
        fc = tuple(sum(p[i] for p in face) / len(face) for i in range(3))
        # упорядочить точки грани по углу вокруг её центра
        u = sub(face[0], fc)
        w = cross(normal, u)
        face.sort(key=lambda p: math.atan2(float(dot(sub(p, fc), w)), float(dot(sub(p, fc), u))))
        for a, b in zip(face[1:], face[2:]):
            volume += abs(dot(sub(face[0], c), cross(sub(a, c), sub(b, c)))) / 6
    return volume


def _ans(x) -> str:
    return f'\n\n**Ответ:** {dec(x)}.'


class Solid(Template):
    number = 3

    def render(self, p):
        cond, sol, fig = self.build(p)
        figures = {}
        if fig is not None:
            cond += '\n\n![](figure://fig)'
            figures['fig'] = fig.svg()
        return Rendered(cond, sol + _ans(self.solve(p)), figures)


def _sub(name: str) -> str:
    """A1 → A_1"""
    return re.sub(r'([A-Z])1', r'\1_1', name)


# ---------------------------------------------------------------------------
# Многогранники
# ---------------------------------------------------------------------------

BOX_COORDS = {'A': (0, 0, 0), 'B': (1, 0, 0), 'C': (1, 1, 0), 'D': (0, 1, 0)}


class BoxPart(Solid):
    """Объём многогранника с вершинами в вершинах прямоугольного параллелепипеда"""
    topic, code = 'Многогранники', '3.box.part'
    patterns = [r'В прямоугольном параллелепипеде \$ABCDA_1B_1C_1D_1\$ известно, что \$(AB|BC|CD|AD)=(\d+)\$, \$(AB|BC|CD|AD)=(\d+)\$, \$(AA_1|BB_1|CC_1|DD_1)=(\d+)\$[.,] '
                r'Найдите объём многогранника, вершинами которого являются точки (.+?)\.\s',
                r'Найдите объём многогранника, вершинами которого являются вершины (.+?) прямоугольного параллелепипеда \$ABCDA_1B_1C_1D_1\$, у которого '
                r'\$(AB|BC|CD|AD)=(\d+)\$, \$(AB|BC|CD|AD)=(\d+)\$, \$(AA_1|BB_1|CC_1|DD_1)=(\d+)\$']

    def parse(self, m, task):
        g = m.groups()
        if m.re.pattern.startswith('В прям'):
            dims = {g[0]: int(g[1]), g[2]: int(g[3]), 'h': int(g[5])}
            verts = g[6]
        else:
            verts = g[0]
            dims = {g[1]: int(g[2]), g[3]: int(g[4]), 'h': int(g[6])}
        x = dims.get('AB') or dims.get('CD')
        y = dims.get('BC') or dims.get('AD')
        names = re.findall(r'([A-D])\s*\*?\s*(?:\$?_\{?1\}?\$?|_1)?', verts)
        names = re.findall(r'([A-D])(?:\*?\s*\$?\s*_\{?(1)\}?)?', verts.replace('*', '').replace('$', '').replace(' ', ''))
        vs = [a + (b or '') for a, b in names]
        if len(vs) < 4 or not x or not y:
            return None
        return {'a': x, 'b': y, 'c': dims['h'], 'v': vs}

    def _point(self, p, name):
        x, y, z = BOX_COORDS[name[0]]
        return (x * p['a'], y * p['b'], (p['c'] if name.endswith('1') else 0))

    def solve(self, p):
        return hull_volume([self._point(p, v) for v in p['v']])

    def build(self, p):
        a, b, c, vs = p['a'], p['b'], p['c'], p['v']
        listing = ', '.join(f'${_sub(v)}$' for v in vs)
        cond = (f'В прямоугольном параллелепипеде $ABCDA_1B_1C_1D_1$ известно, что $AB={a}$, $BC={b}$, $AA_1={c}$. '
                f'Найдите объём многогранника, вершинами которого являются точки {listing}.')
        V = a * b * c
        r = self.solve(p) / V
        kind = {Fraction(1, 6): ('треугольная пирамида', 'её основание — половина грани $ABCD$, высота — ребро параллелепипеда',
                                 '\\frac{1}{3}\\cdot\\frac{1}{2}S_{ABCD}\\cdot h=\\frac{1}{6}V'),
                Fraction(1, 3): ('четырёхугольная пирамида', 'её основание — грань параллелепипеда, высота — его ребро',
                                 '\\frac{1}{3}S_{\\text{осн}}\\cdot h=\\frac{1}{3}V'),
                Fraction(1, 2): ('треугольная призма', 'она отсекается от параллелепипеда диагональной плоскостью и составляет его половину',
                                 '\\frac{1}{2}V')}.get(r)
        sol = f'Объём параллелепипеда $V={a}\\cdot {b}\\cdot {c}={V}$.\n\n'
        if kind:
            sol += (f'Многогранник с вершинами {listing} — {kind[0]}: {kind[1]}. Поэтому его объём '
                    f'$${kind[2]}=\\frac{{{V}}}{{{r.denominator}}}={tex_num(self.solve(p))}.$$'
                    .replace(f'\\frac{{{V}}}{{1}}', str(V)))
        else:
            sol += f'Объём многогранника равен ${tex_frac(r)}V={tex_num(self.solve(p))}$.'
        fig = Figure(width=300, height=250)
        box(fig, a, b * 1.0, c)
        # выделим многогранник: рёбра между его вершинами
        coords = {v: fig.points[v] for v in vs}
        for u, w in itertools.combinations(vs, 2):
            fig.segment(coords[u], coords[w], width=1.0)
        return cond, sol, fig

    def sample(self, rng):
        sets = [['A', 'B', 'C', 'B1'], ['A', 'B', 'C', 'D', 'A1'], ['A', 'B', 'C', 'D', 'C1'], ['A', 'B', 'C', 'A1', 'B1', 'C1'],
                ['A', 'B', 'C', 'D', 'A1', 'B1'], ['A', 'D', 'D1', 'C'], ['B', 'C', 'D', 'B1', 'C1', 'D1']]
        vs = rng.choice(sets)
        a, b, c = rng.randint(2, 10), rng.randint(2, 10), rng.randint(2, 10)
        p = {'a': a, 'b': b, 'c': c, 'v': vs}
        return p if frac(self.solve(p)).denominator == 1 else None


class TriPrismPart(Solid):
    """Части правильной треугольной призмы: пирамида с вершинами A, B, C, C₁ и дополнение"""
    topic, code = 'Многогранники', '3.prism.part'
    patterns = [r'вершины (.+?) правильной треугольной призмы \$ABCA_1B_1C_1\$, площадь основания которой равна (\d+), а боковое ребро равно (\d+)',
                r'правильная треугольная призма \$ABCA_1B_1C_1\$, площадь основания которой равна (\d+), а боковое ребро равно (\d+)\. '
                r'Найдите объём многогранника, вершинами которого являются точки (.+?)\.\s']

    def parse(self, m, task):
        if m.re.pattern.startswith('вершины'):
            verts, s, h = m.group(1), int(m.group(2)), int(m.group(3))
        else:
            s, h, verts = int(m.group(1)), int(m.group(2)), m.group(3)
        vs = [a + (b or '') for a, b in re.findall(r'([A-C])(?:_\{?(1)\}?)?', verts.replace('$', '').replace(' ', ''))]
        return {'s': s, 'h': h, 'v': vs}

    COORDS = {'A': (0, 0), 'B': (2, 0), 'C': (1, 1)}  # площадь основания 1

    def solve(self, p):
        pts = [(*self.COORDS[v[0]], 1 if v.endswith('1') else 0) for v in p['v']]
        return hull_volume(pts) * p['s'] * p['h']

    def build(self, p):
        s, h, vs = p['s'], p['h'], p['v']
        listing = ', '.join(f'${_sub(v)}$' for v in vs)
        cond = (f'Дана правильная треугольная призма $ABCA_1B_1C_1$, площадь основания которой равна {s}, а боковое ребро равно {h}. '
                f'Найдите объём многогранника, вершинами которого являются точки {listing}.')
        V = s * h
        r = self.solve(p) / V
        if r == Fraction(1, 3):
            sol = (f'Многогранник — пирамида, у которой основание совпадает с основанием призмы, а высота равна боковому ребру. '
                   f'$$V=\\frac{{1}}{{3}}S\\cdot h=\\frac{{1}}{{3}}\\cdot {s}\\cdot {h}={tex_num(self.solve(p))}.$$')
        else:
            sol = (f'Многогранник получается из призмы, если отрезать от неё треугольную пирамиду, у которой основание — основание призмы, '
                   f'а высота — боковое ребро. Объём призмы $V={s}\\cdot {h}={V}$, объём пирамиды $\\frac{{1}}{{3}}V={tex_num(Fraction(V, 3))}$, '
                   f'поэтому искомый объём $${V}-{tex_num(Fraction(V, 3))}={tex_num(self.solve(p))}.$$')
        fig = Figure(width=280, height=260)
        coords3 = {'A': (0, 0, 0), 'B': (2.6, 0, 0), 'C': (0.7, 2.4, 0)}
        for n, (x, y, z) in coords3.items():
            fig.point(n, proj(x, y, z))
            fig.point(n + '1', proj(x, y, z + 2.2))
        for u, w in [('A', 'B'), ('A1', 'B1'), ('B1', 'C1'), ('C1', 'A1'), ('A', 'A1'), ('B', 'B1'), ('B', 'C')]:
            fig.segment(u, w)
        for u, w in [('A', 'C'), ('C', 'C1')]:
            fig.segment(u, w, dashed=True)
        center = proj(1, 0.6, 1.1)
        for n in list(fig.points):
            text = n if len(n) == 1 else f"{n[0]}<tspan baseline-shift='sub' font-size='12'>1</tspan>"
            fig.label(n, text=text, away_from=center)
        for u, w in itertools.combinations(vs, 2):
            fig.segment(fig.points[u], fig.points[w], width=1.0)
        return cond, sol, fig

    def sample(self, rng):
        sets = [['A', 'B', 'C', 'C1'], ['A', 'B', 'C', 'B1'], ['A', 'C', 'A1', 'B1', 'C1'], ['B', 'C', 'A1', 'B1', 'C1'],
                ['A', 'B', 'C', 'A1']]
        s, h = rng.randint(2, 15), rng.randint(2, 15)
        p = {'s': s, 'h': h, 'v': rng.choice(sets)}
        return p if frac(self.solve(p)).denominator == 1 else None


class PrismMidline(Solid):
    """Плоскость через среднюю линию основания, параллельная боковому ребру: объём ÷4, боковая поверхность ÷2"""
    topic, code = 'Многогранники', '3.prism.midline'
    patterns = [r'(?P<lat>Площадь боковой поверхности) треугольной призмы равна (?P<S>\d+)\. Через среднюю линию',
                r'Через среднюю линию основания (?:правильной )?треугольной призмы, объём которой равен (?P<V>\d+), проведена',
                r'Найдите объём этой призмы, если объём отсечённой треугольной призмы равен (?P<v>\d+)',
                r'Площадь боковой поверхности отсечённой треугольной призмы равна (?P<s>\d+)\. Найдите площадь боковой поверхности исходной']

    def parse(self, m, task):
        g = {k: int(v) for k, v in m.groupdict().items() if v and k != 'lat'}
        (kind, value), = g.items()
        return {'kind': kind, 'x': value}

    def solve(self, p):
        return {'S': Fraction(p['x'], 2), 'V': Fraction(p['x'], 4), 'v': 4 * p['x'], 's': 2 * p['x']}[p['kind']]

    def build(self, p):
        x, kind = p['x'], p['kind']
        head = 'Через среднюю линию основания треугольной призмы проведена плоскость, параллельная боковому ребру.'
        cond = {
            'S': f'Площадь боковой поверхности треугольной призмы равна {x}. {head[0].lower() + head[1:]} '.replace('через', 'Через', 1)
                 + 'Найдите площадь боковой поверхности отсечённой треугольной призмы.',
            'V': f'Через среднюю линию основания треугольной призмы, объём которой равен {x}, проведена плоскость, параллельная боковому ребру. '
                 'Найдите объём отсечённой треугольной призмы.',
            'v': f'{head} Найдите объём этой призмы, если объём отсечённой треугольной призмы равен {x}.',
            's': f'{head} Площадь боковой поверхности отсечённой треугольной призмы равна {x}. Найдите площадь боковой поверхности исходной призмы.',
        }[kind]
        if kind in ('V', 'v'):
            sol = ('Высоты призм одинаковы, а основание отсечённой призмы — треугольник, отсекаемый средней линией: '
                   'он подобен основанию с коэффициентом $\\frac{1}{2}$, его площадь в $4$ раза меньше. Значит, и объём отсечённой призмы '
                   'в 4 раза меньше объёма исходной: ')
            sol += f'$\\frac{{{x}}}{{4}}={tex_num(self.solve(p))}$.' if kind == 'V' else f'$4\\cdot {x}={self.solve(p)}$.'
        else:
            sol = ('Боковые рёбра у призм общие по длине, а периметр основания отсечённой призмы вдвое меньше: её стороны — '
                   'половины двух сторон основания и средняя линия, равная половине третьей. Поэтому площадь боковой поверхности '
                   'отсечённой призмы вдвое меньше: ')
            sol += f'$\\frac{{{x}}}{{2}}={tex_num(self.solve(p))}$.' if kind == 'S' else f'$2\\cdot {x}={self.solve(p)}$.'
        fig = Figure(width=280, height=240)
        A3, B3, C3 = (0, 0, 0), (2.4, 0, 0), (0.9, 1.9, 0)
        H = 2.0
        pts = {}
        for n, (x3, y3, z3) in {'A': A3, 'B': B3, 'C': C3}.items():
            pts[n] = fig.point(n, proj(x3, y3, z3))
            pts[n + '1'] = fig.point(n + '1', proj(x3, y3, z3 + H))
        M = ((A3[0] + C3[0]) / 2, (A3[1] + C3[1]) / 2, 0)
        N = ((B3[0] + C3[0]) / 2, (B3[1] + C3[1]) / 2, 0)
        fig.point('M', proj(*M)), fig.point('N', proj(*N)), fig.point('M1', proj(M[0], M[1], H)), fig.point('N1', proj(N[0], N[1], H))
        for u, w in [('A', 'B'), ('A1', 'B1'), ('B1', 'C1'), ('C1', 'A1'), ('A', 'A1'), ('B', 'B1'), ('B', 'C')]:
            fig.segment(u, w)
        for u, w in [('A', 'C'), ('C', 'C1'), ('M', 'N'), ('M', 'M1')]:
            fig.segment(u, w, dashed=True)
        fig.segment('M1', 'N1'), fig.segment('N', 'N1')
        return cond, sol, fig

    def sample(self, rng):
        kind = rng.choice(['S', 'V', 'v', 's'])
        x = rng.randint(3, 40) * (4 if kind == 'V' else 2 if kind == 'S' else 1)
        return {'kind': kind, 'x': x}


class CubeCorner(Solid):
    """Призма, отсечённая от куба плоскостью через середины двух рёбер из одной вершины: V/8"""
    topic, code = 'Многогранники', '3.cube.corner'
    patterns = [r'Объём куба равен (\d+)\. Найдите объём треугольной призмы, отсекаемой от куба']

    def parse(self, m, task):
        return {'V': int(m.group(1))}

    def solve(self, p):
        return Fraction(p['V'], 8)

    def build(self, p):
        V = p['V']
        cond = (f'Объём куба равен {V}. Найдите объём треугольной призмы, отсекаемой от куба плоскостью, проходящей через середины '
                f'двух рёбер, выходящих из одной вершины, и параллельной третьему ребру, выходящему из этой же вершины.')
        sol = ('Высота призмы равна ребру куба $a$, а основание — прямоугольный треугольник с катетами $\\frac{a}{2}$, его площадь '
               '$\\frac{1}{2}\\cdot\\frac{a}{2}\\cdot\\frac{a}{2}=\\frac{a^2}{8}$. Значит, объём призмы равен $\\frac{a^3}{8}$ — восьмая часть объёма куба: '
               f'$$\\frac{{{V}}}{{8}}={tex_num(self.solve(p))}.$$')
        fig = Figure(width=260, height=240)
        box(fig, 2, 2, 2, labels=False)
        for a3, b3 in [((1, 0, 0), (1, 0, 2)), ((0, 1, 0), (0, 1, 2)), ((1, 0, 2), (0, 1, 2))]:
            fig.segment(proj(*a3), proj(*b3), dashed=a3[1] > 0)
        fig.segment(proj(1, 0, 0), proj(0, 1, 0), dashed=True)
        return cond, sol, fig

    def sample(self, rng):
        return {'V': 8 * rng.randint(2, 40)}


# ---------------------------------------------------------------------------
# Тела вращения
# ---------------------------------------------------------------------------

def _cyl_figure(cone: bool = False, sphere: bool = False) -> Figure:
    fig = Figure(width=220, height=240)
    r, h = 1.0, (2.0 if not sphere else 2.0)
    fig.ellipse((0, 0), r, 0.3)
    fig.ellipse((0, h), r, 0.3, back='solid')
    fig.segment((-r, 0), (-r, h)), fig.segment((r, 0), (r, h))
    if cone:
        fig.segment((-r, 0), (0, h)), fig.segment((r, 0), (0, h))
    if sphere:
        fig.circle((0, h / 2), r)
        fig.ellipse((0, h / 2), r, 0.3)
    return fig


class CylinderCone(Solid):
    """Общие основание и высота: V_конуса = V_цилиндра / 3"""
    topic, code = 'Тела вращения', '3.rot.cyl-cone'
    patterns = [r'Цилиндр и конус имеют общие основание и высоту\. Объём (цилиндра|конуса) равен (\d+)\.']

    def parse(self, m, task):
        return {'given': 'cyl' if m.group(1) == 'цилиндра' else 'cone', 'x': int(m.group(2))}

    def solve(self, p):
        return Fraction(p['x'], 3) if p['given'] == 'cyl' else 3 * p['x']

    def build(self, p):
        given, x = p['given'], p['x']
        names = {'cyl': ('цилиндра', 'конуса'), 'cone': ('конуса', 'цилиндра')}[given]
        cond = f'Цилиндр и конус имеют общие основание и высоту. Объём {names[0]} равен {x}. Найдите объём {names[1]}.'
        sol = ('$V_{\\text{цил}}=\\pi r^2h$, $V_{\\text{кон}}=\\frac{1}{3}\\pi r^2h$: при общих основании и высоте объём конуса втрое меньше. ')
        sol += f'$V_{{\\text{{кон}}}}=\\frac{{{x}}}{{3}}={tex_num(self.solve(p))}$.' if given == 'cyl' else f'$V_{{\\text{{цил}}}}=3\\cdot {x}={self.solve(p)}$.'
        return cond, sol, _cyl_figure(cone=True)

    def sample(self, rng):
        given = rng.choice(['cyl', 'cone'])
        return {'given': given, 'x': rng.randint(2, 40) * (3 if given == 'cyl' else 1)}


class CylConeLateral(Solid):
    """h = r: S_бок.цил = 2πr², S_бок.кон = πr·r√2 → отношение √2"""
    topic, code = 'Тела вращения', '3.rot.cyl-cone-lateral'
    patterns = [r'Высота цилиндра равна радиусу основания\. Площадь боковой поверхности (цилиндра|конуса) равна \$(?:\\text\{)?(\d+)\}?\\sqrt\{2\}\$']

    def parse(self, m, task):
        return {'given': 'cyl' if m.group(1) == 'цилиндра' else 'cone', 'k': int(m.group(2))}

    def solve(self, p):
        # цилиндр k√2 → конус k;  конус k√2 → цилиндр 2k
        return p['k'] if p['given'] == 'cyl' else 2 * p['k']

    def build(self, p):
        k = p['k']
        names = ('цилиндра', 'конуса') if p['given'] == 'cyl' else ('конуса', 'цилиндра')
        cond = (f'Цилиндр и конус имеют общие основание и высоту. Высота цилиндра равна радиусу основания. Площадь боковой поверхности '
                f'{names[0]} равна ${k}\\sqrt{{2}}$. Найдите площадь боковой поверхности {names[1]}.')
        sol = ('Пусть $r$ — радиус, тогда $h=r$, а образующая конуса $l=\\sqrt{r^2+h^2}=r\\sqrt{2}$.\n\n'
               '$$S_{\\text{цил}}=2\\pi rh=2\\pi r^2,\\qquad S_{\\text{кон}}=\\pi rl=\\sqrt{2}\\,\\pi r^2,$$ поэтому $S_{\\text{цил}}=\\sqrt{2}\\,S_{\\text{кон}}$. ')
        if p['given'] == 'cyl':
            sol += f'$$S_{{\\text{{кон}}}}=\\frac{{{k}\\sqrt{{2}}}}{{\\sqrt{{2}}}}={k}.$$'
        else:
            sol += f'$$S_{{\\text{{цил}}}}=\\sqrt{{2}}\\cdot {k}\\sqrt{{2}}={2 * k}.$$'
        return cond, sol, _cyl_figure(cone=True)

    def sample(self, rng):
        return {'given': rng.choice(['cyl', 'cone']), 'k': rng.randint(2, 30)}


class SphereInCylinder(Solid):
    """Шар вписан в цилиндр: V_цил = 3/2·V_шара, S_полн.цил = 3/2·S_шара"""
    topic, code = 'Тела вращения', '3.rot.sphere-cyl'
    patterns = [r'(?P<a>Шар, объём которого равен (?P<vb>\d+), вписан в цилиндр)',
                r'(?P<b>Цилиндр, объём которого равен (?P<vc>\d+), описан около шара)',
                r'(?P<c>Шар вписан в цилиндр\. Площадь полной поверхности цилиндра равна (?P<sc>\d+))']

    def parse(self, m, task):
        g = m.groupdict()
        if g.get('vb'):
            return {'kind': 'vb', 'x': int(g['vb'])}
        if g.get('vc'):
            return {'kind': 'vc', 'x': int(g['vc'])}
        return {'kind': 'sc', 'x': int(g['sc'])}

    def solve(self, p):
        x = p['x']
        return {'vb': Fraction(3, 2) * x, 'vc': Fraction(2, 3) * x, 'sc': Fraction(2, 3) * x}[p['kind']]

    def build(self, p):
        x, kind = p['x'], p['kind']
        cond = {'vb': f'Шар, объём которого равен {x}, вписан в цилиндр. Найдите объём цилиндра.',
                'vc': f'Цилиндр, объём которого равен {x}, описан около шара. Найдите объём шара.',
                'sc': f'Шар вписан в цилиндр. Площадь полной поверхности цилиндра равна {x}. Найдите площадь поверхности шара.'}[kind]
        if kind == 'sc':
            sol = ('Радиус основания цилиндра равен радиусу шара $r$, высота цилиндра $2r$. '
                   '$$S_{\\text{цил}}=2\\pi r^2+2\\pi r\\cdot 2r=6\\pi r^2,\\qquad S_{\\text{шара}}=4\\pi r^2=\\frac{2}{3}S_{\\text{цил}}.$$'
                   f'$$S_{{\\text{{шара}}}}=\\frac{{2}}{{3}}\\cdot {x}={tex_num(self.solve(p))}.$$')
        else:
            sol = ('Радиус основания цилиндра равен радиусу шара $r$, высота цилиндра $2r$. '
                   '$$V_{\\text{цил}}=\\pi r^2\\cdot 2r=2\\pi r^3,\\qquad V_{\\text{шара}}=\\frac{4}{3}\\pi r^3=\\frac{2}{3}V_{\\text{цил}}.$$')
            sol += (f'$$V_{{\\text{{цил}}}}=\\frac{{3}}{{2}}\\cdot {x}={tex_num(self.solve(p))}.$$' if kind == 'vb'
                    else f'$$V_{{\\text{{шара}}}}=\\frac{{2}}{{3}}\\cdot {x}={tex_num(self.solve(p))}.$$')
        return cond, sol, _cyl_figure(sphere=True)

    def sample(self, rng):
        kind = rng.choice(['vb', 'vc', 'sc'])
        return {'kind': kind, 'x': rng.randint(2, 30) * (2 if kind == 'vb' else 3)}


class ConeInSphere(Solid):
    """Конус вписан в шар, радиус основания равен радиусу шара: V_кон = V_шара / 4"""
    topic, code = 'Тела вращения', '3.rot.cone-sphere'
    patterns = [r'Конус вписан в шар\. Радиус основания конуса равен радиусу шара\. Объём (шара|конуса) равен (\d+)\.']

    def parse(self, m, task):
        return {'given': 'ball' if m.group(1) == 'шара' else 'cone', 'x': int(m.group(2))}

    def solve(self, p):
        return Fraction(p['x'], 4) if p['given'] == 'ball' else 4 * p['x']

    def build(self, p):
        x = p['x']
        names = ('шара', 'конуса') if p['given'] == 'ball' else ('конуса', 'шара')
        cond = f'Конус вписан в шар. Радиус основания конуса равен радиусу шара. Объём {names[0]} равен {x}. Найдите объём {names[1]}.'
        sol = ('Основание конуса — большой круг шара, а высота конуса равна радиусу шара $R$. '
               '$$V_{\\text{кон}}=\\frac{1}{3}\\pi R^2\\cdot R=\\frac{1}{3}\\pi R^3,\\qquad V_{\\text{шара}}=\\frac{4}{3}\\pi R^3=4V_{\\text{кон}}.$$')
        sol += f'$V_{{\\text{{кон}}}}=\\frac{{{x}}}{{4}}={tex_num(self.solve(p))}$.' if p['given'] == 'ball' else f'$V_{{\\text{{шара}}}}=4\\cdot {x}={self.solve(p)}$.'
        fig = Figure(width=220, height=220)
        fig.circle((0, 0), 1)
        fig.ellipse((0, 0), 1, 0.3)
        fig.segment((-1, 0), (0, 1)), fig.segment((1, 0), (0, 1))
        return cond, sol, fig

    def sample(self, rng):
        given = rng.choice(['ball', 'cone'])
        return {'given': given, 'x': rng.randint(2, 40) * (4 if given == 'ball' else 1)}


class SphereAroundCone(Solid):
    """Центр описанной сферы — в центре основания конуса: l = R√2"""
    topic, code = 'Тела вращения', '3.rot.sphere-cone'
    patterns = [r'Центр сферы находится в центре основания конуса\. (Радиус сферы|Образующая конуса) рав\w+ \$(\d+)\\sqrt\{2\}\$']

    def parse(self, m, task):
        return {'given': 'R' if 'Радиус' in m.group(1) else 'l', 'k': int(m.group(2))}

    def solve(self, p):
        return 2 * p['k'] if p['given'] == 'R' else p['k']

    def build(self, p):
        k = p['k']
        head = ('Около конуса описана сфера (сфера содержит окружность основания конуса и его вершину). '
                'Центр сферы находится в центре основания конуса. ')
        cond = head + (f'Радиус сферы равен ${k}\\sqrt{{2}}$. Найдите длину образующей конуса.' if p['given'] == 'R'
                       else f'Образующая конуса равна ${k}\\sqrt{{2}}$. Найдите радиус сферы.')
        sol = ('Радиус основания конуса и его высота равны радиусу сферы $R$, а образующая — гипотенуза прямоугольного '
               'треугольника с катетами $R$ и $R$: $l=R\\sqrt{2}$. ')
        sol += (f'$$l={k}\\sqrt{{2}}\\cdot\\sqrt{{2}}={2 * k}.$$' if p['given'] == 'R' else f'$$R=\\frac{{{k}\\sqrt{{2}}}}{{\\sqrt{{2}}}}={k}.$$')
        fig = Figure(width=220, height=220)
        fig.circle((0, 0), 1)
        fig.ellipse((0, 0), 1, 0.3)
        fig.segment((-1, 0), (0, 1)), fig.segment((1, 0), (0, 1))
        fig.segment((0, 0), (0, 1), dashed=True), fig.segment((0, 0), (1, 0), dashed=True)
        return cond, sol, fig

    def sample(self, rng):
        return {'given': rng.choice(['R', 'l']), 'k': rng.randint(2, 40)}


class SolidScaling(Solid):
    """Как меняется объём при изменении размеров: цилиндры и конусы"""
    topic, code = 'Тела вращения', '3.rot.scale'
    patterns = [r'(?P<two>Дано два цилиндра\. Объём первого цилиндра равен (?P<V>\d+)\. У второго цилиндра высота в (?P<h>\d+) раза? (?P<hd>меньше|больше), '
                r'а радиус основания в (?P<r>\d+) раза? (?P<rd>меньше|больше))',
                r'(?P<cone>Во сколько раз (?P<dir>уменьшится|увеличится) объём конуса, если (?:его высота (?P<hd2>уменьшится|увеличится) в (?P<h2>\d+) раза?, а радиус основания останется прежним|радиус его основания (?P<rd2>увеличится|уменьшится) в (?P<r2>\d+) раза?, а высота останется прежней))']

    def parse(self, m, task):
        g = m.groupdict()
        if g.get('two'):
            h = Fraction(int(g['h'])) ** (1 if g['hd'] == 'больше' else -1)
            r = Fraction(int(g['r'])) ** (1 if g['rd'] == 'больше' else -1)
            return {'kind': 'two', 'V': int(g['V']), 'h': h, 'r': r}
        if g.get('h2'):
            return {'kind': 'cone', 'what': 'h', 'k': int(g['h2']), 'dir': g['dir']}
        return {'kind': 'cone', 'what': 'r', 'k': int(g['r2']), 'dir': g['dir']}

    def solve(self, p):
        if p['kind'] == 'two':
            return p['V'] * p['r'] ** 2 * p['h']
        return p['k'] if p['what'] == 'h' else p['k'] ** 2

    def build(self, p):
        if p['kind'] == 'two':
            h, r = p['h'], p['r']
            hw = f'в {h.denominator if h < 1 else h.numerator} раза {"меньше" if h < 1 else "больше"}'
            rw = f'в {r.denominator if r < 1 else r.numerator} раза {"меньше" if r < 1 else "больше"}'
            cond = (f'Дано два цилиндра. Объём первого цилиндра равен {p["V"]}. У второго цилиндра высота {hw}, '
                    f'а радиус основания {rw}, чем у первого. Найдите объём второго цилиндра.')
            sol = (f'$V=\\pi r^2h$. Радиус умножается на ${tex_num(r)}$, значит $r^2$ — на ${tex_num(r * r)}$; высота умножается на ${tex_frac(h)}$. '
                   f'$$V_2={p["V"]}\\cdot {tex_num(r * r)}\\cdot {tex_frac(h)}={tex_num(self.solve(p))}.$$')
            return cond, sol, _cyl_figure()
        k = p['k']
        if p['what'] == 'h':
            cond = f'Во сколько раз {p["dir"]} объём конуса, если его высота {p["dir"]} в {k} раз, а радиус основания останется прежним?'
            sol = f'$V=\\frac{{1}}{{3}}\\pi r^2h$ пропорционален высоте, поэтому объём {p["dir"]} в {k} раз.'
        else:
            cond = f'Во сколько раз {p["dir"]} объём конуса, если радиус его основания {p["dir"]} в {k} раз, а высота останется прежней?'
            sol = f'$V=\\frac{{1}}{{3}}\\pi r^2h$ пропорционален квадрату радиуса, поэтому объём {p["dir"]} в ${k}^2={k * k}$ раз.'
        return cond, sol, _cyl_figure(cone=True)

    def sample(self, rng):
        if rng.random() < 0.5:
            h = Fraction(rng.choice([2, 3, 4])) ** rng.choice([1, -1])
            r = Fraction(rng.choice([2, 3])) ** rng.choice([1, -1])
            V = rng.randint(2, 40)
            p = {'kind': 'two', 'V': V, 'h': h, 'r': r}
            return p if frac(self.solve(p)).denominator == 1 else None
        d = rng.choice(['уменьшится', 'увеличится'])
        return {'kind': 'cone', 'what': rng.choice(['h', 'r']), 'k': rng.randint(2, 12), 'dir': d}


class CylinderInBox(Solid):
    """Цилиндр вписан в прямоугольный параллелепипед: V = (2r)²·h"""
    topic, code = 'Тела вращения', '3.rot.cyl-box'
    patterns = [r'Цилиндр вписан в прямоугольный параллелепипед\. Радиус основания и высота цилиндра равны (\d+)\.']

    def parse(self, m, task):
        return {'r': int(m.group(1)), 'h': int(m.group(1))}

    def solve(self, p):
        return (2 * p['r']) ** 2 * p['h']

    def build(self, p):
        r, h = p['r'], p['h']
        if r == h:
            cond = f'Цилиндр вписан в прямоугольный параллелепипед. Радиус основания и высота цилиндра равны {r}. Найдите объём параллелепипеда.'
        else:
            cond = f'Цилиндр вписан в прямоугольный параллелепипед. Радиус основания цилиндра равен {r}, а высота равна {h}. Найдите объём параллелепипеда.'
        sol = (f'Основание параллелепипеда — квадрат, описанный около основания цилиндра: его сторона $2r={2 * r}$. Высоты совпадают. '
               f'$$V={2 * r}^2\\cdot {h}={self.solve(p)}.$$')
        return cond, sol, self.figure(r, h)

    @staticmethod
    def figure(r: float, h: float) -> Figure:
        """Параллелепипед 2r×2r×h и вписанный цилиндр: окружности оснований касаются сторон квадратов"""
        fig = Figure(width=260, height=260)
        box(fig, 2 * r, 2 * r, h, labels=False)
        k, deg = 0.45, math.radians(35)
        t1 = math.atan(k * math.cos(deg))                  # образующие — там, где контур эллипса крайний слева/справа
        for z in (0, h):
            pts = [proj(r + r * math.cos(t), r + r * math.sin(t), z) for t in [i * math.pi / 60 for i in range(121)]]
            front = [proj(r + r * math.cos(t), r + r * math.sin(t), z) for t in [t1 + math.pi + i * math.pi / 60 for i in range(61)]]
            back = [proj(r + r * math.cos(t), r + r * math.sin(t), z) for t in [t1 + i * math.pi / 60 for i in range(61)]]
            if z == 0:
                fig.curve(front, width=1.6)
                fig.curve(back, width=1.2, dashed=True)
            else:
                fig.curve(pts, width=1.6)
        for t in (t1, t1 + math.pi):
            x, y = r + r * math.cos(t), r + r * math.sin(t)
            fig.segment(proj(x, y, 0), proj(x, y, h), width=1.6)
        return fig

    def sample(self, rng):
        r = rng.randint(1, 9)
        return {'r': r, 'h': r if rng.random() < 0.5 else rng.randint(1, 12)}


class SphereSection(Solid):
    """Сечение через центр — большой круг: S_сферы = 4·S_сечения"""
    topic, code = 'Тела вращения', '3.rot.sphere-section'
    patterns = [r'Площадь сечения шара плоскостью, проходящей через центр шара, равна (\d+)\.']

    def parse(self, m, task):
        return {'s': int(m.group(1))}

    def solve(self, p):
        return 4 * p['s']

    def build(self, p):
        cond = f'Площадь сечения шара плоскостью, проходящей через центр шара, равна {p["s"]}. Найдите площадь поверхности шара.'
        sol = (f'Сечение через центр — круг радиуса $R$: $\\pi R^2={p["s"]}$. Площадь сферы $4\\pi R^2=4\\cdot {p["s"]}={self.solve(p)}$.')
        fig = Figure(width=200, height=200)
        fig.circle((0, 0), 1)
        fig.ellipse((0, 0), 1, 0.3)
        return cond, sol, fig

    def sample(self, rng):
        return {'s': rng.randint(2, 50)}


TEMPLATES = [BoxPart(), TriPrismPart(), PrismMidline(), CubeCorner(), CylinderCone(), CylConeLateral(), SphereInCylinder(),
             ConeInSphere(), SphereAroundCone(), SolidScaling(), CylinderInBox(), SphereSection()]
EXTRA = []
