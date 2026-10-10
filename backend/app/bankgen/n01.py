"""№ 1. Планиметрия"""
import math
import random
import re
from fractions import Fraction

from app.bankgen.core import Rendered, Template, dec, frac, isqrt_exact, num, tex_frac, tex_num
from app.bankgen.figures import Figure, bisector_foot, foot, lerp, mid, polar, tri_from_angles

DEGREES = ' Ответ дайте в градусах.'
D = r'(\d+)\^\\circ'


def _ans(x) -> str:
    return f'\n\n**Ответ:** {dec(x)}.'


class Geo(Template):
    number = 1

    def render(self, p):
        cond, sol, fig = self.build(p)
        figures = {'fig': fig.svg()} if fig else {}
        if fig:
            cond += '\n\n![](figure://fig)'
        return Rendered(cond, sol + _ans(self.solve(p)), figures)

    def build(self, p) -> tuple[str, str, Figure | None]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Прямоугольный треугольник
# ---------------------------------------------------------------------------

def _side(s: str) -> tuple[int, int]:
    """'10' → (10, 1); '\\sqrt{19}' → (1, 19) — длина как k√m"""
    m = re.fullmatch(r'(\d*)\\sqrt\{(\d+)\}', s)
    if m:
        return (int(m.group(1) or 1), int(m.group(2)))
    return (int(s), 1)


def _side_tex(k: int, m: int) -> str:
    if m == 1:
        return str(k)
    return (str(k) if k != 1 else '') + f'\\sqrt{{{m}}}'


def _side_sq(s: tuple[int, int]) -> int:
    return s[0] * s[0] * s[1]


class RightTriangleRatio(Geo):
    """∠C = 90°, известны гипотенуза и катет → sin A / cos A / tg A"""
    topic, code = 'Прямоугольный треугольник', '1.right.ratio'
    patterns = [r'угол \$C\$ равен \$90\^\\circ\$, \$AB=([\d\\sqrt{}]+)\$, \$(BC|AC)=([\d\\sqrt{}]+)\$\. Найдите \$\\(cos|sin|tg)A\$']

    def parse(self, m, task):
        return {'ab': _side(m.group(1)), 'leg': m.group(2), 'l': _side(m.group(3)), 'f': m.group(4)}

    def _sides(self, p):
        ab2, l2 = _side_sq(p['ab']), _side_sq(p['l'])
        other2 = ab2 - l2
        if other2 <= 0:
            raise ValueError('катет длиннее гипотенузы')
        return ab2, l2, other2

    def solve(self, p):
        ab2, l2, other2 = self._sides(p)
        bc2, ac2 = (l2, other2) if p['leg'] == 'BC' else (other2, l2)
        sq = {'sin': Fraction(bc2, ab2), 'cos': Fraction(ac2, ab2), 'tg': Fraction(bc2, ac2)}[p['f']]
        r = Fraction(isqrt_exact(sq.numerator) or 0, isqrt_exact(sq.denominator) or 1)
        if r * r != sq:
            raise ValueError('ответ не рациональный')
        return r

    def verify(self, p, a):
        ab2, l2, other2 = self._sides(p)
        bc2, ac2 = (l2, other2) if p['leg'] == 'BC' else (other2, l2)
        A = math.atan2(math.sqrt(bc2), math.sqrt(ac2))
        return math.isclose({'sin': math.sin, 'cos': math.cos, 'tg': math.tan}[p['f']](A), float(a), abs_tol=1e-9)

    def build(self, p):
        ab2, l2, other2 = self._sides(p)
        ab, leg = _side_tex(*p['ab']), _side_tex(*p['l'])
        other_name = 'AC' if p['leg'] == 'BC' else 'BC'
        f = p['f']
        fname = {'sin': '\\sin', 'cos': '\\cos', 'tg': '\\operatorname{tg}'}[f]
        cond = (f'В треугольнике $ABC$ угол $C$ равен $90^\\circ$, $AB={ab}$, ${p["leg"]}={leg}$. Найдите ${fname} A$.')
        other = isqrt_exact(other2)
        other_tex = str(other) if other is not None else f'\\sqrt{{{other2}}}'
        steps = (f'По теореме Пифагора $${other_name}=\\sqrt{{AB^2-{p["leg"]}^2}}=\\sqrt{{{ab2}-{l2}}}={other_tex}.$$\n\n')
        definition = {'sin': ('\\sin A=\\frac{BC}{AB}', 'противолежащего катета к гипотенузе'),
                      'cos': ('\\cos A=\\frac{AC}{AB}', 'прилежащего катета к гипотенузе'),
                      'tg': ('\\operatorname{tg} A=\\frac{BC}{AC}', 'противолежащего катета к прилежащему')}[f]
        need_other = (f == 'sin' and p['leg'] == 'AC') or (f == 'cos' and p['leg'] == 'BC') or f == 'tg'
        values = {'BC': leg if p['leg'] == 'BC' else other_tex, 'AC': leg if p['leg'] == 'AC' else other_tex, 'AB': ab}
        formula = definition[0]
        for k, v in values.items():
            formula_value = formula
        frac_tex = {'sin': f'\\frac{{{values["BC"]}}}{{{values["AB"]}}}', 'cos': f'\\frac{{{values["AC"]}}}{{{values["AB"]}}}',
                    'tg': f'\\frac{{{values["BC"]}}}{{{values["AC"]}}}'}[f]
        sol = ((steps if need_other else '')
               + f'{fname.replace("\\operatorname{tg}", "Тангенс").replace("\\sin", "Синус").replace("\\cos", "Косинус")} '
               f'острого угла — отношение {definition[1]}: $${formula}={frac_tex}={tex_num(self.solve(p))}.$$')
        # чертёж: C в начале координат, A на оси y
        ac, bc = math.sqrt(values_num(p)['AC']), math.sqrt(values_num(p)['BC'])
        fig = Figure()
        fig.point('C', (0, 0)), fig.point('A', (0, ac)), fig.point('B', (bc, 0))
        fig.polygon('A', 'B', 'C')
        fig.right_angle('C', 'A', 'B')
        for n in 'ABC':
            fig.label(n)
        return cond, sol, fig

    def sample(self, rng):
        f = rng.choice(['sin', 'cos', 'cos', 'sin', 'tg'])
        # гипотенуза и катеты: квадрат ответа рациональный, ответ — конечная дробь
        ab = rng.choice([2, 4, 5, 10, 20, 25])
        ratio = Fraction(rng.choice([1, 2, 3, 4, 6, 7, 8, 9]), 10) if ab in (5, 10, 20) else \
            Fraction(rng.choice([1, 3]), 4) if ab == 4 else Fraction(rng.choice([1, 2, 3, 4, 6, 7, 8, 9, 11, 12]), 25) if ab == 25 \
            else Fraction(1, 2)
        if f == 'tg':
            # tg A = BC/AC = t: BC = t·AC, AB² = AC²(1+t²)
            t = Fraction(rng.choice([1, 2, 3, 4, 5, 3, 1]), rng.choice([1, 2, 4, 5]))
            ac = rng.randint(2, 9)
            bc = t * ac
            if bc.denominator != 1:
                return None
            ab2 = ac * ac + int(bc) ** 2
            leg = rng.choice(['BC', 'AC'])
            l2 = int(bc) ** 2 if leg == 'BC' else ac * ac
            if math.isqrt(ab2) ** 2 == ab2:
                abt = (math.isqrt(ab2), 1)
            else:
                abt = (1, ab2)
            return {'ab': abt, 'leg': leg, 'l': (int(math.isqrt(l2)), 1), 'f': f}
        target = ratio * ab          # длина нужного катета (sin → BC, cos → AC)
        if target.denominator != 1:
            return None
        need = 'BC' if f == 'sin' else 'AC'
        other2 = ab * ab - int(target) ** 2
        leg = rng.choice(['BC', 'AC'])
        if leg == need:
            l = (int(target), 1)
        else:
            r = isqrt_exact(other2)
            l = (r, 1) if r else (1, other2)
        return {'ab': (ab, 1), 'leg': leg, 'l': l, 'f': f}

    def nice(self, x):
        # без «иголок»: острый угол от ~12° до ~78°
        return frac(x).denominator in (1, 2, 4, 5, 10, 20, 25) and Fraction(1, 5) <= x <= 5 and x != 1


def values_num(p) -> dict:
    ab2, l2 = _side_sq(p['ab']), _side_sq(p['l'])
    other2 = ab2 - l2
    return {'BC': l2 if p['leg'] == 'BC' else other2, 'AC': l2 if p['leg'] == 'AC' else other2, 'AB': ab2}


class RightTriangleLines(Geo):
    """Угол между высотой, медианой и биссектрисой из вершины прямого угла"""
    topic, code = 'Прямоугольный треугольник', '1.right.lines'
    patterns = [r'Острый угол \$B\$ прямоугольного треугольника \$ABC\$ равен \$' + D + r'\$\. Найдите величину угла между '
                r'(высотой|биссектрисой) \$C[HD]\$ и (медианой|биссектрисой) \$C[MD]\$']

    def parse(self, m, task):
        return {'b': int(m.group(1)), 'l1': m.group(2), 'l2': m.group(3)}

    def solve(self, p):
        b = p['b']
        angle = {'высотой': 90 - b, 'биссектрисой': 45, 'медианой': b}  # угол линии с катетом CB
        return abs(angle[p['l1']] - angle[p['l2']])

    def build(self, p):
        b, l1, l2 = p['b'], p['l1'], p['l2']
        letters = {'высотой': 'H', 'биссектрисой': 'D', 'медианой': 'M'}
        names = {'высотой': 'высотой', 'биссектрисой': 'биссектрисой', 'медианой': 'медианой'}
        cond = (f'Острый угол $B$ прямоугольного треугольника $ABC$ равен ${b}^\\circ$. Найдите величину угла между '
                f'{names[l1]} $C{letters[l1]}$ и {names[l2]} $C{letters[l2]}$, проведёнными из вершины прямого угла $C$.'
                + DEGREES)
        facts = {
            'высотой': f'В треугольнике $CHB$ угол $H$ прямой, поэтому $\\angle HCB=90^\\circ-{b}^\\circ={90 - b}^\\circ$.',
            'медианой': (f'Медиана, проведённая к гипотенузе, равна её половине: $CM=MB$, поэтому треугольник $CMB$ '
                         f'равнобедренный и $\\angle MCB=\\angle B={b}^\\circ$.'),
            'биссектрисой': 'Биссектриса делит прямой угол пополам: $\\angle DCB=45^\\circ$.',
        }
        angle = {'высотой': 90 - b, 'биссектрисой': 45, 'медианой': b}
        x, y = letters[l1], letters[l2]
        sol = (f'{facts[l1]} {facts[l2]}\n\nИскомый угол — разность этих углов: '
               f'$$\\angle {x}C{y}=|{angle[l1]}^\\circ-{angle[l2]}^\\circ|={self.solve(p)}^\\circ.$$')
        A, B, C = tri_from_angles(90 - b, b, 1.0)
        fig = Figure()
        fig.point('A', A), fig.point('B', B), fig.point('C', C)
        fig.polygon('A', 'B', 'C')
        fig.right_angle('C', 'A', 'B')
        pts = {'H': foot(C, A, B), 'M': mid(A, B), 'D': bisector_foot(C, A, B)}
        for name in {x, y}:
            fig.point(name, pts[name])
            fig.segment('C', name)
            fig.label(name, away_from=C)
        if 'H' in (x, y):
            fig.right_angle('H', 'B', 'C')
        for n in 'ABC':
            fig.label(n)
        return cond, sol, fig

    def sample(self, rng):
        l1, l2 = rng.choice([('высотой', 'медианой'), ('высотой', 'биссектрисой'), ('биссектрисой', 'медианой')])
        b = rng.randint(8, 82)
        if b == 45:
            return None
        return {'b': b, 'l1': l1, 'l2': l2}


# ---------------------------------------------------------------------------
# Окружность
# ---------------------------------------------------------------------------

class Diameters(Geo):
    """AC и BD — диаметры. ∠ACB ↔ ∠AOD"""
    topic, code = 'Углы в окружности', '1.circle.diameters'
    patterns = [r'Отрезки \$AC\$ и \$BD\$ — диаметры окружности с центром \$O\$\. Угол \$(ACB|AOD)\$ равен \$' + D
                + r'\$\. Найдите [^$]*\$(AOD|ACB)\$']

    def parse(self, m, task):
        if m.group(1) == m.group(3):
            return None
        return {'given': m.group(1), 'x': int(m.group(2))}

    def solve(self, p):
        return 180 - 2 * p['x'] if p['given'] == 'ACB' else Fraction(180 - p['x'], 2)

    def build(self, p):
        x, given = p['x'], p['given']
        find = 'AOD' if given == 'ACB' else 'ACB'
        cond = (f'Отрезки $AC$ и $BD$ — диаметры окружности с центром $O$. Угол ${given}$ равен ${x}^\\circ$. '
                f'Найдите {"вписанный угол" if find == "ACB" else "угол"} ${find}$.' + DEGREES)
        acb = x if given == 'ACB' else self.solve(p)
        aob = 2 * acb
        sol = (f'Вписанный угол $ACB$ опирается на дугу $AB$, поэтому центральный угол $AOB$ вдвое больше: '
               f'$\\angle AOB=2\\angle ACB$. Углы $AOB$ и $AOD$ смежные ($BD$ — диаметр), так что '
               f'$\\angle AOD=180^\\circ-\\angle AOB$.\n\n')
        if given == 'ACB':
            sol += f'$$\\angle AOD=180^\\circ-2\\cdot {x}^\\circ={self.solve(p)}^\\circ.$$'
        else:
            sol += (f'$$\\angle AOB=180^\\circ-{x}^\\circ={180 - x}^\\circ,\\qquad '
                    f'\\angle ACB=\\frac{{{180 - x}^\\circ}}{{2}}={tex_num(self.solve(p))}^\\circ.$$')
        # чертёж: A и C на концах диаметра, угол AOB = 2·ACB
        fig = Figure()
        O = fig.point('O', (0, 0))
        fig.point('A', polar(O, 1, 200)), fig.point('C', polar(O, 1, 20))
        fig.point('B', polar(O, 1, 200 - float(aob))), fig.point('D', polar(O, 1, 20 - float(aob)))
        fig.circle('O', 1)
        fig.segment('A', 'C'), fig.segment('B', 'D'), fig.segment('C', 'B')
        fig.dot('O')
        for n in 'ABCD':
            fig.label(n, away_from=O)
        fig.label('O', at=(0.05, -0.2))
        return cond, sol, fig

    def sample(self, rng):
        given = rng.choice(['ACB', 'AOD'])
        if given == 'ACB':
            return {'given': given, 'x': rng.randint(12, 78)}
        x = rng.randint(10, 160)
        return {'given': given, 'x': x} if x % 2 == 0 else None


class TangentAngle(Geo):
    """CA — касательная, CO пересекает окружность в B: ∠ACO + дуга AB = 90°"""
    topic, code = 'Касательная к окружности', '1.circle.tangent'
    patterns = [r'Найдите [^$]*\$ACO\$.*?дуга \$AB\$ окружности, заключённая внутри этого угла, равна \$(?P<arc>\d+)\^\\circ\$',
                r'Угол \$ACO\$ равен \$(?P<angle>\d+)\^\\circ\$\..*?Найдите градусную меру дуги \$AB\$']

    def parse(self, m, task):
        g = m.groupdict()
        if g.get('arc'):
            return {'given': 'arc', 'x': int(g['arc'])}
        return {'given': 'angle', 'x': int(g['angle'])}

    def solve(self, p):
        return 90 - p['x']

    def build(self, p):
        x = p['x']
        if p['given'] == 'arc':
            cond = (f'Найдите угол $ACO$, если его сторона $CA$ касается окружности с центром $O$, отрезок $CO$ '
                    f'пересекает окружность в точке $B$ (см. рисунок), а дуга $AB$ окружности, заключённая внутри этого угла, '
                    f'равна ${x}^\\circ$.' + DEGREES)
            arc = x
        else:
            cond = (f'Угол $ACO$ равен ${x}^\\circ$. Его сторона $CA$ касается окружности с центром $O$. Отрезок $CO$ '
                    f'пересекает окружность в точке $B$ (см. рисунок). Найдите градусную меру дуги $AB$ окружности, '
                    f'заключённой внутри этого угла.' + DEGREES)
            arc = 90 - x
        sol = (f'Радиус, проведённый в точку касания, перпендикулярен касательной: $\\angle OAC=90^\\circ$. '
               f'Центральный угол $AOB$ равен дуге $AB$, на которую он опирается. Сумма острых углов прямоугольного '
               f'треугольника $OAC$ равна $90^\\circ$, поэтому $$\\angle ACO+\\overset{{\\frown}}{{AB}}=90^\\circ,$$ и искомая величина '
               f'равна $90^\\circ-{x}^\\circ={self.solve(p)}^\\circ$.')
        fig = Figure()
        O = fig.point('O', (0, 0))
        A = fig.point('A', polar(O, 1, 90 + 0))
        # C на касательной в A (горизонтальная прямая y=1), угол AOC = arc
        dist = math.tan(math.radians(arc))
        C = fig.point('C', (dist, 1))
        b = 1 / math.hypot(*C)
        fig.point('B', (C[0] * b, C[1] * b))
        fig.circle('O', 1)
        fig.segment('O', 'A'), fig.segment('O', 'C'), fig.segment('A', 'C')
        fig.right_angle('A', 'O', 'C')
        fig.dot('O')
        fig.label('A', away_from=O), fig.label('C', away_from=O)
        Bp = fig.points['B']
        fig.label('B', at=(Bp[0] + 0.14, Bp[1] - 0.06))  # справа от прямой CO, а не на ней
        fig.label('O', at=(-0.12, -0.12))
        return cond, sol, fig

    def sample(self, rng):
        return {'given': rng.choice(['arc', 'angle']), 'x': rng.randint(15, 75)}


class CentralInscribed(Geo):
    """Центральный угол на d больше вписанного, опирающегося на ту же дугу"""
    topic, code = 'Углы в окружности', '1.circle.central'
    patterns = [r'(?:Найдите [^,]*центральн\w+ уг\w*, если он|Центральный угол) на \$' + D
                + r'\$ больше острого вписанного угла, опирающегося на ту же дугу(?: окружности)?\. (Найдите (?:величину )?вписанн\w+ угл?а?)?']

    def parse(self, m, task):
        return {'d': int(m.group(1)), 'find': 'inscribed' if m.group(2) else 'central'}

    def solve(self, p):
        return p['d'] if p['find'] == 'inscribed' else 2 * p['d']

    def build(self, p):
        d = p['d']
        if p['find'] == 'central':
            cond = f'Найдите центральный угол, если он на ${d}^\\circ$ больше острого вписанного угла, опирающегося на ту же дугу.' + DEGREES
        else:
            cond = f'Центральный угол на ${d}^\\circ$ больше острого вписанного угла, опирающегося на ту же дугу окружности. Найдите вписанный угол.' + DEGREES
        sol = (f'Центральный угол вдвое больше вписанного, опирающегося на ту же дугу. Если вписанный угол равен $x$, '
               f'то центральный равен $2x$, и $2x-x={d}^\\circ$, то есть $x={d}^\\circ$.\n\n'
               f'Значит, вписанный угол равен ${d}^\\circ$, а центральный — ${2 * d}^\\circ$.')
        fig = Figure()
        O = fig.point('O', (0, 0))
        fig.point('A', polar(O, 1, -90 - d)), fig.point('B', polar(O, 1, -90 + d)), fig.point('C', polar(O, 1, 100))
        fig.circle('O', 1)
        fig.segment('O', 'A'), fig.segment('O', 'B'), fig.segment('C', 'A'), fig.segment('C', 'B')
        fig.dot('O')
        for n in 'ABC':
            fig.label(n, away_from=O)
        fig.label('O', at=(0.15, 0.08))
        return cond, sol, fig

    def sample(self, rng):
        return {'d': rng.randint(12, 85), 'find': rng.choice(['central', 'inscribed'])}


class CyclicQuad(Geo):
    """Вписанный четырёхугольник ABCD: ∠ABC = ∠ABD + ∠DBC, ∠DBC = ∠DAC"""
    topic, code = 'Углы в окружности', '1.circle.cyclic'
    patterns = [r'Четырёхугольник \$ABCD\$ вписан в окружность\. Угол \$(ABC|ABD)\$ равен \$' + D + r'\$, угол \$(CAD|ABD)\$ равен \$'
                + D + r'\$\. Найдите угол \$(ABD|ABC|CAD)\$']

    def parse(self, m, task):
        return {'g1': m.group(1), 'x': int(m.group(2)), 'g2': m.group(3), 'y': int(m.group(4)), 'find': m.group(5)}

    def _angles(self, p):
        v = {p['g1']: p['x'], p['g2']: p['y']}
        abc, abd, cad = v.get('ABC'), v.get('ABD'), v.get('CAD')
        if abc is None:
            abc = abd + cad
        elif abd is None:
            abd = abc - cad
        else:
            cad = abc - abd
        return abc, abd, cad

    def solve(self, p):
        abc, abd, cad = self._angles(p)
        if min(abc, abd, cad) <= 0 or abc >= 180:
            raise ValueError('некорректные углы')
        return {'ABC': abc, 'ABD': abd, 'CAD': cad}[p['find']]

    def build(self, p):
        abc, abd, cad = self._angles(p)
        cond = (f'Четырёхугольник $ABCD$ вписан в окружность. Угол ${p["g1"]}$ равен ${p["x"]}^\\circ$, '
                f'угол ${p["g2"]}$ равен ${p["y"]}^\\circ$. Найдите угол ${p["find"]}$.' + DEGREES)
        sol = (f'Вписанные углы $DBC$ и $DAC$ опираются на одну дугу $DC$, поэтому $\\angle DBC=\\angle CAD$. '
               f'Кроме того, $\\angle ABC=\\angle ABD+\\angle DBC=\\angle ABD+\\angle CAD$.\n\n')
        sol += {'ABC': f'$$\\angle ABC={abd}^\\circ+{cad}^\\circ={abc}^\\circ.$$',
                'ABD': f'$$\\angle ABD=\\angle ABC-\\angle CAD={abc}^\\circ-{cad}^\\circ={abd}^\\circ.$$',
                'CAD': f'$$\\angle CAD=\\angle ABC-\\angle ABD={abc}^\\circ-{abd}^\\circ={cad}^\\circ.$$'}[p['find']]
        # A, B, C, D по окружности: дуга AD = 2·ABD, дуга DC = 2·CAD
        fig = Figure()
        O = (0, 0)
        b_ang = 90
        a_ang = b_ang + 180 - 2 * abc + 2 * cad  # подбираем так, чтобы дуги были корректны
        a_ang = 210
        d_ang = a_ang + 2 * abd
        c_ang = d_ang + 2 * cad
        b_ang = (c_ang + (360 + a_ang - c_ang) / 2) % 360 if c_ang < a_ang + 360 else 90
        fig.point('A', polar(O, 1, a_ang)), fig.point('D', polar(O, 1, d_ang)), fig.point('C', polar(O, 1, c_ang))
        fig.point('B', polar(O, 1, b_ang))
        fig.circle(O, 1)
        fig.polygon('A', 'B', 'C', 'D')
        fig.segment('A', 'C'), fig.segment('B', 'D')
        for n in 'ABCD':
            fig.label(n, away_from=O)
        return cond, sol, fig

    def sample(self, rng):
        abd, cad = rng.randint(20, 75), rng.randint(20, 75)
        abc = abd + cad
        if abc >= 150:
            return None
        known = rng.choice([('ABC', 'CAD', 'ABD'), ('ABD', 'CAD', 'ABC'), ('ABC', 'ABD', 'CAD')])
        v = {'ABC': abc, 'ABD': abd, 'CAD': cad}
        return {'g1': known[0], 'x': v[known[0]], 'g2': known[1], 'y': v[known[1]], 'find': known[2]}


class CyclicQuadAngles(Geo):
    """Два угла вписанного четырёхугольника → больший из оставшихся"""
    topic, code = 'Углы в окружности', '1.circle.cyclic-sum'
    patterns = [r'Два угла вписанного в окружность четырёхугольника равны \$' + D + r'\$ и \$' + D + r'\$\. Найдите (бо́льший|меньший)']

    def parse(self, m, task):
        return {'a': int(m.group(1)), 'b': int(m.group(2)), 'which': 'больший' if 'бо' in m.group(3) else 'меньший'}

    def solve(self, p):
        others = [180 - p['a'], 180 - p['b']]
        return max(others) if p['which'] == 'больший' else min(others)

    def build(self, p):
        a, b = p['a'], p['b']
        cond = (f'Два угла вписанного в окружность четырёхугольника равны ${a}^\\circ$ и ${b}^\\circ$. '
                f'Найдите {"бо́льший" if p["which"] == "больший" else "меньший"} из оставшихся углов.' + DEGREES)
        sol = (f'Данные углы не могут быть противолежащими: их сумма ${a + b}^\\circ\\ne 180^\\circ$. '
               f'Сумма противолежащих углов вписанного четырёхугольника равна $180^\\circ$, поэтому оставшиеся углы равны '
               f'$180^\\circ-{a}^\\circ={180 - a}^\\circ$ и $180^\\circ-{b}^\\circ={180 - b}^\\circ$. '
               f'{p["which"].capitalize()} из них — ${self.solve(p)}^\\circ$.')
        # ∠A = a, ∠B = b: дуги BCD = 2a и CDA = 2b; дугу CD берём посередине допустимого
        gamma = (max(2 * a + 2 * b - 360, 0) + min(2 * a, 2 * b)) / 2
        beta, delta = 2 * a - gamma, 2 * b - gamma
        alpha = 360 - beta - gamma - delta
        fig = Figure()
        O = (0, 0)
        start = 200 - alpha / 2
        angles = [start, start + alpha, start + alpha + beta, start + alpha + beta + gamma]
        for name, ang in zip('ABCD', angles):
            fig.point(name, polar(O, 1, ang))
        fig.circle(O, 1)
        fig.polygon('A', 'B', 'C', 'D')
        for n in 'ABCD':
            fig.label(n, away_from=O)
        return cond, sol, fig

    def sample(self, rng):
        a, b = rng.randint(40, 140), rng.randint(40, 140)
        if a + b == 180 or a == b or 180 - a == b:
            return None
        return {'a': a, 'b': b, 'which': rng.choice(['больший', 'меньший'])}


# ---------------------------------------------------------------------------
# Треугольники и четырёхугольники
# ---------------------------------------------------------------------------

class IsoscelesExterior(Geo):
    """AC = BC; ∠C ↔ внешний угол при B"""
    topic, code = 'Треугольники', '1.tri.isosceles'
    patterns = [r'стороны \$AC\$ и \$BC\$ равны, угол \$C\$ равен \$(?P<c>\d+)\^\\circ\$, угол \$CBD\$ внешний',
                r'стороны \$AC\$ и \$BC\$ равны\. Внешний угол при вершине \$B\$ равен \$(?P<ext>\d+)\^\\circ\$\. Найдите угол \$C\$']

    def parse(self, m, task):
        g = m.groupdict()
        if g.get('c'):
            return {'given': 'C', 'x': int(g['c'])}
        return {'given': 'ext', 'x': int(g['ext'])}

    def solve(self, p):
        x = p['x']
        return Fraction(180 + x, 2) if p['given'] == 'C' else 2 * x - 180

    def build(self, p):
        x = p['x']
        if p['given'] == 'C':
            cond = (f'В треугольнике $ABC$ стороны $AC$ и $BC$ равны, угол $C$ равен ${x}^\\circ$, угол $CBD$ внешний. '
                    f'Найдите величину угла $CBD$.' + DEGREES)
            b = Fraction(180 - x, 2)
            sol = (f'Треугольник равнобедренный с основанием $AB$, поэтому $\\angle A=\\angle B=\\frac{{180^\\circ-{x}^\\circ}}{{2}}'
                   f'={tex_num(b)}^\\circ$. Внешний угол смежен с углом $B$: $$\\angle CBD=180^\\circ-{tex_num(b)}^\\circ={tex_num(self.solve(p))}^\\circ.$$')
            c = x
        else:
            cond = (f'В треугольнике $ABC$ стороны $AC$ и $BC$ равны. Внешний угол при вершине $B$ равен ${x}^\\circ$. '
                    f'Найдите угол $C$.' + DEGREES)
            b = 180 - x
            sol = (f'Угол $B$ смежен с внешним: $\\angle B=180^\\circ-{x}^\\circ={b}^\\circ$. Треугольник равнобедренный с основанием $AB$, '
                   f'поэтому $\\angle A=\\angle B={b}^\\circ$, и $$\\angle C=180^\\circ-2\\cdot {b}^\\circ={self.solve(p)}^\\circ.$$')
            c = self.solve(p)
        base = float(Fraction(180 - c, 2))
        A, B, C = tri_from_angles(base, base, 1.0)
        fig = Figure()
        fig.point('A', A), fig.point('B', B), fig.point('C', C), fig.point('D', (1.45, 0))
        fig.polygon('A', 'B', 'C')
        fig.segment('B', 'D')
        fig.tick('A', 'C'), fig.tick('B', 'C')
        for n in 'ABC':
            fig.label(n)
        fig.label('D', at=(1.45, -0.12))
        return cond, sol, fig

    def sample(self, rng):
        if rng.random() < 0.5:
            x = rng.randint(20, 170)
            return {'given': 'C', 'x': x} if x % 2 == 0 else None
        return {'given': 'ext', 'x': rng.randint(95, 175)}


class BisectorTriangle(Geo):
    """∠C и угол при биссектрисе AD → ∠B или ∠ADB"""
    topic, code = 'Треугольники', '1.tri.bisector'
    patterns = [r'В треугольнике \$ABC\$ угол \$C\$ равен \$' + D + r'\$, \$AD\$ — биссектриса, угол \$(CAD|BAD)\$ равен \$' + D
                + r'\$\. Найдите величину угла \$(B|ABD|ADB)\$']

    def parse(self, m, task):
        return {'c': int(m.group(1)), 'half': int(m.group(3)), 'which': m.group(2),
                'find': 'ADB' if m.group(4) == 'ADB' else 'B', 'name': m.group(4)}

    def solve(self, p):
        c, h = p['c'], p['half']
        if p['find'] == 'ADB':
            return c + h
        b = 180 - c - 2 * h
        if b <= 0:
            raise ValueError('углы не складываются')
        return b

    def build(self, p):
        c, h, which = p['c'], p['half'], p['which']
        name = p.get('name') or p['find']
        cond = (f'В треугольнике $ABC$ угол $C$ равен ${c}^\\circ$, $AD$ — биссектриса, угол ${which}$ равен ${h}^\\circ$. '
                f'Найдите величину угла ${name}$.' + DEGREES)
        if p['find'] == 'ADB':
            sol = (f'Биссектриса делит угол $A$ пополам: $\\angle CAD=\\angle BAD={h}^\\circ$. Угол $ADB$ — внешний угол '
                   f'треугольника $ADC$, он равен сумме двух углов, не смежных с ним: $$\\angle ADB=\\angle C+\\angle CAD='
                   f'{c}^\\circ+{h}^\\circ={c + h}^\\circ.$$')
        else:
            sol = (f'Биссектриса делит угол $A$ пополам, поэтому $\\angle A=2\\cdot {h}^\\circ={2 * h}^\\circ$. По сумме углов треугольника '
                   f'$$\\angle B=180^\\circ-{c}^\\circ-{2 * h}^\\circ={self.solve(p) if p["find"] == "B" else 0}^\\circ.$$')
        A, B, C = tri_from_angles(2 * h, 180 - c - 2 * h, 1.0)
        fig = Figure()
        fig.point('A', A), fig.point('B', B), fig.point('C', C)
        fig.point('D', bisector_foot(A, B, C))
        fig.polygon('A', 'B', 'C')
        fig.segment('A', 'D')
        fig.angle_arc('A', 'B', 'D'), fig.angle_arc('A', 'D', 'C')
        for n in 'ABC':
            fig.label(n)
        fig.label('D', away_from=A)
        return cond, sol, fig

    def sample(self, rng):
        c, h = rng.randint(30, 100), rng.randint(12, 40)
        if 180 - c - 2 * h < 15:
            return None
        if rng.random() < 0.5:
            return {'c': c, 'half': h, 'which': 'BAD', 'find': 'ADB', 'name': 'ADB'}
        return {'c': c, 'half': h, 'which': 'CAD', 'find': 'B', 'name': rng.choice(['B', 'ABD'])}


class TangentialQuad(Geo):
    """В четырёхугольник вписана окружность: AB + CD = BC + AD"""
    topic, code = 'Четырёхугольники', '1.quad.incircle'
    patterns = [r'В четырёхугольник \$ABCD\$, периметр которого равен (\d+), вписана окружность, \$AB=(\d+)\$, Найдите длину стороны \$CD\$',
                r'В четырёхугольник \$ABCD\$ вписана окружность, \$AB=(\d+)\$, \$CD=(\d+)\$, Найдите периметр',
                r'В четырёхугольник \$ABCD\$ вписана окружность, \$AB=(\d+)\$, \$BC=(\d+)\$, \$CD=(\d+)\$, Найдите длину четвёртой']

    def parse(self, m, task):
        g = m.groups()
        if 'периметр которого' in m.group(0):
            return {'kind': 'cd', 'P': int(g[0]), 'ab': int(g[1])}
        if 'Найдите периметр' in m.group(0):
            return {'kind': 'P', 'ab': int(g[0]), 'cd': int(g[1])}
        return {'kind': 'ad', 'ab': int(g[0]), 'bc': int(g[1]), 'cd': int(g[2])}

    def solve(self, p):
        if p['kind'] == 'cd':
            return Fraction(p['P'], 2) - p['ab']
        if p['kind'] == 'P':
            return 2 * (p['ab'] + p['cd'])
        return p['ab'] + p['cd'] - p['bc']

    def build(self, p):
        rule = ('В четырёхугольник можно вписать окружность тогда и только тогда, когда суммы его противоположных сторон равны: '
                '$$AB+CD=BC+AD.$$\n\n')
        if p['kind'] == 'cd':
            cond = (f'В четырёхугольник $ABCD$, периметр которого равен {p["P"]}, вписана окружность, $AB={p["ab"]}$. '
                    f'Найдите длину стороны $CD$.')
            sol = rule + (f'Значит, $AB+CD$ — половина периметра: $AB+CD={tex_num(Fraction(p["P"], 2))}$, '
                          f'откуда $CD={tex_num(Fraction(p["P"], 2))}-{p["ab"]}={tex_num(self.solve(p))}$.')
        elif p['kind'] == 'P':
            cond = f'В четырёхугольник $ABCD$ вписана окружность, $AB={p["ab"]}$, $CD={p["cd"]}$. Найдите периметр четырёхугольника $ABCD$.'
            sol = rule + (f'Периметр равен $2(AB+CD)=2\\cdot ({p["ab"]}+{p["cd"]})={self.solve(p)}$.')
        else:
            cond = (f'В четырёхугольник $ABCD$ вписана окружность, $AB={p["ab"]}$, $BC={p["bc"]}$, $CD={p["cd"]}$. '
                    f'Найдите длину четвёртой стороны четырёхугольника.')
            sol = rule + f'$$AD=AB+CD-BC={p["ab"]}+{p["cd"]}-{p["bc"]}={self.solve(p)}.$$'
        # описанный четырёхугольник: касательные из вершин к единичной окружности
        fig = Figure()
        O = (0, 0)
        tangents = [200, 300, 30, 110]
        pts = []
        for a1, a2 in zip(tangents, tangents[1:] + tangents[:1]):
            d = ((a2 - a1) % 360) / 2
            pts.append(polar(O, 1 / math.cos(math.radians(d)), a1 + d))
        for name, pt in zip('ABCD', pts):
            fig.point(name, pt)
        fig.polygon('A', 'B', 'C', 'D')
        fig.circle(O, 1)
        for n in 'ABCD':
            fig.label(n, away_from=O)
        return cond, sol, fig

    def sample(self, rng):
        kind = rng.choice(['cd', 'P', 'ad'])
        if kind == 'cd':
            ab = rng.randint(3, 15)
            cd = rng.randint(3, 15)
            return {'kind': kind, 'P': 2 * (ab + cd), 'ab': ab}
        if kind == 'P':
            return {'kind': kind, 'ab': rng.randint(3, 20), 'cd': rng.randint(3, 20)}
        ab, bc, cd = rng.randint(4, 15), rng.randint(3, 15), rng.randint(4, 18)
        if ab + cd - bc < 2 or ab + cd - bc == bc:
            return None
        return {'kind': kind, 'ab': ab, 'bc': bc, 'cd': cd}


class AreaParts(Geo):
    """Части площади: параллелограмм и середина стороны, треугольник и средняя линия"""
    topic, code = 'Площади', '1.area.parts'
    patterns = [r'Площадь параллелограмма \$ABCD\$ равна (\d+)\. Точка \$E\$ — середина стороны \$AD\$\. Найдите площадь (трапеции \$BCDE\$|треугольника \$ABE\$)',
                r'Площадь треугольника \$ABC\$ равна (\d+), \$DE\$ — средняя линия, параллельная стороне \$AB\$\. Найдите площадь (треугольника \$CDE\$|трапеции \$ABED\$)']

    def parse(self, m, task):
        shape = 'par' if 'параллелограмма' in m.group(0) else 'tri'
        part = 'trap' if 'трапеции' in m.group(2) else 'tri'
        return {'shape': shape, 'S': int(m.group(1)), 'part': part}

    def solve(self, p):
        k = Fraction(1, 4) if p['part'] == 'tri' else Fraction(3, 4)
        return p['S'] * k

    def build(self, p):
        S = p['S']
        if p['shape'] == 'par':
            target = 'трапеции $BCDE$' if p['part'] == 'trap' else 'треугольника $ABE$'
            cond = f'Площадь параллелограмма $ABCD$ равна {S}. Точка $E$ — середина стороны $AD$. Найдите площадь {target}.'
            sol = (f'Треугольник $ABE$ и параллелограмм имеют общую высоту, проведённую к прямой $AD$, а основание $AE$ '
                   f'вдвое меньше $AD$. Поэтому $S_{{ABE}}=\\frac{{1}}{{2}}\\cdot AE\\cdot h=\\frac{{1}}{{4}}\\cdot AD\\cdot h=\\frac{{{S}}}{{4}}'
                   f'={tex_num(Fraction(S, 4))}$.')
            if p['part'] == 'trap':
                sol += f' Трапеция $BCDE$ — оставшаяся часть: ${S}-{tex_num(Fraction(S, 4))}={tex_num(self.solve(p))}$.'
            fig = Figure()
            fig.point('A', (0, 0)), fig.point('D', (2, 0)), fig.point('B', (0.6, 1)), fig.point('C', (2.6, 1)), fig.point('E', (1, 0))
            fig.polygon('A', 'B', 'C', 'D')
            fig.segment('B', 'E')
            for n in 'ABCDE':
                fig.label(n)
            fig.tick('A', 'E'), fig.tick('E', 'D')
        else:
            target = 'треугольника $CDE$' if p['part'] == 'tri' else 'трапеции $ABED$'
            cond = f'Площадь треугольника $ABC$ равна {S}, $DE$ — средняя линия, параллельная стороне $AB$. Найдите площадь {target}.'
            sol = (f'Треугольник $CDE$ подобен треугольнику $CAB$ с коэффициентом $\\frac{{1}}{{2}}$ (средняя линия вдвое короче $AB$), '
                   f'а площади подобных фигур относятся как квадрат коэффициента: $S_{{CDE}}=\\frac{{1}}{{4}}\\cdot {S}={tex_num(Fraction(S, 4))}$.')
            if p['part'] == 'trap':
                sol += f' Площадь трапеции $ABED$: ${S}-{tex_num(Fraction(S, 4))}={tex_num(self.solve(p))}$.'
            fig = Figure()
            A, B, C = (0, 0), (2.4, 0), (0.8, 1.6)
            fig.point('A', A), fig.point('B', B), fig.point('C', C)
            fig.point('D', mid(A, C)), fig.point('E', mid(B, C))
            fig.polygon('A', 'B', 'C')
            fig.segment('D', 'E')
            for n in 'ABCDE':
                fig.label(n)
        return cond, sol, fig

    def sample(self, rng):
        return {'shape': rng.choice(['par', 'tri']), 'S': 4 * rng.randint(3, 30), 'part': rng.choice(['trap', 'tri'])}


class HeightsInverse(Geo):
    """Стороны и высоты: a·hₐ = b·h_b (треугольник и параллелограмм)"""
    topic, code = 'Площади', '1.area.heights'
    patterns = [r'(Две стороны треугольника|Стороны параллелограмма) равны (\d+) и (\d+)\. Высота, опущенная на (бо́льшую|меньшую) из этих сторон, равна (\d+)\.']

    def parse(self, m, task):
        a, b = sorted([int(m.group(2)), int(m.group(3))])
        return {'shape': 'tri' if 'треугольника' in m.group(1) else 'par', 'small': a, 'big': b,
                'to': 'big' if 'бо' in m.group(4) else 'small', 'h': int(m.group(5))}

    def solve(self, p):
        if p['to'] == 'big':
            return Fraction(p['big'] * p['h'], p['small'])
        return Fraction(p['small'] * p['h'], p['big'])

    def build(self, p):
        a, b, h = p['small'], p['big'], p['h']
        known, other = ('бо́льшую', 'меньшую') if p['to'] == 'big' else ('меньшую', 'бо́льшую')
        side_k, side_o = (b, a) if p['to'] == 'big' else (a, b)
        if p['shape'] == 'tri':
            cond = (f'Две стороны треугольника равны {a} и {b}. Высота, опущенная на {known} из этих сторон, равна {h}. '
                    f'Найдите высоту, опущенную на {other} из этих сторон треугольника.')
            formula = 'S=\\frac{1}{2}a h_a=\\frac{1}{2}b h_b'
        else:
            cond = (f'Стороны параллелограмма равны {a} и {b}. Высота, опущенная на {known} из этих сторон, равна {h}. '
                    f'Найдите высоту, опущенную на {other} сторону параллелограмма.')
            formula = 'S=a h_a=b h_b'
        sol = (f'Площадь можно посчитать через любую сторону и проведённую к ней высоту: $${formula}.$$ '
               f'Поэтому произведение стороны на высоту одинаково: $$h=\\frac{{{side_k}\\cdot {h}}}{{{side_o}}}={tex_num(self.solve(p))}.$$')
        fig = Figure()
        if p['shape'] == 'tri':
            A, B = (0, 0), (float(b), 0)
            hb = float(h if p['to'] == 'big' else self.solve(p))
            x = math.sqrt(max(a * a - hb * hb, 0.01))
            C = (x, hb)
            fig.point('A', A), fig.point('B', B), fig.point('C', C), fig.point('H', (x, 0))
            fig.polygon('A', 'B', 'C')
            fig.segment('C', 'H', dashed=True)
            fig.right_angle('H', 'B', 'C')
            return cond, sol, fig
        # AB = b (бо́льшая) по горизонтали, AD = a; высота на бо́льшую сторону равна a·sin φ
        h_big = float(h if p['to'] == 'big' else self.solve(p))
        if h_big >= a:
            return cond, sol, None
        phi = math.asin(h_big / a)
        A, B = (0.0, 0.0), (float(b), 0.0)
        D = (a * math.cos(phi), a * math.sin(phi))
        C = (B[0] + D[0], D[1])
        for n, pt in zip('ABCD', (A, B, C, D)):
            fig.point(n, pt)
        fig.polygon('A', 'B', 'C', 'D')
        if p['to'] == 'big':          # данная высота — на AB из вершины D
            fig.point('H', (D[0], 0.0))
            fig.segment('D', 'H', dashed=True)
            fig.right_angle('H', 'B', 'D')
        else:                         # данная высота — на AD из вершины B
            t = (B[0] * D[0]) / (a * a)
            fig.point('H', (D[0] * t, D[1] * t))
            fig.segment('B', 'H', dashed=True)
            fig.right_angle('H', 'B', 'D')
        center = (C[0] / 2, C[1] / 2)
        for n in 'ABCDH':
            fig.label(n, away_from=center)
        return cond, sol, fig

    def sample(self, rng):
        a, b = sorted(rng.sample(range(6, 40), 2))
        h = rng.randint(4, a - 1) if rng.random() < 0.5 else rng.randint(4, min(a, b) - 1)
        to = rng.choice(['big', 'small'])
        return {'shape': rng.choice(['tri', 'par']), 'small': a, 'big': b, 'to': to, 'h': h}

    def nice(self, x):
        return frac(x).denominator in (1, 2, 4, 5)


class CircumRadius(Geo):
    """R = c / (2 sin C)"""
    topic, code = 'Треугольники', '1.tri.circumradius'
    patterns = [r'сторона \$AB\$ равна \$(\d*)\\sqrt\{(\d+)\}\$, угол \$[CС]\$ равен \$' + D + r'\$\. Найдите радиус описанной']

    SIN = {30: (1, 2, 1), 150: (1, 2, 1), 45: (1, 2, 2), 135: (1, 2, 2), 60: (1, 2, 3), 120: (1, 2, 3)}

    def parse(self, m, task):
        return {'k': int(m.group(1) or 1), 'r': int(m.group(2)), 'c': int(m.group(3))}

    def solve(self, p):
        # 2R = k√r / sin C, sin C = √s/2 → R = k√r/√s
        _, _, s = self.SIN[p['c']]
        if p['r'] % s:
            raise ValueError('не сокращается')
        q = Fraction(p['k'] ** 2 * p['r'], s)
        root = isqrt_exact(q.numerator)
        if root is None or q.denominator != 1:
            raise ValueError('R иррациональный')
        return Fraction(root)

    def build(self, p):
        k, r, c = p['k'], p['r'], p['c']
        side = f'{k if k != 1 else ""}\\sqrt{{{r}}}'
        s = self.SIN[p['c']][2]
        sin_tex = '\\frac{1}{2}' if s == 1 else f'\\frac{{\\sqrt{{{s}}}}}{{2}}'
        cond = f'В треугольнике $ABC$ сторона $AB$ равна ${side}$, угол $C$ равен ${c}^\\circ$. Найдите радиус описанной около этого треугольника окружности.'
        sol = (f'По теореме синусов $\\frac{{AB}}{{\\sin C}}=2R$, где $\\sin {c}^\\circ={sin_tex}$:\n\n'
               f'$$R=\\frac{{AB}}{{2\\sin C}}=\\frac{{{side}}}{{2\\cdot {sin_tex}}}={tex_num(self.solve(p))}.$$')
        # дуга AB, не содержащая C, равна 2c: A и B симметричны относительно низа окружности, C — наверху
        fig = Figure()
        O = (0, 0)
        fig.point('A', polar(O, 1, 270 - c)), fig.point('B', polar(O, 1, 270 + c)), fig.point('C', polar(O, 1, 90 + 25))
        fig.point('O', O)
        fig.circle(O, 1)
        fig.polygon('A', 'B', 'C')
        fig.dot('O')
        fig.label('O', at=(0.08, -0.12))
        for n in 'ABC':
            fig.label(n, away_from=O)
        return cond, sol, fig

    def sample(self, rng):
        c = rng.choice([60, 120, 45, 135])
        s = self.SIN[c][2]
        R = rng.randint(2, 15)
        # AB = 2R sin C = R√s → k√r с r = s
        return {'k': R, 'r': s, 'c': c}


TEMPLATES = [RightTriangleRatio(), RightTriangleLines(), Diameters(), TangentAngle(), CentralInscribed(), CyclicQuad(),
             CyclicQuadAngles(), IsoscelesExterior(), BisectorTriangle(), TangentialQuad(), AreaParts(), HeightsInverse(),
             CircumRadius()]
EXTRA = []
