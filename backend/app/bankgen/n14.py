"""
№ 14. Стереометрическая задача (вторая часть): доказательство и вычисление.

Каждый класс — семейство заданий ФИПИ с одной формулировкой. Ответ пишется формулой в решении,
а check получает его заново из координат вершин (app.bankgen.geo3).
"""
import math

import sympy as sp

from app.bankgen import geo3 as g
from app.bankgen.part2 import S, Answer, Solved, r, tx

SECTIONS, DIST, ANGLES, VOLUMES, BODIES = 'Сечения многогранников', 'Расстояния в пространстве', \
    'Углы в пространстве', 'Объёмы многогранников', 'Тела вращения'

RATIOS = [(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (3, 2)]


def tri_pyramid(a, b):
    """Правильная треугольная пирамида ABCD (D — вершина): координаты float"""
    a, b = float(a), float(b)
    h = math.sqrt(b * b - a * a / 3)
    A, B, C = (0.0, 0.0, 0.0), (a, 0.0, 0.0), (a / 2, a * math.sqrt(3) / 2, 0.0)
    O = g.centroid(A, B, C)
    return A, B, C, (O[0], O[1], h)


def quad_pyramid(a, s=None, h=None) -> dict:
    """Правильная четырёхугольная пирамида SABCD: центр основания O в начале координат"""
    a = float(a)
    h = float(h) if h is not None else math.sqrt(float(s) ** 2 - a * a / 2)
    k = a / 2
    return {'A': (-k, -k, 0.0), 'B': (k, -k, 0.0), 'C': (k, k, 0.0), 'D': (-k, k, 0.0), 'S': (0.0, 0.0, h)}


def hex_pyramid(a, s=None, h=None) -> dict:
    """Правильная шестиугольная пирамида SABCDEF: O — начало, C = (a, 0), F = (−a, 0), AB ∥ FC сверху"""
    a = float(a)
    h = float(h) if h is not None else math.sqrt(float(s) ** 2 - a * a)
    pts = {}
    for name, ang in zip('ABCDEF', (120, 60, 0, -60, -120, 180)):
        pts[name] = (a * math.cos(math.radians(ang)), a * math.sin(math.radians(ang)), 0.0)
    pts['S'] = (0.0, 0.0, h)
    return pts


def box(p, q, h) -> dict:
    """Прямоугольный параллелепипед: AB = p вдоль x, AD = q вдоль y, AA₁ = h"""
    p, q, h = float(p), float(q), float(h)
    base = {'A': (0, 0), 'B': (p, 0), 'C': (p, q), 'D': (0, q)}
    pts = {n: (x, y, 0.0) for n, (x, y) in base.items()}
    pts.update({n + '1': (x, y, h) for n, (x, y) in base.items()})
    return pts


def prism(base: dict, h) -> dict:
    """Прямая призма над многоугольником base (имя → (x, y))"""
    pts = {n: (x, y, 0.0) for n, (x, y) in base.items()}
    pts.update({n + '1': (x, y, float(h)) for n, (x, y) in base.items()})
    return pts


def tri_base(a) -> dict:
    """Правильный треугольник ABC со стороной a: AB вдоль x"""
    a = float(a)
    return {'A': (0.0, 0.0), 'B': (a, 0.0), 'C': (a / 2, a * math.sqrt(3) / 2)}


class TriPyramidRectangle(Solved):
    """Сечение правильной треугольной пирамиды плоскостью ∥ AC и BD — прямоугольник"""
    number, topic = 14, SECTIONS
    fipi = {'30ED04': dict(a=6, b=5, m=2, n=1), '149319': dict(a=5, b=9, m=1, n=2)}

    def answer(self, p):
        return Answer.num(r(p['a'] * p['b'] * p['m'] * p['n'], (p['m'] + p['n']) ** 2))

    def check(self, p):
        A, B, C, D = tri_pyramid(p['a'], p['b'])
        T = g.ratio(A, D, p['m'], p['n'])
        pl = g.plane_pv(T, g.sub(C, A), g.sub(D, B))
        sec = g.section([A, B, C, D], pl)
        sides = [g.sub(sec[(i + 1) % 4], sec[i]) for i in range(4)]
        assert len(sec) == 4 and g.perpendicular(sides[0], sides[1])   # пункт а — прямоугольник
        return g.polygon_area(sec)

    def condition(self, p):
        return (f'Дана правильная треугольная пирамида $ABCD$ с основанием $ABC$, сторона основания равна ${p["a"]}$, '
                f'боковое ребро равно ${p["b"]}$. Точка $T$ на ребре $AD$ такова, что $AT:TD={p["m"]}:{p["n"]}$. '
                'Через $T$ проведена плоскость, параллельная прямым $AC$ и $BD$.\n\n'
                'а) Докажите, что сечение пирамиды этой плоскостью — прямоугольник.\n\n'
                'б) Найдите площадь сечения.')

    def solution(self, p):
        a, b, m, n = p['a'], p['b'], p['m'], p['n']
        k = m + n
        tk, tl = r(a * n, k), r(b * m, k)
        return (
            'а) Плоскость сечения параллельна $AC$, поэтому пересекает грани $ACD$ и $ABC$ по прямым, параллельным $AC$; '
            'она параллельна $BD$ — и пересекает грани $ABD$ и $BCD$ по прямым, параллельным $BD$. '
            'Пусть $K$, $L$, $M$ — точки пересечения плоскости с рёбрами $CD$, $AB$, $BC$. Тогда $TK\\parallel AC\\parallel LM$ '
            'и $TL\\parallel BD\\parallel KM$, значит, $TLMK$ — параллелограмм.\n\n'
            'Пусть $O$ — центр основания, $DO$ — высота пирамиды. В правильном треугольнике $BO\\perp AC$, '
            '$BO$ — проекция $BD$ на плоскость основания, по теореме о трёх перпендикулярах $BD\\perp AC$. '
            'Стороны параллелограмма $TLMK$ параллельны $AC$ и $BD$, поэтому он — прямоугольник.\n\n'
            f'б) Из подобия треугольников $DTK$ и $DAC$: $TK=AC\\cdot\\frac{{DT}}{{DA}}={a}\\cdot\\frac{{{n}}}{{{k}}}={tx(tk)}$. '
            f'Из подобия $ATL$ и $ADB$: $TL=BD\\cdot\\frac{{AT}}{{AD}}={b}\\cdot\\frac{{{m}}}{{{k}}}={tx(tl)}$.\n\n'
            f'$$S_{{TLMK}}=TK\\cdot TL={tx(tk)}\\cdot {tx(tl)}={tx(tk * tl)}.$$')

    def figure(self, p):
        A, B, C, D = tri_pyramid(p['a'], p['b'])
        T = g.ratio(A, D, p['m'], p['n'])
        pl = g.plane_pv(T, g.sub(C, A), g.sub(D, B))
        L, M, K = g.line_plane(A, B, pl), g.line_plane(B, C, pl), g.line_plane(C, D, pl)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D}, extra={'T': T, 'L': L, 'M': M, 'K': K},
                      section_names=['T', 'L', 'M', 'K'])

    def sample(self, rng):
        a = rng.randint(3, 12)
        b = rng.randint(math.floor(a / math.sqrt(3)) + 1, 14)
        m, n = rng.choice(RATIOS)
        return dict(a=a, b=b, m=m, n=n)


class PrismKMPerp(Solved):
    """Прямая призма с равнобедренным основанием: KM ⊥ AC, угол KM с плоскостью ABB₁"""
    number, topic = 14, ANGLES
    fipi = {'F7B7A1': dict(ab=6, ac=8, h=3)}

    @staticmethod
    def _pts(p):
        ab, ac, h = map(float, (p['ab'], p['ac'], p['h']))
        bh = math.sqrt(ab * ab - ac * ac / 4)
        A, C, B = (0.0, 0.0, 0.0), (ac, 0.0, 0.0), (ac / 2, bh, 0.0)
        up = lambda P: (P[0], P[1], h)
        return A, B, C, up(A), up(B), up(C)

    def _sin(self, p):
        ab, ac, h = p['ab'], p['ac'], p['h']
        cosA = r(ac, 2 * ab)
        sinA = S(1 - cosA ** 2)
        d = r(ac, 4) * sinA                       # расстояние от M до AB
        km = S(r(ab ** 2, 4) - r(ac ** 2, 16) + h ** 2)  # K'M = BH/2
        return sp.radsimp(d / km), d, km, sinA

    def answer(self, p):
        return Answer.angle(self._sin(p)[0], 'arcsin')

    def check(self, p):
        A, B, C, A1, B1, C1 = self._pts(p)
        K, M = g.mid(A1, B1), g.ratio(A, C, 1, 3)
        assert g.perpendicular(g.sub(M, K), g.sub(C, A))
        return g.angle_line_plane(g.sub(M, K), g.plane(A, B, B1))

    def condition(self, p):
        return (f'В основании прямой призмы $ABCA_1B_1C_1$ лежит равнобедренный треугольник $ABC$ с $AB=BC={p["ab"]}$ '
                f'и $AC={p["ac"]}$, боковое ребро равно ${p["h"]}$. Точка $K$ — середина $A_1B_1$, точка $M$ на $AC$ '
                'такова, что $AM:MC=1:3$.\n\nа) Докажите, что $KM\\perp AC$.\n\n'
                'б) Найдите угол между прямой $KM$ и плоскостью $ABB_1$.')

    def solution(self, p):
        ab, ac, h = p['ab'], p['ac'], p['h']
        sin, d, km, sinA = self._sin(p)
        bh2 = ab ** 2 - r(ac ** 2, 4)
        return (
            'а) Пусть $K\'$ — середина $AB$ (проекция точки $K$ на плоскость основания), $H$ — середина $AC$. '
            'Медиана $BH$ равнобедренного треугольника — его высота: $BH\\perp AC$. Так как $AM=\\frac14 AC=\\frac12 AH$, '
            '$M$ — середина $AH$, и $K\'M$ — средняя линия треугольника $ABH$: $K\'M\\parallel BH$, значит, $K\'M\\perp AC$. '
            '$K\'M$ — проекция $KM$ на плоскость основания, по теореме о трёх перпендикулярах $KM\\perp AC$.\n\n'
            f'б) $BH=\\sqrt{{AB^2-AH^2}}=\\sqrt{{{tx(bh2)}}}$, $K\'M=\\frac12 BH$, '
            f'$KM=\\sqrt{{KK\'^2+K\'M^2}}=\\sqrt{{{h ** 2}+{tx(bh2 / 4)}}}={tx(km)}$.\n\n'
            'Плоскость $ABB_1$ перпендикулярна основанию, поэтому расстояние от $M$ до неё равно расстоянию от $M$ '
            f'до прямой $AB$: $AM\\cdot\\sin A$, где $\\cos A=\\frac{{AH}}{{AB}}={tx(r(ac, 2 * ab))}$, $\\sin A={tx(sinA)}$. '
            f'Расстояние равно ${tx(r(ac, 4))}\\cdot {tx(sinA)}={tx(d)}$. Точка $K$ лежит в плоскости $ABB_1$, поэтому синус '
            f'искомого угла $$\\sin\\varphi=\\frac{{{tx(d)}}}{{{tx(km)}}}={tx(sin)}.$$')

    def figure(self, p):
        A, B, C, A1, B1, C1 = self._pts(p)
        K, M = g.mid(A1, B1), g.ratio(A, C, 1, 3)
        return g.draw({'A': A, 'B': B, 'C': C, 'A1': A1, 'B1': B1, 'C1': C1}, extra={'K': K, 'M': M},
                      segments=[('K', 'M')], azim=-25, elev=20)

    def sample(self, rng):
        ac = rng.choice([4, 6, 8, 10, 12])
        ab = rng.randint(ac // 2 + 1, ac + 4)
        return dict(ab=ab, ac=ac, h=rng.randint(2, 8))


class BoxEFT(Solved):
    """Параллелепипед: A₁E = 2·B₁F, T — середина B₁C₁ ⇒ плоскость EFT проходит через D₁"""
    number, topic = 14, SECTIONS
    fipi = {'E95564': dict(p=2, q=6, h=6, m=1, n=2, ask='angle'),
            'C300DC': dict(p='6*sqrt(2)', q=10, h=16, m=5, n=3, ask='area'),
            'E8E9A7': dict(p='2*sqrt(2)', q=6, h=10, m=3, n=2, ask='area')}

    @staticmethod
    def _v(p):
        P, q, h = sp.sympify(p['p']), sp.Integer(p['q']), sp.Integer(p['h'])
        e = h * r(p['m'], p['m'] + p['n'])
        return P, q, h, e

    def _pts(self, p):
        P, q, h, e = (float(x) for x in self._v(p))
        pts = box(P, q, h)
        E = (0.0, 0.0, h - e)
        F = (P, 0.0, h - e / 2)
        T = g.mid(pts['B1'], pts['C1'])
        return pts, E, F, T

    def answer(self, p):
        P, q, h, e = self._v(p)
        if p['ask'] == 'angle':
            a1p = e * 2 * P / S(e ** 2 + 4 * P ** 2)
            return Answer.angle(sp.radsimp(q / a1p))
        xd1 = S(4 * P ** 2 + q ** 2)
        eh = S(e ** 2 + (2 * P * q / xd1) ** 2)
        return Answer.num(sp.nsimplify(sp.simplify(r(3, 8) * xd1 * eh)))

    def check(self, p):
        pts, E, F, T = self._pts(p)
        pl = g.plane(E, F, T)
        assert g.on_plane(pl, pts['D1'])
        if p['ask'] == 'angle':
            return g.angle_planes(pl, g.plane(pts['A'], pts['A1'], pts['B1']))
        return g.polygon_area(g.section(list(pts.values()), pl))

    def condition(self, p):
        q = 'угол между плоскостью $EFT$ и плоскостью $AA_1B_1$' if p['ask'] == 'angle' else \
            'площадь сечения параллелепипеда плоскостью $EFT$'
        m, n = p['m'], p['n']
        return (f'В прямоугольном параллелепипеде $ABCDA_1B_1C_1D_1$ известно, что $AB={tx(sp.sympify(p["p"]))}$, '
                f'$AD={p["q"]}$, $AA_1={p["h"]}$. Точка $E$ на ребре $AA_1$ делит его в отношении $A_1E:EA={m}:{n}$, '
                f'точка $F$ на ребре $BB_1$ — в отношении $B_1F:FB={m}:{m + 2 * n}$, $T$ — середина ребра $B_1C_1$.\n\n'
                'а) Докажите, что плоскость $EFT$ проходит через вершину $D_1$.\n\n'
                f'б) Найдите {q}.')

    def solution(self, p):
        P, q, h, e = self._v(p)
        f = e / 2
        t = (f'а) $A_1E=AA_1\\cdot\\frac{{{p["m"]}}}{{{p["m"] + p["n"]}}}={tx(e)}$, '
             f'$B_1F=BB_1\\cdot\\frac{{{p["m"]}}}{{{2 * p["m"] + 2 * p["n"]}}}={tx(f)}$, то есть $A_1E=2B_1F$. '
             'В плоскости $AA_1B_1$ прямая $EF$ пересекает прямую $A_1B_1$ в точке $X$. Так как $B_1F\\parallel A_1E$ и '
             '$B_1F=\\frac12 A_1E$, отрезок $B_1F$ — средняя линия треугольника $XA_1E$, поэтому $XB_1=A_1B_1$, $XA_1=2A_1B_1$.\n\n'
             'В плоскости $A_1B_1C_1$: $B_1T\\parallel A_1D_1$ и $B_1T=\\frac12 A_1D_1=\\frac12 B_1C_1$. Треугольники $XB_1T$ и $XA_1D_1$ '
             'подобны с коэффициентом $\\frac12$ (общий угол $X$, $\\frac{XB_1}{XA_1}=\\frac{B_1T}{A_1D_1}$), поэтому точки $X$, $T$, $D_1$ '
             'лежат на одной прямой. Прямая $XT$ лежит в плоскости $EFT$, значит, и $D_1$ лежит в этой плоскости.\n\n')
        if p['ask'] == 'angle':
            a1p = e * 2 * P / S(e ** 2 + 4 * P ** 2)
            return t + (
                'б) Плоскости $EFT$ и $AA_1B_1$ пересекаются по прямой $EX$. Ребро $A_1D_1$ перпендикулярно плоскости $AA_1B_1$. '
                'Проведём $A_1H\\perp EX$; по теореме о трёх перпендикулярах $D_1H\\perp EX$, и $\\angle A_1HD_1$ — линейный угол '
                'искомого двугранного угла.\n\n'
                f'В прямоугольном треугольнике $EA_1X$: $A_1E={tx(e)}$, $A_1X=2AB={tx(2 * P)}$, '
                f'$A_1H=\\frac{{A_1E\\cdot A_1X}}{{EX}}=\\frac{{{tx(e * 2 * P)}}}{{{tx(S(e ** 2 + 4 * P ** 2))}}}={tx(a1p)}$.\n\n'
                f'$$\\operatorname{{tg}}\\angle A_1HD_1=\\frac{{A_1D_1}}{{A_1H}}=\\frac{{{q}}}{{{tx(a1p)}}}={tx(sp.radsimp(q / a1p))}.$$')
        xd1 = S(4 * P ** 2 + q ** 2)
        a1h = 2 * P * q / xd1
        eh = S(e ** 2 + a1h ** 2)
        s = sp.nsimplify(sp.simplify(r(3, 8) * xd1 * eh))
        return t + (
            'б) Сечение — четырёхугольник $EFTD_1$: плоскость пересекает грани $AA_1B_1B$, $BB_1C_1C$, $A_1B_1C_1D_1$, $AA_1D_1D$ '
            'по отрезкам $EF$, $FT$, $TD_1$, $D_1E$. Он получается из треугольника $XED_1$ отрезанием треугольника $XFT$, '
            'подобного ему с коэффициентом $\\frac12$, поэтому $S_{EFTD_1}=\\frac34 S_{XED_1}$.\n\n'
            f'В треугольнике $XA_1D_1$ ($\\angle A_1=90^\\circ$): $XA_1={tx(2 * P)}$, $A_1D_1={q}$, $XD_1={tx(xd1)}$, высота '
            f'$A_1H=\\frac{{XA_1\\cdot A_1D_1}}{{XD_1}}={tx(sp.radsimp(a1h))}$. По теореме о трёх перпендикулярах $EH\\perp XD_1$, '
            f'$EH=\\sqrt{{A_1E^2+A_1H^2}}=\\sqrt{{{tx(e ** 2)}+{tx(sp.nsimplify(a1h ** 2))}}}={tx(sp.radsimp(eh))}$.\n\n'
            f'$$S_{{EFTD_1}}=\\frac34\\cdot\\frac12\\cdot XD_1\\cdot EH=\\frac38\\cdot {tx(xd1)}\\cdot {tx(sp.radsimp(eh))}={tx(s)}.$$')

    def figure(self, p):
        pts, E, F, T = self._pts(p)
        return g.draw(pts, extra={'E': E, 'F': F, 'T': T}, section_names=['E', 'F', 'T', 'D1'], elev=20)

    def sample(self, rng):
        m, n = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3), (3, 2), (2, 3), (3, 1)])
        k = 2 * (m + n)
        h = k * rng.randint(1, max(1, 18 // k))
        P = rng.choice(['2', '3', '4', '6', 'sqrt(2)', '2*sqrt(2)', '3*sqrt(2)', 'sqrt(3)', '2*sqrt(3)'])
        return dict(p=P, q=rng.choice([2, 3, 4, 6, 8, 10, 12]), h=h, m=m, n=n, ask=rng.choice(['angle', 'area']))


class RectPyramidCEF(Solved):
    """Пирамида с прямоугольником в основании и равными боковыми рёбрами: плоскость CEF ∥ SB"""
    number, topic = 14, DIST
    fipi = {'EA6B32': dict(ab=5, bd=9, s=5)}

    def _pts(self, p):
        ab, bd, s = map(float, (p['ab'], p['bd'], p['s']))
        ad = math.sqrt(bd * bd - ab * ab)
        A, B, C, D = (0.0, 0.0, 0.0), (ab, 0.0, 0.0), (ab, ad, 0.0), (0.0, ad, 0.0)
        O = g.centroid(A, B, C, D)
        Sv = (O[0], O[1], math.sqrt(s * s - bd * bd / 4))
        k = bd - s
        E = g.lerp(B, D, k / bd)
        F = g.lerp(Sv, A, k / s)
        return {'S': Sv, 'A': A, 'B': B, 'C': C, 'D': D}, E, F

    def answer(self, p):
        bd, s = p['bd'], p['s']
        return Answer.num(sp.radsimp(r(s, bd) * S(sp.Integer(s) ** 2 - r(bd ** 2, 4))))

    def check(self, p):
        pts, E, F = self._pts(p)
        pl = g.plane(pts['C'], E, F)
        assert abs(g.dot(pl[0], g.sub(pts['B'], pts['S']))) < 1e-9
        Q = g.line_plane(pts['S'], pts['D'], pl)
        return Q[2]

    def condition(self, p):
        k = p['bd'] - p['s']
        return (f'В основании пирамиды $SABCD$ лежит прямоугольник $ABCD$ со стороной $AB={p["ab"]}$ и диагональю $BD={p["bd"]}$, '
                f'все боковые рёбра пирамиды равны ${p["s"]}$. На диагонали $BD$ отмечена точка $E$, на ребре $AS$ — точка $F$, '
                f'причём $SF=BE={k}$.\n\nа) Докажите, что плоскость $CEF$ параллельна ребру $SB$.\n\n'
                'б) Плоскость $CEF$ пересекает ребро $SD$ в точке $Q$. Найдите расстояние от точки $Q$ до плоскости $ABC$.')

    def solution(self, p):
        ab, bd, s = p['ab'], p['bd'], p['s']
        k = bd - s
        gb = r(ab * k, bd - k)
        so = S(sp.Integer(s) ** 2 - r(bd ** 2, 4))
        return (
            f'а) $ED=BD-BE={bd - k}$. Пусть прямая $CE$ пересекает прямую $AB$ в точке $G$. Треугольники $GBE$ и $CDE$ подобны '
            f'($AB\\parallel CD$): $\\frac{{GB}}{{CD}}=\\frac{{BE}}{{ED}}=\\frac{{{k}}}{{{bd - k}}}$, $GB={tx(gb)}$, '
            f'$AG=AB-GB={tx(ab - gb)}$. Значит, $AG:GB={tx(ab - gb)}:{tx(gb)}={s - k}:{k}$. '
            f'Но и $AF:FS=(AS-SF):SF={s - k}:{k}$. По теореме, обратной теореме о пропорциональных отрезках, $FG\\parallel SB$. '
            'Прямая $FG$ лежит в плоскости $CEF$, поэтому плоскость $CEF$ параллельна $SB$.\n\n'
            'б) Плоскость $SBD$ содержит прямую $SB$, параллельную плоскости $CEF$, поэтому пересекает её по прямой $EQ\\parallel SB$. '
            f'Тогда $\\frac{{DQ}}{{DS}}=\\frac{{DE}}{{DB}}=\\frac{{{s}}}{{{bd}}}$.\n\n'
            'Боковые рёбра равны, поэтому высота $SO$ пирамиды падает в центр $O$ прямоугольника (точку пересечения диагоналей): '
            f'$SO=\\sqrt{{SB^2-OB^2}}=\\sqrt{{{s ** 2}-{tx(r(bd ** 2, 4))}}}={tx(so)}$. Расстояние от $Q$ до плоскости основания '
            f'$$\\frac{{DQ}}{{DS}}\\cdot SO=\\frac{{{s}}}{{{bd}}}\\cdot {tx(so)}={tx(sp.radsimp(r(s, bd) * so))}.$$')

    def figure(self, p):
        pts, E, F = self._pts(p)
        pl = g.plane(pts['C'], E, F)
        Q = g.line_plane(pts['S'], pts['D'], pl)
        return g.draw(pts, extra={'E': E, 'F': F, 'Q': Q}, segments=[('B', 'D'), ('C', 'E'), ('E', 'Q')],
                      section_names=[], azim=125, elev=22)

    def sample(self, rng):
        bd = rng.randint(6, 14)
        s = rng.randint(bd // 2 + 1, bd - 1)
        ab = rng.randint(bd // 3 + 1, bd * 4 // 5)
        return dict(ab=ab, bd=bd, s=s)


class QuadPyramidCKM(Solved):
    """Правильная четырёхугольная пирамида: M на AB, K на SB, проекция K лежит на CM"""
    number, topic = 14, SECTIONS
    fipi = {'03B44B': dict(a=8, s=7, u=2, v=1, ask='volume'), '3C8708': dict(a=8, s=7, u=2, v=1, ask='area')}

    def _pts(self, p):
        pts = quad_pyramid(p['a'], p['s'])
        M = g.lerp(pts['A'], pts['B'], p['u'] / p['a'])
        K = g.lerp(pts['S'], pts['B'], p['v'] / p['s'])
        return pts, M, K

    def _vals(self, p):
        a, s, u = sp.Integer(p['a']), sp.Integer(p['s']), sp.Integer(p['u'])
        lam = 2 * (a - u) / (2 * a - u)
        so = S(s ** 2 - a ** 2 / 2)
        kk = lam * so
        return a, s, u, lam, so, kk

    def answer(self, p):
        a, s, u, lam, so, kk = self._vals(p)
        if p['ask'] == 'volume':
            return Answer.num(sp.radsimp(r(1, 3) * (a - u) * a / 2 * kk))
        cm = S((a - u) ** 2 + a ** 2)
        return Answer.num(sp.radsimp(cm * kk / 2))

    def check(self, p):
        pts, M, K = self._pts(p)
        pl = g.plane(M, K, pts['C'])
        assert g.perpendicular(pl[0], (0, 0, 1))
        if p['ask'] == 'volume':
            return g.volume([pts['B'], pts['C'], K, M])
        return g.polygon_area(g.section(list(pts.values()), pl))

    def condition(self, p):
        a, s, u, v = p['a'], p['s'], p['u'], p['v']
        if p['ask'] == 'volume':
            return (f'В правильной четырёхугольной пирамиде $SABCD$ сторона основания равна ${a}$, боковое ребро равно ${s}$. '
                    f'На рёбрах $AB$ и $SB$ отмечены точки $M$ и $K$, причём $AM={u}$, $SK={tx(sp.nsimplify(v))}$.\n\n'
                    'а) Докажите, что плоскость $CKM$ перпендикулярна плоскости $ABC$.\n\nб) Найдите объём пирамиды $BCKM$.')
        return (f'В правильной четырёхугольной пирамиде $SABCD$ сторона основания равна ${a}$, боковое ребро равно ${s}$. '
                f'На рёбрах $AB$ и $SB$ отмечены точки $M$ и $K$, причём $AM={u}$, $SK={tx(sp.nsimplify(v))}$. Плоскость $\\alpha$ '
                'перпендикулярна плоскости $ABC$ и содержит точки $M$ и $K$.\n\n'
                'а) Докажите, что плоскость $\\alpha$ содержит точку $C$.\n\nб) Найдите площадь сечения пирамиды плоскостью $\\alpha$.')

    def solution(self, p):
        a, s, u, lam, so, kk = self._vals(p)
        v = sp.nsimplify(p['v'])
        bm = a - u
        ratio_kb = (s - v) / s
        pre = (f'Пусть $O$ — центр основания, $SO$ — высота пирамиды, $K\'$ — проекция точки $K$ на плоскость основания; '
               f'$K\'$ лежит на $BO$ и $\\frac{{BK\'}}{{BO}}=\\frac{{BK}}{{BS}}=\\frac{{{tx(s - v)}}}{{{s}}}$.\n\n'
               f'Пусть прямая $CM$ пересекает диагональ $BD$ в точке $P$. Треугольники $PBM$ и $PDC$ подобны ($BM\\parallel DC$): '
               f'$\\frac{{BP}}{{PD}}=\\frac{{BM}}{{DC}}=\\frac{{{bm}}}{{{a}}}$, откуда $BP=\\frac{{{bm}}}{{{bm + a}}}BD$ и '
               f'$\\frac{{BP}}{{BO}}=\\frac{{{2 * bm}}}{{{bm + a}}}={tx(lam)}$. Так как и $\\frac{{BK\'}}{{BO}}={tx(ratio_kb)}$, точки $P$ и $K\'$ '
               'совпадают: проекция точки $K$ лежит на прямой $CM$.\n\n')
        if p['ask'] == 'volume':
            vol = sp.radsimp(r(1, 3) * bm * a / 2 * kk)
            return ('а) ' + pre +
                    'Значит, $KK\'$ лежит в плоскости $CKM$, а $KK\'\\perp ABC$, поэтому плоскости $CKM$ и $ABC$ перпендикулярны.\n\n'
                    f'б) $SO=\\sqrt{{SA^2-\\frac{{AC^2}}{{4}}}}=\\sqrt{{{s ** 2}-{tx(a ** 2 / 2)}}}={tx(so)}$, '
                    f'$KK\'=\\frac{{BK}}{{BS}}\\cdot SO={tx(kk)}$. $S_{{BCM}}=\\frac12\\cdot BM\\cdot BC=\\frac12\\cdot {bm}\\cdot {a}={tx(bm * a / 2)}$.\n\n'
                    f'$$V_{{BCKM}}=\\frac13 S_{{BCM}}\\cdot KK\'=\\frac13\\cdot {tx(bm * a / 2)}\\cdot {tx(kk)}={tx(vol)}.$$')
        cm = S(bm ** 2 + a ** 2)
        return ('а) ' + pre +
                'Плоскость, перпендикулярная основанию и проходящая через $K$, содержит перпендикуляр $KK\'$, поэтому $\\alpha$ проходит '
                'через $M$ и $K\'$, то есть пересекает основание по прямой $MK\'$ — это прямая $CM$. Значит, $C\\in\\alpha$.\n\n'
                'б) Прямая $CM$ пересекает основание по отрезку $CM$, пересекающему диагональ $BD$ между $B$ и $O$, поэтому сечение — '
                'треугольник $CKM$ с высотой $KK\'$.\n\n'
                f'$SO=\\sqrt{{{s ** 2}-{tx(a ** 2 / 2)}}}={tx(so)}$, $KK\'={tx(ratio_kb)}\\cdot SO={tx(kk)}$, '
                f'$CM=\\sqrt{{BM^2+BC^2}}=\\sqrt{{{bm ** 2}+{a ** 2}}}={tx(cm)}$.\n\n'
                f'$$S_{{CKM}}=\\frac12\\cdot CM\\cdot KK\'=\\frac12\\cdot {tx(cm)}\\cdot {tx(kk)}={tx(sp.radsimp(cm * kk / 2))}.$$')

    def figure(self, p):
        pts, M, K = self._pts(p)
        return g.draw(pts, extra={'M': M, 'K': K}, section_names=['M', 'K', 'C'], segments=[('B', 'D')], azim=140)

    def sample(self, rng):
        a = rng.choice([4, 6, 8, 10, 12])
        u = rng.randint(1, a - 1)
        s = rng.randint(math.floor(a / math.sqrt(2)) + 1, a + 6)
        v = sp.Rational(s * u, 2 * a - u)
        if v.q > 2:
            return None
        return dict(a=a, s=s, u=u, v=float(v) if v.q != 1 else int(v), ask=rng.choice(['volume', 'area']))


def _hex_n(p):
    """Середина N отрезка MD в правильном шестиугольнике (AM = u): ON = u/2 по лучу OC"""
    a, u = sp.Integer(p['a']), sp.nsimplify(p['u'])
    return a, u, u / 2, a - u / 2


class HexPyramidKMKD(Solved):
    """Шестиугольная пирамида: α ⊥ основанию через M и D пересекает SC в K ⇒ KM = KD"""
    number, topic = 14, VOLUMES
    fipi = {'9A3AF9': dict(a=2, s=8, u=1)}

    def _pts(self, p):
        pts = hex_pyramid(p['a'], p['s'])
        M = g.lerp(pts['A'], pts['B'], float(p['u']) / p['a'])
        N = g.mid(M, pts['D'])
        K = g.lerp(pts['C'], pts['S'], (p['a'] - N[0]) / p['a'])
        return pts, M, K

    def _vol(self, p):
        a, u, on, cn = _hex_n(p)
        so = S(sp.Integer(p['s']) ** 2 - a ** 2)
        kk = cn / a * so
        area = cn * a * S(3) / 2     # S_CDN + S_CMN = ½·CN·(h_D + h_M), h_D = h_M = a√3/2
        return so, kk, sp.radsimp(area), sp.radsimp(area * kk / 3)

    def answer(self, p):
        return Answer.num(self._vol(p)[3])

    def check(self, p):
        pts, M, K = self._pts(p)
        pl = g.plane_pv(M, g.sub(pts['D'], M), (0, 0, 1))
        K2 = g.line_plane(pts['S'], pts['C'], pl)
        assert g.close(g.dist(K2, M), g.dist(K2, pts['D']))
        return g.volume([pts['C'], pts['D'], K2, M])

    def condition(self, p):
        return (f'В правильной шестиугольной пирамиде $SABCDEF$ сторона основания равна ${p["a"]}$, боковое ребро равно ${p["s"]}$. '
                'Точка $M$ — середина ребра $AB$. Плоскость $\\alpha$ перпендикулярна плоскости $ABC$ и содержит точки $M$ и $D$. '
                'Прямая $SC$ пересекает плоскость $\\alpha$ в точке $K$.\n\n'
                'а) Докажите, что $KM=KD$.\n\nб) Найдите объём пирамиды $CDKM$.')

    def solution(self, p):
        a, u, on, cn = _hex_n(p)
        so, kk, area, vol = self._vol(p)
        return (
            'а) Пусть $O$ — центр основания. В правильном шестиугольнике прямые $AB$ и $ED$ параллельны диагонали $FC$ и удалены от неё '
            'на одно и то же расстояние (высоту правильного треугольника $AOB$), причём лежат по разные стороны от $FC$. Поэтому прямая '
            '$FC$ проходит через середину $N$ отрезка $MD$.\n\n'
            'Проекция $K\'$ точки $K$ на основание лежит на $OC$ (проекции прямой $SC$) и на $MD$ (так как $\\alpha\\perp ABC$), '
            'значит, $K\'=N$ — середина $MD$. Прямоугольные треугольники $KNM$ и $KND$ равны по двум катетам, откуда $KM=KD$.\n\n'
            f'б) Направим ось $Ox$ по лучу $OC$. Проекции точек $M$ и $D$ на прямую $FC$ имеют абсциссы ${tx(u - a / 2)}$ и ${tx(a / 2)}$, '
            f'поэтому абсцисса середины $N$ равна ${tx(on)}$, $CN={tx(cn)}$. $SO=\\sqrt{{SC^2-OC^2}}=\\sqrt{{{p["s"] ** 2}-{a ** 2}}}={tx(so)}$, '
            f'$KN=SO\\cdot\\frac{{CN}}{{CO}}={tx(kk)}$.\n\n'
            f'Отрезок $CN$ делит треугольник $CDM$ на треугольники $CDN$ и $CMN$ с общим основанием $CN$ и высотами, равными расстояниям '
            f'от $D$ и $M$ до прямой $FC$, то есть ${tx(a * S(3) / 2)}$: $S_{{CDM}}=\\frac12\\cdot {tx(cn)}\\cdot {tx(a * S(3))}={tx(area)}$.\n\n'
            f'$$V_{{CDKM}}=\\frac13 S_{{CDM}}\\cdot KN=\\frac13\\cdot {tx(area)}\\cdot {tx(kk)}={tx(vol)}.$$')

    def figure(self, p):
        pts, M, K = self._pts(p)
        return g.draw(pts, extra={'M': M, 'K': K}, section_names=['M', 'K', 'D'], segments=[('C', 'M')], azim=-20, elev=20)

    def sample(self, rng):
        a = rng.choice([2, 4, 6, 8])
        return dict(a=a, s=rng.randint(a + 1, a + 9), u=a // 2)


class HexPyramidPerp(Solved):
    """Шестиугольная пирамида: K на SC и KM = KD ⇒ плоскость DKM перпендикулярна основанию"""
    number, topic = 14, SECTIONS
    fipi = {'065E0A': dict(a=5, s=9, u=1)}

    def _vals(self, p):
        a, u, on, cn = _hex_n(p)
        so = S(sp.Integer(p['s']) ** 2 - a ** 2)
        kk = cn / a * so
        md = S((a - u) ** 2 + 3 * a ** 2)   # MD² = (Δx)² + (a√3)²
        return a, u, on, cn, so, kk, md

    def answer(self, p):
        *_, kk, md = self._vals(p)
        return Answer.num(sp.radsimp(md * kk / 2))

    def check(self, p):
        pts = hex_pyramid(p['a'], p['s'])
        M = g.lerp(pts['A'], pts['B'], float(p['u']) / p['a'])
        D = pts['D']
        # K на SC с KM = KD: перебор по параметру (функция монотонна)
        lo, hi = 0.0, 1.0
        f = lambda t: g.dist(g.lerp(pts['C'], pts['S'], t), M) - g.dist(g.lerp(pts['C'], pts['S'], t), D)
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(lo) * f(mid) <= 0:
                hi = mid
            else:
                lo = mid
        K = g.lerp(pts['C'], pts['S'], lo)
        assert g.perpendicular(g.plane(D, K, M)[0], (0, 0, 1))
        return g.polygon_area([D, K, M])

    def condition(self, p):
        return (f'В правильной шестиугольной пирамиде $SABCDEF$ сторона основания равна ${p["a"]}$, боковое ребро равно ${p["s"]}$. '
                f'Точка $M$ лежит на ребре $AB$, $AM={tx(sp.nsimplify(p["u"]))}$, а точка $K$ — на ребре $SC$, причём $MK=KD$.\n\n'
                'а) Докажите, что плоскость $DKM$ перпендикулярна плоскости $ABC$.\n\nб) Найдите площадь треугольника $DKM$.')

    def solution(self, p):
        a, u, on, cn, so, kk, md = self._vals(p)
        return (
            'а) Пусть $O$ — центр основания, $K\'$ — проекция $K$ на основание; $K\'$ лежит на $OC$. Так как $KM=KD$, наклонные равны, '
            'и равны их проекции: $K\'M=K\'D$, то есть $K\'$ лежит на серединном перпендикуляре к $MD$.\n\n'
            'Прямые $AB$ и $ED$ параллельны диагонали $FC$ и удалены от неё на одно и то же расстояние по разные стороны, поэтому '
            '$FC$ проходит через середину $N$ отрезка $MD$. Серединный перпендикуляр к $MD$ и прямая $FC$ — разные прямые '
            '($MD$ не перпендикулярна $FC$), пересекаются они в точке $N$. Значит, $K\'=N$ лежит на $MD$, перпендикуляр $KK\'$ '
            'лежит в плоскости $DKM$, и эта плоскость перпендикулярна основанию.\n\n'
            f'б) Направим ось $Ox$ по лучу $OC$. Проекции $M$ и $D$ на $FC$ имеют абсциссы ${tx(u - a / 2)}$ и ${tx(a / 2)}$, поэтому '
            f'абсцисса точки $N$ равна ${tx(on)}$, $CN={tx(cn)}$. $SO=\\sqrt{{SC^2-OC^2}}=\\sqrt{{{p["s"] ** 2}-{a ** 2}}}={tx(so)}$, $KN=SO\\cdot\\frac{{CN}}{{CO}}={tx(kk)}$.\n\n'
            f'Расстояние между проекциями $M$ и $D$ на $FC$ равно ${tx(a - u)}$, а расстояние между прямыми $AB$ и $ED$ — ${tx(a * S(3))}$, '
            f'поэтому $MD=\\sqrt{{{tx((a - u) ** 2)}+{tx(3 * a ** 2)}}}={tx(md)}$.\n\n'
            f'$$S_{{DKM}}=\\frac12\\cdot MD\\cdot KN=\\frac12\\cdot {tx(md)}\\cdot {tx(kk)}={tx(sp.radsimp(md * kk / 2))}.$$')

    def figure(self, p):
        pts = hex_pyramid(p['a'], p['s'])
        M = g.lerp(pts['A'], pts['B'], float(p['u']) / p['a'])
        N = g.mid(M, pts['D'])
        K = g.lerp(pts['C'], pts['S'], (p['a'] - N[0]) / p['a'])
        return g.draw(pts, extra={'M': M, 'K': K}, section_names=['M', 'K', 'D'], azim=-20, elev=20)

    def sample(self, rng):
        a = rng.choice([2, 3, 4, 5, 6])
        return dict(a=a, s=rng.randint(a + 1, a + 8), u=rng.randint(1, a - 1) if a > 2 else 1)


class PrismCentroidCMN(Solved):
    """Правильная призма, AM = BN: ось OO₁ проходит через центроид CMN; расстояние от C₁ до CMN"""
    number, topic = 14, DIST
    fipi = {'F416AF': dict(a=6, h=4, k=3)}

    def _pts(self, p):
        pts = prism(tri_base(p['a']), p['h'])
        M = (*pts['A'][:2], float(p['k']))
        N = (*pts['B'][:2], float(p['k']))
        return pts, M, N

    def _d(self, p):
        a, h, k = (sp.Integer(p[x]) for x in ('a', 'h', 'k'))
        ch = a * S(3) / 2
        return ch, sp.radsimp(h * ch / S(ch ** 2 + k ** 2))

    def answer(self, p):
        return Answer.num(self._d(p)[1])

    def check(self, p):
        pts, M, N = self._pts(p)
        G = g.centroid(pts['C'], M, N)
        O = g.centroid(pts['A'], pts['B'], pts['C'])
        assert abs(G[0] - O[0]) < 1e-9 and abs(G[1] - O[1]) < 1e-9 and 0 <= G[2] <= p['h']
        return g.dist_point_plane(pts['C1'], g.plane(pts['C'], M, N))

    def condition(self, p):
        return (f'В правильной треугольной призме $ABCA_1B_1C_1$ сторона основания равна ${p["a"]}$, боковое ребро равно ${p["h"]}$. '
                f'На рёбрах $AA_1$ и $BB_1$ отмечены точки $M$ и $N$, причём $AM=BN={p["k"]}$.\n\n'
                'а) Точки $O$ и $O_1$ — центры окружностей, описанных около треугольников $ABC$ и $A_1B_1C_1$. Докажите, что прямая '
                '$OO_1$ содержит точку пересечения медиан треугольника $CMN$.\n\n'
                'б) Найдите расстояние от точки $C_1$ до плоскости $CMN$.')

    def solution(self, p):
        a, h, k = p['a'], p['h'], p['k']
        ch, d = self._d(p)
        cp = S(ch ** 2 + k ** 2)
        return (
            'а) В правильном треугольнике центр описанной окружности совпадает с точкой пересечения медиан, поэтому $O$ — центроид '
            '$ABC$, а $OO_1$ — прямая, перпендикулярная основаниям. Пусть $H$ и $P$ — середины $AB$ и $MN$. Так как $AM=BN$ и '
            '$AM\\parallel BN$, $ABNM$ — прямоугольник, $PH\\parallel AA_1$, $PH=AM$.\n\n'
            'Точка $G$ пересечения медиан треугольника $CMN$ лежит на медиане $CP$ и $CG:GP=2:1$. Её проекция на основание лежит '
            'на проекции $CH$ отрезка $CP$ и делит $CH$ в том же отношении $2:1$, то есть совпадает с центроидом $O$. Значит, $G$ '
            'лежит на перпендикуляре $OO_1$ к основанию.\n\n'
            'б) $MN\\perp CH$ и $MN\\perp PH$, поэтому $MN$ перпендикулярна плоскости $CHP$ (она же содержит $CC_1$), и плоскость '
            '$CMN$ перпендикулярна плоскости $CC_1H$. Искомое расстояние — расстояние от $C_1$ до прямой $CP$ в плоскости $CC_1H$.\n\n'
            f'$CH={tx(ch)}$, $PH={k}$, $CP=\\sqrt{{{tx(ch ** 2)}+{k ** 2}}}={tx(cp)}$. Угол $C_1CP$ равен углу $CPH$ '
            f'(накрест лежащие при $CC_1\\parallel HP$), $\\sin\\angle CPH=\\frac{{CH}}{{CP}}$.\n\n'
            f'$$d=CC_1\\cdot\\sin\\angle C_1CP={h}\\cdot\\frac{{{tx(ch)}}}{{{tx(cp)}}}={tx(d)}.$$')

    def figure(self, p):
        pts, M, N = self._pts(p)
        return g.draw(pts, extra={'M': M, 'N': N}, section_names=['M', 'N', 'C'], elev=30)

    def sample(self, rng):
        a = rng.choice([2, 4, 6, 8, 10, 12])
        h = rng.randint(2, 12)
        return dict(a=a, h=h, k=rng.randint(1, h))


def _circle_pt(R, deg, z=0.0):
    return (R * math.cos(math.radians(deg)), R * math.sin(math.radians(deg)), z)


class CylinderABC1(Solved):
    """Цилиндр: A, B внизу, B₁, C₁ вверху, BB₁ — образующая, AC₁ пересекает ось ⇒ ∠ABC₁ = 90°"""
    number, topic = 14, BODIES
    fipi = {'416B0F': dict(ab=20, h=15, bc=21, ask='lateral'), '13D60B': dict(ab=7, h=24, bc=10, ask='volume'),
            '77C190': dict(ab=6, h=15, bc=8, ask='angle'), '8EBB9F': dict(ab=21, h=12, bc=16, ask='dist')}
    QUESTION = {'lateral': 'площадь боковой поверхности цилиндра', 'volume': 'объём цилиндра',
                'angle': 'угол между прямыми $BB_1$ и $AC_1$', 'dist': 'расстояние от точки $B$ до прямой $AC_1$'}

    def _pts(self, p):
        d = math.hypot(p['ab'], p['bc'])
        R = d / 2
        delta = math.degrees(2 * math.asin(p['ab'] / d))
        A, C = _circle_pt(R, 200), _circle_pt(R, 20)
        B = _circle_pt(R, 200 - delta)
        return R, {'A': A, 'B': B, 'C': C, 'B1': (B[0], B[1], p['h']), 'C1': (C[0], C[1], p['h'])}

    def _ans(self, p):
        ab, h, bc = (sp.Integer(p[k]) for k in ('ab', 'h', 'bc'))
        d2 = ab ** 2 + bc ** 2
        if p['ask'] == 'lateral':
            return Answer.num(sp.pi * S(d2) * h)
        if p['ask'] == 'volume':
            return Answer.num(sp.pi * d2 / 4 * h)
        if p['ask'] == 'angle':
            return Answer.angle(sp.radsimp(S(d2) / h))
        bc1 = S(bc ** 2 + h ** 2)
        return Answer.num(sp.radsimp(ab * bc1 / S(ab ** 2 + bc1 ** 2)))

    def answer(self, p):
        return self._ans(p)

    def check(self, p):
        R, P = self._pts(p)
        assert g.perpendicular(g.sub(P['A'], P['B']), g.sub(P['C1'], P['B']))
        if p['ask'] == 'lateral':
            return 2 * math.pi * R * p['h']
        if p['ask'] == 'volume':
            return math.pi * R * R * p['h']
        if p['ask'] == 'angle':
            return g.angle_lines(g.sub(P['B1'], P['B']), g.sub(P['C1'], P['A']))
        return g.dist_point_line(P['B'], P['A'], P['C1'])

    def condition(self, p):
        return ('В цилиндре образующая перпендикулярна плоскости основания. На окружности одного основания взяты точки $A$ и $B$, '
                'на окружности другого — точки $B_1$ и $C_1$, причём $BB_1$ — образующая, а отрезок $AC_1$ пересекает ось цилиндра.\n\n'
                'а) Докажите, что $\\angle ABC_1=90^\\circ$.\n\n'
                f'б) Найдите {self.QUESTION[p["ask"]]}, если $AB={p["ab"]}$, $BB_1={p["h"]}$, $B_1C_1={p["bc"]}$.')

    def solution(self, p):
        ab, h, bc = p['ab'], p['h'], p['bc']
        d2 = ab ** 2 + bc ** 2
        d = S(d2)
        t = ('а) Пусть $C$ — проекция точки $C_1$ на плоскость нижнего основания ($CC_1$ — образующая), $O$ — центр нижнего основания. '
             'Ось цилиндра проецируется в точку $O$, поэтому проекция $AC$ отрезка $AC_1$ проходит через $O$: $AC$ — диаметр, '
             'и вписанный угол $ABC$ прямой. $BC$ — проекция наклонной $BC_1$, $AB\\perp BC$, по теореме о трёх перпендикулярах '
             '$AB\\perp BC_1$, то есть $\\angle ABC_1=90^\\circ$.\n\n'
             f'б) $BC=B_1C_1={bc}$ ($BCC_1B_1$ — прямоугольник), диаметр основания $AC=\\sqrt{{AB^2+BC^2}}=\\sqrt{{{ab ** 2}+{bc ** 2}}}={tx(d)}$.\n\n')
        a = self._ans(p)
        if p['ask'] == 'lateral':
            return t + f'$$S_{{\\text{{бок}}}}=\\pi\\cdot AC\\cdot BB_1=\\pi\\cdot {tx(d)}\\cdot {h}={a.display.strip("$")}.$$'
        if p['ask'] == 'volume':
            return t + (f'$$V=\\pi\\left(\\frac{{AC}}{{2}}\\right)^2\\cdot BB_1=\\pi\\cdot\\frac{{{d2}}}{{4}}\\cdot {h}='
                        f'{a.display.strip("$")}.$$')
        if p['ask'] == 'angle':
            return t + ('$BB_1\\parallel CC_1$, поэтому искомый угол равен углу $AC_1C$ прямоугольного треугольника $ACC_1$: '
                        f'$$\\operatorname{{tg}}\\angle AC_1C=\\frac{{AC}}{{CC_1}}=\\frac{{{tx(d)}}}{{{h}}}.$$ Угол равен {a.display}.')
        bc1 = S(bc ** 2 + h ** 2)
        ac1 = S(ab ** 2 + bc1 ** 2)
        return t + (f'Треугольник $ABC_1$ прямоугольный (пункт а): $BC_1=\\sqrt{{BC^2+CC_1^2}}=\\sqrt{{{bc ** 2}+{h ** 2}}}={tx(bc1)}$, '
                    f'$AC_1=\\sqrt{{AB^2+BC_1^2}}={tx(ac1)}$. Расстояние от $B$ до $AC_1$ — высота, проведённая к гипотенузе:\n\n'
                    f'$$d=\\frac{{AB\\cdot BC_1}}{{AC_1}}=\\frac{{{ab}\\cdot {tx(bc1)}}}{{{tx(ac1)}}}={a.display.strip("$")}.$$')

    def figure(self, p):
        R, P = self._pts(p)
        segs = [('A', 'B', False), ('B', 'B1', False), ('B1', 'C1', False), ('A', 'C1', True), ('C', 'C1', True),
                ('A', 'C', True), ('B', 'C', True), ('B', 'C1', True)]
        return g.draw_round(R, p['h'], points=P, segments=segs)

    def sample(self, rng):
        a, b, c = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (7, 24, 25), (9, 12, 15), (20, 21, 29),
                              (12, 16, 20), (2, 3, None), (4, 6, None), (1, 2, None), (3, 3, None)])
        if rng.random() < 0.5:
            a, b = b, a
        return dict(ab=a, bc=b, h=rng.randint(2, 20), ask=rng.choice(list(self.QUESTION)))


class CylinderACB(Solved):
    """Цилиндр: AC — диаметр, CC₁ — образующая, угол между AC₁ и BC табличный"""
    number, topic = 14, BODIES
    fipi = {'C84642': dict(gamma=45, ab='2*sqrt(3)', cc='2*sqrt(6)', ask='dist'),
            'D7147A': dict(gamma=30, ab='sqrt(2)', cc=2, ask='volume'),
            'E8FAA5': dict(gamma=30, ab=1, cc='2*sqrt(2)', ask='lateral')}
    QUESTION = {'dist': 'расстояние от точки $B$ до прямой $AC_1$', 'volume': 'объём цилиндра',
                'lateral': 'площадь боковой поверхности цилиндра'}

    def _v(self, p):
        gm = sp.rad(p['gamma'])
        ab, cc = sp.sympify(p['ab']), sp.sympify(p['cc'])
        ac = sp.radsimp(ab / sp.sin(gm))
        bc = sp.radsimp(ac * sp.cos(gm))
        ac1 = sp.radsimp(S(ac ** 2 + cc ** 2))
        phi = sp.acos(sp.radsimp(bc / ac1))
        return ab, cc, ac, bc, ac1, phi

    def _pts(self, p):
        ab, cc, ac, bc, ac1, phi = (float(x) for x in self._v(p))
        R = ac / 2
        A, C = _circle_pt(R, 200), _circle_pt(R, 20)
        B = _circle_pt(R, 200 - 2 * p['gamma'])   # ∠ACB = γ ⇒ центральный ∠AOB = 2γ
        return R, {'A': A, 'B': B, 'C': C, 'C1': (C[0], C[1], cc)}

    def answer(self, p):
        ab, cc, ac, bc, ac1, phi = self._v(p)
        if p['ask'] == 'dist':
            bc1 = S(bc ** 2 + cc ** 2)
            return Answer.num(sp.radsimp(ab * bc1 / ac1))
        if p['ask'] == 'volume':
            return Answer.num(sp.pi * ac ** 2 / 4 * cc)
        return Answer.num(sp.radsimp(sp.pi * ac * cc))

    def check(self, p):
        R, P = self._pts(p)
        phi = g.angle_lines(g.sub(P['C1'], P['A']), g.sub(P['C'], P['B']))
        assert g.close(phi, float(self._v(p)[5]))
        if p['ask'] == 'dist':
            return g.dist_point_line(P['B'], P['A'], P['C1'])
        if p['ask'] == 'volume':
            return math.pi * R * R * float(sp.sympify(p['cc']))
        return 2 * math.pi * R * float(sp.sympify(p['cc']))

    def condition(self, p):
        ab, cc, ac, bc, ac1, phi = self._v(p)
        return ('В цилиндре образующая перпендикулярна плоскости основания. На окружности одного основания взяты точки $A$, $B$ и $C$, '
                'на окружности другого — точка $C_1$, причём $CC_1$ — образующая, а $AC$ — диаметр основания. Известно, что '
                f'$\\angle ACB={p["gamma"]}^\\circ$, $AB={tx(ab)}$, $CC_1={tx(cc)}$.\n\n'
                f'а) Докажите, что угол между прямыми $AC_1$ и $BC$ равен ${tx(phi * 180 / sp.pi)}^\\circ$.\n\n'
                f'б) Найдите {self.QUESTION[p["ask"]]}.')

    def solution(self, p):
        ab, cc, ac, bc, ac1, phi = self._v(p)
        gm = p['gamma']
        t = ('а) $AC$ — диаметр, поэтому $\\angle ABC=90^\\circ$. '
             f'$AC=\\frac{{AB}}{{\\sin {gm}^\\circ}}={tx(ac)}$, $BC=AC\\cos {gm}^\\circ={tx(bc)}$, '
             f'$AC_1=\\sqrt{{AC^2+CC_1^2}}=\\sqrt{{{tx(ac ** 2)}+{tx(cc ** 2)}}}={tx(ac1)}$.\n\n'
             'Угол между прямыми $AC_1$ и $BC$ найдём через скалярное произведение. $\\overrightarrow{AC_1}=\\overrightarrow{AC}+\\overrightarrow{CC_1}$, $\\overrightarrow{CC_1}\\perp\\overrightarrow{BC}$, поэтому '
             '$\\overrightarrow{AC_1}\\cdot\\overrightarrow{BC}=\\overrightarrow{AC}\\cdot\\overrightarrow{BC}=AC\\cdot BC\\cos\\angle ACB=BC^2$ '
             '(в прямоугольном треугольнике $AC\\cos C=BC$).\n\n'
             f'$$\\cos\\varphi=\\frac{{BC^2}}{{AC_1\\cdot BC}}=\\frac{{BC}}{{AC_1}}=\\frac{{{tx(bc)}}}{{{tx(ac1)}}}={tx(sp.radsimp(bc / ac1))},$$ '
             f'значит, $\\varphi={tx(phi * 180 / sp.pi)}^\\circ$.\n\n')
        a = self.answer(p)
        if p['ask'] == 'dist':
            bc1 = S(bc ** 2 + cc ** 2)
            return t + ('б) $AB\\perp BC$ и $AB\\perp CC_1$, поэтому $AB$ перпендикулярна плоскости $BCC_1$ и $AB\\perp BC_1$. '
                        f'В прямоугольном треугольнике $ABC_1$: $BC_1=\\sqrt{{BC^2+CC_1^2}}={tx(bc1)}$, $AC_1={tx(ac1)}$; '
                        'расстояние от $B$ до $AC_1$ — высота к гипотенузе:\n\n'
                        f'$$d=\\frac{{AB\\cdot BC_1}}{{AC_1}}=\\frac{{{tx(ab)}\\cdot {tx(bc1)}}}{{{tx(ac1)}}}={a.display.strip("$")}.$$')
        if p['ask'] == 'volume':
            return t + (f'б) Радиус основания $R=\\frac{{AC}}{{2}}={tx(ac / 2)}$, высота $CC_1={tx(cc)}$:\n\n'
                        f'$$V=\\pi R^2\\cdot CC_1=\\pi\\cdot {tx(ac ** 2 / 4)}\\cdot {tx(cc)}={a.display.strip("$")}.$$')
        return t + (f'б) $$S_{{\\text{{бок}}}}=\\pi\\cdot AC\\cdot CC_1=\\pi\\cdot {tx(ac)}\\cdot {tx(cc)}={a.display.strip("$")}.$$')

    def figure(self, p):
        R, P = self._pts(p)
        segs = [('A', 'B', False), ('B', 'C', False), ('A', 'C', True), ('C', 'C1', True), ('A', 'C1', True)]
        return g.draw_round(R, float(sp.sympify(p['cc'])), points=P, segments=segs)

    def sample(self, rng):
        gm = rng.choice([30, 45, 60])
        phi = rng.choice([45, 60])
        bcv = rng.choice([1, 2, 3, 4, 6, 'sqrt(2)', 'sqrt(3)', '2*sqrt(3)', '2*sqrt(2)'])
        bc = sp.sympify(bcv)
        ac = bc / sp.cos(sp.rad(gm))
        ac1 = bc / sp.cos(sp.rad(phi))
        cc2 = sp.radsimp(ac1 ** 2 - ac ** 2)
        if cc2 <= 0:
            return None
        ab = sp.radsimp(ac * sp.sin(sp.rad(gm)))
        return dict(gamma=gm, ab=str(ab), cc=str(sp.radsimp(S(cc2))), ask=rng.choice(list(self.QUESTION)))


class ConeCos(Solved):
    """Конус, угол образующей с основанием 60°, AB — диаметр: cos∠ASC + cos∠BSC = 3/2"""
    number, topic = 14, BODIES
    fipi = {'6B5C41': dict(l=1, c='2/3')}

    def _v(self, p):
        l, c = sp.sympify(p['l']), sp.Rational(p['c'])
        c2 = r(3, 2) - c
        ac, bc = S(2 * l ** 2 * (1 - c)), S(2 * l ** 2 * (1 - c2))
        h = l * S(3) / 2
        return l, c, c2, ac, bc, h, sp.radsimp(ac * bc / 6 * h)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def _pts(self, p):
        l = float(sp.sympify(p['l']))
        R, h = l / 2, l * math.sqrt(3) / 2
        A, B = _circle_pt(R, 200), _circle_pt(R, 20)
        Sv = (0.0, 0.0, h)
        # C: cos∠ASC = c ⇒ AC² = 2l²(1 − c)
        ac = math.sqrt(2 * l * l * (1 - float(sp.Rational(p['c']))))
        ang = math.degrees(2 * math.asin(ac / (2 * R)))
        C = _circle_pt(R, 200 - ang)
        return R, h, {'S': Sv, 'A': A, 'B': B, 'C': C}

    def check(self, p):
        R, h, P = self._pts(p)
        cs = lambda X, Y: g.dot(g.sub(X, P['S']), g.sub(Y, P['S'])) / g.norm(g.sub(X, P['S'])) / g.norm(g.sub(Y, P['S']))  # noqa: E731
        assert g.close(cs(P['A'], P['C']) + cs(P['B'], P['C']), 1.5)
        return g.volume(list(P.values()))

    def condition(self, p):
        return ('Точки $A$, $B$ и $C$ лежат на окружности основания конуса с вершиной $S$, причём $AB$ — диаметр. Угол между '
                'образующей конуса и плоскостью основания равен $60^\\circ$.\n\n'
                'а) Докажите, что $\\cos\\angle ASC+\\cos\\angle BSC=1{,}5$.\n\n'
                f'б) Найдите объём тетраэдра $SABC$, если $SC={tx(sp.sympify(p["l"]))}$ и $\\cos\\angle ASC={tx(sp.Rational(p["c"]))}$.')

    def solution(self, p):
        l, c, c2, ac, bc, h, v = self._v(p)
        return (
            'а) Пусть $l$ — образующая, $R$ — радиус основания. Угол образующей с основанием $60^\\circ$, поэтому $R=l\\cos 60^\\circ=\\frac l2$, '
            '$AB=2R=l$. По теореме косинусов в равнобедренных треугольниках $ASC$ и $BSC$: '
            '$AC^2=2l^2(1-\\cos\\angle ASC)$, $BC^2=2l^2(1-\\cos\\angle BSC)$. Угол $ACB$ опирается на диаметр, $AC^2+BC^2=AB^2=l^2$:\n\n'
            '$$2l^2\\bigl(2-\\cos\\angle ASC-\\cos\\angle BSC\\bigr)=l^2\\ \\Rightarrow\\ \\cos\\angle ASC+\\cos\\angle BSC=2-\\frac12=1{,}5.$$\n\n'
            f'б) $l={tx(l)}$, $\\cos\\angle BSC=1{{,}}5-{tx(c)}={tx(c2)}$. $AC^2=2l^2(1-{tx(c)})={tx(ac ** 2)}$, '
            f'$BC^2=2l^2(1-{tx(c2)})={tx(bc ** 2)}$. Высота конуса $SO=l\\sin 60^\\circ={tx(h)}$ — она же высота тетраэдра.\n\n'
            f'$$V=\\frac13\\cdot\\frac12\\, AC\\cdot BC\\cdot SO=\\frac16\\cdot {tx(ac)}\\cdot {tx(bc)}\\cdot {tx(h)}={tx(v)}.$$')

    def figure(self, p):
        R, h, P = self._pts(p)
        segs = [('S', 'A', False), ('S', 'B', False), ('S', 'C', False), ('A', 'C', False), ('B', 'C', False), ('A', 'B', True)]
        return g.draw_round(R, h, apex=True, points=P, segments=segs)

    def sample(self, rng):
        c = rng.choice(['2/3', '3/4', '4/5', '5/6', '5/8', '7/8', '3/5'])
        return dict(l=rng.choice([1, 2, 3, 4, 6]), c=c)


class PrismAKC(Solved):
    """Правильная треугольная призма, K — середина A₁B₁: сечение AKC — равнобедренная трапеция; расстояние от B до AKC"""
    number, topic = 14, DIST
    fipi = {'6BFFF1': dict(a=4, h=4)}

    def _v(self, p):
        a, h = sp.Integer(p['a']), sp.Integer(p['h'])
        kh = S(h ** 2 + 3 * a ** 2 / 16)
        return a, h, kh, sp.radsimp(a * S(3) * h / (2 * kh))

    def answer(self, p):
        return Answer.num(self._v(p)[3])

    def check(self, p):
        pts = prism(tri_base(p['a']), p['h'])
        K = g.mid(pts['A1'], pts['B1'])
        pl = g.plane(pts['A'], K, pts['C'])
        sec = g.section(list(pts.values()), pl)
        assert len(sec) == 4
        return g.dist_point_plane(pts['B'], pl)

    def condition(self, p):
        return (f'В правильной треугольной призме $ABCA_1B_1C_1$ сторона основания равна ${p["a"]}$, боковое ребро равно ${p["h"]}$. '
                'Точка $K$ — середина ребра $A_1B_1$.\n\n'
                'а) Докажите, что сечение призмы плоскостью $AKC$ — равнобедренная трапеция.\n\n'
                'б) Найдите расстояние от точки $B$ до плоскости $AKC$.') if p['a'] != p['h'] else \
            (f'В правильной треугольной призме $ABCA_1B_1C_1$ все рёбра равны ${p["a"]}$. Точка $K$ — середина ребра $A_1B_1$.\n\n'
             'а) Докажите, что сечение призмы плоскостью $AKC$ — равнобедренная трапеция.\n\n'
             'б) Найдите расстояние от точки $B$ до плоскости $AKC$.')

    def solution(self, p):
        a, h, kh, d = self._v(p)
        sabc = a ** 2 * S(3) / 4
        return (
            'а) Плоскости оснований параллельны, поэтому плоскость $AKC$ пересекает верхнее основание по прямой, параллельной $AC$: '
            'через $K$ проведём $KL\\parallel A_1C_1$, $L\\in B_1C_1$. Так как $K$ — середина $A_1B_1$, $L$ — середина $B_1C_1$ и '
            '$KL=\\frac12 A_1C_1=\\frac12 AC$. Сечение $AKLC$ — трапеция ($KL\\parallel AC$, $KL\\ne AC$). Прямоугольные треугольники '
            '$AA_1K$ и $CC_1L$ равны по двум катетам ($AA_1=CC_1$, $A_1K=C_1L=\\frac12 AB$), поэтому $AK=CL$, и трапеция равнобедренная.\n\n'
            'б) Найдём расстояние через объём пирамиды $KABC$: $V=\\frac13 S_{ABC}\\cdot AA_1=\\frac13 S_{AKC}\\cdot d$.\n\n'
            f'$S_{{ABC}}=\\frac{{\\sqrt3}}{{4}}\\cdot {a}^2={tx(sabc)}$. Пусть $K\'$ — середина $AB$ (проекция $K$), $K\'H\\perp AC$; тогда '
            f'$K\'H=AK\'\\sin 60^\\circ={tx(a * S(3) / 4)}$ и по теореме о трёх перпендикулярах $KH\\perp AC$, '
            f'$KH=\\sqrt{{KK\'^2+K\'H^2}}=\\sqrt{{{h ** 2}+{tx(3 * a ** 2 / 16)}}}={tx(kh)}$, $S_{{AKC}}=\\frac12\\cdot AC\\cdot KH={tx(a * kh / 2)}$.\n\n'
            f'$$d=\\frac{{S_{{ABC}}\\cdot AA_1}}{{S_{{AKC}}}}=\\frac{{{tx(sabc)}\\cdot {h}}}{{{tx(a * kh / 2)}}}={tx(d)}.$$')

    def figure(self, p):
        pts = prism(tri_base(p['a']), p['h'])
        K, L = g.mid(pts['A1'], pts['B1']), g.mid(pts['B1'], pts['C1'])
        return g.draw(pts, extra={'K': K, 'L': L}, section_names=['A', 'K', 'L', 'C'], elev=20)

    def sample(self, rng):
        a = rng.choice([2, 4, 6, 8, 12])
        return dict(a=a, h=rng.choice([a, a, rng.randint(1, 12)]))


class PrismA1BM(Solved):
    """Правильная треугольная призма, M — середина CC₁: сечение A₁BM равнобедренное; высота по площади сечения"""
    number, topic = 14, SECTIONS
    fipi = {'727800': dict(a=2, s=6)}

    def _h(self, p):
        a, s = sp.Integer(p['a']), sp.sympify(p['s'])
        return sp.radsimp(S(16 * s ** 2 / (3 * a ** 2) - a ** 2))

    def answer(self, p):
        return Answer.num(self._h(p))

    def check(self, p):
        def area(h):
            pts = prism(tri_base(p['a']), h)
            M = g.mid(pts['C'], pts['C1'])
            sec = g.section(list(pts.values()), g.plane(pts['A1'], pts['B'], M))
            assert len(sec) == 3 and g.close(g.dist(pts['A1'], M), g.dist(pts['B'], M))
            return g.polygon_area(sec)
        lo, hi, s = 1e-6, 1e3, float(sp.sympify(p['s']))
        for _ in range(200):   # площадь сечения растёт с высотой — ищем высоту делением пополам
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if area(mid) < s else (lo, mid)
        return lo

    def condition(self, p):
        return (f'В правильной треугольной призме $ABCA_1B_1C_1$ сторона основания равна ${p["a"]}$. Плоскость $\\alpha$ проходит '
                'через вершины $A_1$, $B$ и середину $M$ ребра $CC_1$.\n\n'
                'а) Докажите, что сечение призмы плоскостью $\\alpha$ — равнобедренный треугольник.\n\n'
                f'б) Найдите высоту призмы, если площадь сечения равна ${tx(sp.sympify(p["s"]))}$.')

    def solution(self, p):
        a, s = sp.Integer(p['a']), sp.sympify(p['s'])
        h = self._h(p)
        return (
            'а) Точки $A_1$, $B$, $M$ лежат на рёбрах призмы, плоскость $\\alpha$ пересекает грани $AA_1B_1B$, $BB_1C_1C$, $AA_1C_1C$ по '
            'отрезкам $A_1B$, $BM$, $MA_1$, так что сечение — треугольник $A_1BM$. Пусть $h$ — высота призмы. Прямоугольные треугольники '
            '$A_1C_1M$ и $BCM$ равны по двум катетам ($A_1C_1=BC$, $C_1M=CM=\\frac h2$), поэтому $A_1M=BM$.\n\n'
            'б) Пусть $P$ — середина $A_1B$; $MP$ — медиана и высота равнобедренного треугольника. $P$ — центр грани $AA_1B_1B$, '
            'точки $P$ и $M$ находятся на одной высоте $\\frac h2$ над основанием, поэтому $MP$ равен своей проекции — отрезку от $C$ '
            f'до середины $AB$, то есть высоте правильного треугольника: $MP=\\frac{{\\sqrt3}}{{2}}\\cdot {a}={tx(a * S(3) / 2)}$.\n\n'
            f'$S=\\frac12\\cdot A_1B\\cdot MP=\\frac12\\sqrt{{{a ** 2}+h^2}}\\cdot {tx(a * S(3) / 2)}={tx(s)}$, откуда '
            f'$\\sqrt{{{a ** 2}+h^2}}={tx(sp.radsimp(4 * s / (a * S(3))))}$, $h^2={tx(sp.radsimp(16 * s ** 2 / (3 * a ** 2)))}-{a ** 2}={tx(h ** 2)}$, '
            f'$h={tx(h)}$.')

    def figure(self, p):
        h = float(self._h(p))
        pts = prism(tri_base(p['a']), h)
        M = g.mid(pts['C'], pts['C1'])
        return g.draw(pts, extra={'M': M}, section_names=['A1', 'B', 'M'], elev=20)

    def sample(self, rng):
        a = rng.choice([2, 3, 4, 6])
        hh = rng.choice([1, 2, 3, 4, 5, 6, 8, 'sqrt(2)', 'sqrt(5)', '2*sqrt(2)'])
        h = sp.sympify(hh)
        s = sp.radsimp(S(a ** 2 + h ** 2) * a * S(3) / 4)
        return dict(a=a, s=str(s))


class HexPyramidMidpoints(Solved):
    """Шестиугольная пирамида, M, K — середины SA, SD: MK ∥ BC; угол плоскости BMC с основанием"""
    number, topic = 14, ANGLES
    fipi = {'B19404': dict(a=8, phi=45, ask='height'), 'DBF6Be': dict(a=12, phi=30, ask='volume'),
            '454D16': dict(a=8, phi=45, ask='volume')}

    def _H(self, p):
        return sp.radsimp(sp.Integer(p['a']) * S(3) * sp.tan(sp.rad(p['phi'])))

    def answer(self, p):
        H = self._H(p)
        if p['ask'] == 'height':
            return Answer.num(H)
        a = sp.Integer(p['a'])
        return Answer.num(sp.radsimp(a ** 2 * S(3) / 4 * H / 6))

    def check(self, p):
        pts = hex_pyramid(p['a'], h=float(self._H(p)))
        M, K = g.mid(pts['S'], pts['A']), g.mid(pts['S'], pts['D'])
        assert g.parallel(g.sub(K, M), g.sub(pts['C'], pts['B']))
        ang = g.angle_planes(g.plane(pts['B'], M, pts['C']), ((0, 0, 1), 0))
        assert g.close(g.deg(ang), p['phi'])
        if p['ask'] == 'height':
            return pts['S'][2]
        return g.volume([M, pts['A'], pts['B'], pts['F']])

    def condition(self, p):
        if p['ask'] == 'height':
            return ('В правильной шестиугольной пирамиде $SABCDEF$ точки $M$ и $K$ — середины боковых рёбер $SA$ и $SD$.\n\n'
                    'а) Докажите, что прямые $BM$ и $CK$ лежат в одной плоскости.\n\n'
                    f'б) Найдите высоту пирамиды, если $AB={p["a"]}$, а угол между плоскостью $BMC$ и плоскостью основания '
                    f'равен ${p["phi"]}^\\circ$.')
        return ('В правильной шестиугольной пирамиде $SABCDEF$ точки $M$ и $K$ — середины боковых рёбер $SA$ и $SD$.\n\n'
                'а) Докажите, что прямые $BC$ и $MK$ параллельны.\n\n'
                f'б) Найдите объём пирамиды $MABF$, если $AB={p["a"]}$, а угол между плоскостью $BMC$ и плоскостью основания '
                f'равен ${p["phi"]}^\\circ$.')

    def solution(self, p):
        a, phi = sp.Integer(p['a']), p['phi']
        H = self._H(p)
        t = ('а) $MK$ — средняя линия треугольника $SAD$, поэтому $MK\\parallel AD$. В правильном шестиугольнике $AD\\parallel BC$ '
             '(большая диагональ параллельна сторонам $BC$ и $EF$). Значит, $MK\\parallel BC$')
        t += (', и прямые $BM$ и $CK$ лежат в плоскости, проходящей через параллельные прямые $MK$ и $BC$.\n\n' if p['ask'] == 'height'
              else '.\n\n')
        t += ('б) Плоскость $BMC$ содержит $MK$ (пункт а), то есть это плоскость трапеции $BCKM$. Пусть $O$ — центр основания, '
              '$SO=h$ — высота. Проекции $M\'$ и $K\'$ точек $M$ и $K$ — середины $OA$ и $OD$ — лежат на прямой $AD$, параллельной '
              f'$BC$ и удалённой от неё на ${tx(a * S(3) / 2)}$ (высота правильного треугольника $OBC$). Середина отрезка $M\'K\'$ — '
              'точка $O$. Пусть $Q$ — середина $BC$; $OQ\\perp BC$. Середина $N$ отрезка $MK$ проецируется в $O$, $NO=\\frac h2$, '
              'по теореме о трёх перпендикулярах $NQ\\perp BC$, и $\\angle NQO$ — линейный угол двугранного угла:\n\n'
              f'$$\\operatorname{{tg}}{phi}^\\circ=\\frac{{NO}}{{OQ}}=\\frac{{h/2}}{{{tx(a * S(3) / 2)}}},\\quad h={tx(a * S(3))}\\cdot'
              f'\\operatorname{{tg}}{phi}^\\circ={tx(H)}.$$')
        if p['ask'] == 'height':
            return t
        sabf = a ** 2 * S(3) / 4
        return t + ('\n\nРасстояние от $M$ до плоскости основания равно $\\frac h2$, '
                    f'$S_{{ABF}}=\\frac12 AB\\cdot AF\\sin 120^\\circ={tx(sabf)}$.\n\n'
                    f'$$V_{{MABF}}=\\frac13 S_{{ABF}}\\cdot\\frac h2=\\frac13\\cdot {tx(sabf)}\\cdot {tx(H / 2)}={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        pts = hex_pyramid(p['a'], h=float(self._H(p)))
        M, K = g.mid(pts['S'], pts['A']), g.mid(pts['S'], pts['D'])
        return g.draw(pts, extra={'M': M, 'K': K}, section_names=['B', 'C', 'K', 'M'], azim=-20, elev=20)

    def sample(self, rng):
        return dict(a=rng.choice([2, 4, 6, 8, 10, 12]), phi=rng.choice([30, 45, 60]), ask=rng.choice(['height', 'volume']))


class QuadPyramidOMK(Solved):
    """Правильная четырёхугольная пирамида: плоскость OMK ∥ SA; отрезок пересечения с гранью SAD"""
    number, topic = 14, SECTIONS
    fipi = {'04294C': dict(a=2, h2=14, m=3, n=1)}

    def _v(self, p):
        a, h2 = sp.Integer(p['a']), sp.Integer(p['h2'])
        sa = S(h2 + a ** 2 / 2)
        return a, h2, sa, sp.radsimp(sa * r(p['m'], p['m'] + p['n']))

    def answer(self, p):
        return Answer.num(self._v(p)[3])

    def check(self, p):
        pts = quad_pyramid(p['a'], h=math.sqrt(p['h2']))
        O = (0.0, 0.0, 0.0)
        M = g.mid(pts['S'], pts['C'])
        K = g.ratio(pts['B'], pts['C'], p['m'], p['n'])
        pl = g.plane(O, M, K)
        assert abs(g.dot(pl[0], g.sub(pts['A'], pts['S']))) < 1e-9
        # отрезок пересечения с гранью SAD: точки сечения, лежащие в плоскости SAD
        face = g.plane(pts['S'], pts['A'], pts['D'])
        on = [q for q in g.section(list(pts.values()), pl) if g.on_plane(face, q)]
        return g.dist(on[0], on[1])

    def condition(self, p):
        return (f'В правильной четырёхугольной пирамиде $SABCD$ точка $O$ — центр основания, $M$ — середина ребра $SC$, '
                f'точка $K$ делит ребро $BC$ в отношении $BK:KC={p["m"]}:{p["n"]}$, $AB={p["a"]}$, $SO={tx(S(p["h2"]))}$.\n\n'
                'а) Докажите, что плоскость $OMK$ параллельна прямой $SA$.\n\n'
                'б) Найдите длину отрезка, по которому плоскость $OMK$ пересекает грань $SAD$.')

    def solution(self, p):
        a, h2, sa, ans = self._v(p)
        m, n = p['m'], p['n']
        return (
            'а) $O$ — середина $AC$, $M$ — середина $SC$, поэтому $OM$ — средняя линия треугольника $SAC$ и $OM\\parallel SA$. '
            'Прямая $OM$ лежит в плоскости $OMK$, значит, $SA\\parallel OMK$.\n\n'
            'б) Прямая $KO$ при симметрии относительно центра $O$ переходит в себя, а сторона $BC$ — в сторону $DA$. Поэтому $KO$ '
            f'пересекает $AD$ в точке $P$, симметричной $K$: $DP:PA=BK:KC={m}:{n}$. Плоскость $OMK$ параллельна $SA$, значит, '
            'пересекает плоскость $SAD$ по прямой $PQ\\parallel SA$, где $Q\\in SD$; $PQ$ — искомый отрезок.\n\n'
            f'Из подобия треугольников $DPQ$ и $DAS$: $PQ=SA\\cdot\\frac{{DP}}{{DA}}=SA\\cdot\\frac{{{m}}}{{{m + n}}}$. '
            f'$OA=\\frac{{AB}}{{\\sqrt2}}$, $SA=\\sqrt{{SO^2+OA^2}}=\\sqrt{{{h2}+{tx(a ** 2 / 2)}}}={tx(sa)}$.\n\n'
            f'$$PQ={tx(sa)}\\cdot\\frac{{{m}}}{{{m + n}}}={tx(ans)}.$$')

    def figure(self, p):
        pts = quad_pyramid(p['a'], h=math.sqrt(p['h2']))
        O = (0.0, 0.0, 0.0)
        M, K = g.mid(pts['S'], pts['C']), g.ratio(pts['B'], pts['C'], p['m'], p['n'])
        P = g.ratio(pts['D'], pts['A'], p['m'], p['n'])
        Q = g.ratio(pts['D'], pts['S'], p['m'], p['n'])
        return g.draw(pts, extra={'O': O, 'M': M, 'K': K, 'P': P, 'Q': Q}, segments=[('O', 'M'), ('A', 'C')],
                      section_names=['K', 'M', 'Q', 'P'], azim=140)

    def sample(self, rng):
        a = rng.choice([2, 4, 6, 8])
        sa = rng.randint(a // 2 + 2, a + 6)
        h2 = sa ** 2 - a ** 2 // 2
        m, n = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (3, 2), (2, 3)])
        return dict(a=a, h2=h2, m=m, n=n)


class TrapezoidPyramidAMN(Solved):
    """Пирамида с трапецией в основании: плоскость AMN, отношение SK:KC и отношение объёмов частей"""
    number, topic = 14, VOLUMES
    fipi = {'8EEB4F': dict(ad=8, bc=3, sm=3, md=2, bn=1, nc=2)}

    def _v(self, p):
        ad, bc = sp.Integer(p['ad']), sp.Integer(p['bc'])
        sm, md, bn, nc = (sp.Integer(p[k]) for k in ('sm', 'md', 'bn', 'nc'))
        cn = bc * nc / (bn + nc)
        k = cn / ad                       # XC : XD
        ck_ks = md / sm * k               # CK : KS
        hm = md / (sm + md)               # высота M в долях H
        hk = ck_ks / (1 + ck_ks)          # высота K в долях H
        sadx = ad / (2 * (1 - k))         # S(ADX) в единицах t (высоты трапеции)
        v1 = sadx * hm - k ** 2 * sadx * hk   # (×tH/3)
        total = (ad + bc) / 2
        return k, ck_ks, hm, hk, sadx, v1, total - v1, total

    def answer(self, p):
        *_, v1, v2, total = self._v(p)
        lo, hi = sorted([v1, v2])
        q = sp.nsimplify(lo / hi)
        return Answer.ratio(q.p, q.q)

    def _pts(self, p):
        ad, bc = float(p['ad']), float(p['bc'])
        t = 3.0
        A, D = (0.0, 0.0, 0.0), (ad, 0.0, 0.0)
        B, C = (1.2, t, 0.0), (1.2 + bc, t, 0.0)
        Sv = (2.0, 1.0, 5.0)
        M = g.ratio(Sv, D, p['sm'], p['md'])
        N = g.ratio(B, C, p['bn'], p['nc'])
        return {'S': Sv, 'A': A, 'B': B, 'C': C, 'D': D}, M, N

    def check(self, p):
        pts, M, N = self._pts(p)
        pl = g.plane(pts['A'], M, N)
        K = g.line_plane(pts['S'], pts['C'], pl)
        k_ratio = g.dist(pts['S'], K) / g.dist(K, pts['C'])
        assert g.close(k_ratio, float(1 / self._v(p)[1]))
        v1, v2 = g.split_volumes(list(pts.values()), pl)
        lo, hi = sorted([v1, v2])
        return lo / hi

    def condition(self, p):
        k = self._v(p)[1]
        sk = sp.nsimplify(1 / k)
        return (f'В основании пирамиды $SABCD$ лежит трапеция $ABCD$ с основаниями $AD={p["ad"]}$ и $BC={p["bc"]}$. Точки $M$ и $N$ '
                f'лежат на рёбрах $SD$ и $BC$, причём $SM:MD={p["sm"]}:{p["md"]}$, $BN:NC={p["bn"]}:{p["nc"]}$. Плоскость $AMN$ '
                f'пересекает ребро $SC$ в точке $K$.\n\nа) Докажите, что $SK:KC={sk.p}:{sk.q}$.\n\n'
                'б) Плоскость $AMN$ делит пирамиду на два многогранника. Найдите отношение их объёмов.')

    def solution(self, p):
        k, ck_ks, hm, hk, sadx, v1, v2, total = self._v(p)
        ad, bc = p['ad'], p['bc']
        cn = sp.Integer(bc) * p['nc'] / (p['bn'] + p['nc'])
        sk = sp.nsimplify(1 / ck_ks)
        a = self.answer(p)
        return (
            f'а) $CN={tx(cn)}$. Прямая $AN$ пересекает прямую $DC$ в точке $X$ за точкой $C$; треугольники $XCN$ и $XDA$ подобны '
            f'($CN\\parallel AD$): $\\frac{{XC}}{{XD}}=\\frac{{CN}}{{AD}}={tx(k)}$. Плоскость $AMN$ пересекает грань $SDC$ по прямой $MX$, '
            'и $K$ — точка пересечения $MX$ с $SC$. По теореме Менелая для треугольника $SDC$ и прямой $MKX$:\n\n'
            f'$$\\frac{{SM}}{{MD}}\\cdot\\frac{{DX}}{{XC}}\\cdot\\frac{{CK}}{{KS}}=1\\ \\Rightarrow\\ \\frac{{{p["sm"]}}}{{{p["md"]}}}\\cdot '
            f'{tx(1 / k)}\\cdot\\frac{{CK}}{{KS}}=1,\\quad \\frac{{CK}}{{KS}}={tx(ck_ks)},$$ то есть $SK:KC={sk.p}:{sk.q}$.\n\n'
            'б) Плоскость отсекает от пирамиды многогранник $ANCDMK$ (с вершинами $C$ и $D$). Он получается из пирамиды $MADX$ '
            'удалением пирамиды $KNCX$. Пусть $H$ — высота пирамиды $SABCD$, $t$ — высота трапеции, $V=\\frac13 S_{ABCD}H$.\n\n'
            f'Высоты точек $M$ и $K$ над основанием: $\\frac{{MD}}{{SD}}H={tx(hm)}H$ и $\\frac{{KC}}{{SC}}H={tx(hk)}H$. '
            f'$XD=\\frac{{CD}}{{1-{tx(k)}}}$, поэтому расстояние от $X$ до $AD$ равно ${tx(1 / (1 - k))}t$ и $S_{{ADX}}={tx(sadx)}t$; '
            f'треугольник $NCX$ подобен $ADX$ с коэффициентом ${tx(k)}$: $S_{{NCX}}={tx(k ** 2 * sadx)}t$. $S_{{ABCD}}={tx(total)}t$.\n\n'
            f'$$V_{{ANCDMK}}=\\frac13\\left({tx(sadx)}t\\cdot {tx(hm)}H-{tx(k ** 2 * sadx)}t\\cdot {tx(hk)}H\\right)=\\frac{{tH}}{{3}}\\cdot {tx(v1)},$$ '
            f'объём второй части $\\frac{{tH}}{{3}}\\left({tx(total)}-{tx(v1)}\\right)=\\frac{{tH}}{{3}}\\cdot {tx(v2)}$. '
            f'Отношение объёмов {a.display}.')

    def figure(self, p):
        pts, M, N = self._pts(p)
        pl = g.plane(pts['A'], M, N)
        K = g.line_plane(pts['S'], pts['C'], pl)
        return g.draw(pts, extra={'M': M, 'N': N, 'K': K}, section_names=['A', 'N', 'K', 'M'], azim=200, elev=30)

    def sample(self, rng):
        ad = rng.randint(4, 12)
        bc = rng.randint(2, ad - 1)
        sm, md = rng.choice([(1, 1), (1, 2), (2, 1), (3, 2), (2, 3), (3, 1)])
        bn, nc = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3)])
        return dict(ad=ad, bc=bc, sm=sm, md=md, bn=bn, nc=nc)


class BoxRhombus(Solved):
    """Сечение параллелепипеда плоскостью через BD₁ ∥ AC — ромб ⇒ основание квадрат; угол с гранью BCC₁"""
    number, topic = 14, ANGLES
    fipi = {'8A0B46': dict(h=10, a=12), '17B23F': dict(h=6, a=4)}

    def answer(self, p):
        a, h = sp.Integer(p['a']), sp.Integer(p['h'])
        return Answer.angle(sp.radsimp(S(4 * a ** 2 + h ** 2) / h))

    def check(self, p):
        pts = box(p['a'], p['a'], p['h'])
        pl = g.plane_pv(pts['B'], g.sub(pts['C'], pts['A']), g.sub(pts['D1'], pts['B']))
        sec = g.section(list(pts.values()), pl)
        sides = [g.dist(sec[i], sec[(i + 1) % 4]) for i in range(4)]
        assert len(sec) == 4 and max(sides) - min(sides) < 1e-9
        return g.angle_planes(pl, g.plane(pts['B'], pts['C'], pts['C1']))

    def condition(self, p):
        return ('Сечением прямоугольного параллелепипеда $ABCDA_1B_1C_1D_1$ плоскостью $\\alpha$, содержащей прямую $BD_1$ и '
                'параллельной прямой $AC$, является ромб.\n\nа) Докажите, что грань $ABCD$ — квадрат.\n\n'
                f'б) Найдите угол между плоскостями $\\alpha$ и $BCC_1$, если $AA_1={p["h"]}$, $AB={p["a"]}$.')

    def solution(self, p):
        a, h = sp.Integer(p['a']), sp.Integer(p['h'])
        return (
            'а) Плоскость $\\alpha$ параллельна $AC$, поэтому пересекает плоскость $AA_1C_1C$ по прямой $EF\\parallel AC$, проходящей через '
            'середину $O$ диагонали $BD_1$ (центр параллелепипеда), $E\\in AA_1$, $F\\in CC_1$. Противоположные грани параллельны, '
            'поэтому сечение $BED_1F$ — параллелограмм. Он ромб, значит, его диагонали перпендикулярны: $BD_1\\perp EF$, и тогда '
            '$BD_1\\perp AC$. $BD$ — проекция $BD_1$ на плоскость основания, по теореме о трёх перпендикулярах $BD\\perp AC$. '
            'Прямоугольник $ABCD$ с перпендикулярными диагоналями — квадрат.\n\n'
            f'б) Пусть $AB=a={a}$, $AA_1=h={h}$. $E$ и $F$ — середины $AA_1$ и $CC_1$ ($EF$ проходит через центр). Спроецируем ромб на '
            'плоскость $BCC_1$: $B\\to B$, $F\\to F$, $D_1\\to C_1$, $E\\to E\'$ — середина $BB_1$. Проекция — параллелограмм $BE\'C_1F$ '
            'с основанием $BE\'=\\frac h2$ и высотой $B_1C_1=a$: $S_{\\text{пр}}=\\frac{ah}{2}$. Площадь ромба '
            '$S=\\frac12\\,BD_1\\cdot EF=\\frac12\\sqrt{2a^2+h^2}\\cdot a\\sqrt2$.\n\n'
            f'$$\\cos\\varphi=\\frac{{S_{{\\text{{пр}}}}}}{{S}}=\\frac{{h}}{{\\sqrt{{2}}\\sqrt{{2a^2+h^2}}}},\\qquad '
            f'\\operatorname{{tg}}\\varphi=\\frac{{\\sqrt{{4a^2+h^2}}}}{{h}}=\\frac{{\\sqrt{{{4 * a ** 2}+{h ** 2}}}}}{{{h}}}'
            f'={tx(sp.radsimp(S(4 * a ** 2 + h ** 2) / h))}.$$')

    def figure(self, p):
        pts = box(p['a'], p['a'], p['h'])
        E, F = g.mid(pts['A'], pts['A1']), g.mid(pts['C'], pts['C1'])
        return g.draw(pts, extra={'E': E, 'F': F}, section_names=['B', 'F', 'D1', 'E'], elev=20)

    def sample(self, rng):
        a, h = rng.choice([(3, 8), (6, 5), (6, 16), (12, 10), (4, 6), (2, 3), (5, 24), (3, 4), (4, 3), (2, 1)])
        k = rng.choice([1, 1, 2])
        return dict(a=a * k, h=h * k)


class TetraLMN(Solved):
    """Правильный тетраэдр: BL:LC = AM:MB = AN:ND = 1:2; сечение LMN делит CD в отношении 2:1; площадь сечения"""
    number, topic = 14, SECTIONS
    fipi = {'7ee2FA': dict(a=6, p=1, q=2)}

    def _v(self, p):
        a = sp.Integer(p['a'])
        t = r(p['p'], p['p'] + p['q'])
        mn, lk = t * a, (1 - t) * a
        ml2 = ((1 - t) * a) ** 2 + (t * a) ** 2 - (1 - t) * t * a ** 2
        hgt = S(ml2 - ((lk - mn) / 2) ** 2)
        return a, t, mn, lk, ml2, hgt, sp.radsimp((mn + lk) / 2 * hgt)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def _pts(self, p):
        a = float(p['a'])
        A, B, C = (0.0, 0.0, 0.0), (a, 0.0, 0.0), (a / 2, a * math.sqrt(3) / 2, 0.0)
        O = g.centroid(A, B, C)
        D = (O[0], O[1], a * math.sqrt(2 / 3))
        t = p['p'] / (p['p'] + p['q'])
        L, M, N = g.lerp(B, C, t), g.lerp(A, B, t), g.lerp(A, D, t)
        return {'A': A, 'B': B, 'C': C, 'D': D}, L, M, N

    def check(self, p):
        pts, L, M, N = self._pts(p)
        pl = g.plane(L, M, N)
        K = g.line_plane(pts['C'], pts['D'], pl)
        assert g.close(g.dist(pts['C'], K) / g.dist(K, pts['D']), p['q'] / p['p'])
        return g.polygon_area(g.section(list(pts.values()), pl))

    def condition(self, p):
        pp, q = p['p'], p['q']
        return (f'На рёбрах $BC$, $AB$ и $AD$ правильного тетраэдра $ABCD$ отмечены точки $L$, $M$ и $N$, причём '
                f'$BL:LC=AM:MB=AN:ND={pp}:{q}$.\n\nа) Докажите, что плоскость $LMN$ делит ребро $CD$ в отношении ${q}:{pp}$, '
                f'считая от вершины $C$.\n\nб) Найдите площадь сечения тетраэдра плоскостью $LMN$, если $AB={p["a"]}$.')

    def solution(self, p):
        a, t, mn, lk, ml2, hgt, s = self._v(p)
        pp, q = p['p'], p['q']
        return (
            f'а) $AM:MB=AN:ND$, поэтому $MN\\parallel BD$. Плоскость $LMN$ содержит прямую $MN\\parallel BD$, значит, пересекает грань $BCD$ '
            f'по прямой $LK\\parallel BD$, $K\\in CD$, и $CK:KD=CL:LB={q}:{pp}$.\n\n'
            f'б) Сечение $MLKN$ — трапеция ($MN\\parallel BD\\parallel LK$). $MN=\\frac{{AM}}{{AB}}\\cdot BD={tx(mn)}$, '
            f'$LK=\\frac{{CL}}{{CB}}\\cdot BD={tx(lk)}$. В треугольнике $MBL$: $BM={tx((1 - t) * a)}$, $BL={tx(t * a)}$, $\\angle B=60^\\circ$, '
            f'$ML^2=BM^2+BL^2-BM\\cdot BL={tx(ml2)}$. Аналогично в треугольнике $NDK$: $DN={tx((1 - t) * a)}$, $DK={tx(t * a)}$, '
            '$NK=ML$ — трапеция равнобедренная.\n\n'
            f'Высота трапеции $\\sqrt{{ML^2-\\left(\\frac{{LK-MN}}{{2}}\\right)^2}}=\\sqrt{{{tx(ml2)}-{tx(((lk - mn) / 2) ** 2)}}}={tx(hgt)}$.\n\n'
            f'$$S=\\frac{{MN+LK}}{{2}}\\cdot {tx(hgt)}=\\frac{{{tx(mn)}+{tx(lk)}}}{{2}}\\cdot {tx(hgt)}={tx(s)}.$$')

    def figure(self, p):
        pts, L, M, N = self._pts(p)
        K = g.line_plane(pts['C'], pts['D'], g.plane(L, M, N))
        return g.draw(pts, extra={'L': L, 'M': M, 'N': N, 'K': K}, section_names=['M', 'L', 'K', 'N'])

    def sample(self, rng):
        pp, q = rng.choice([(1, 2), (1, 3), (2, 3), (1, 4), (3, 4)])
        return dict(a=(pp + q) * rng.randint(1, 3), p=pp, q=q)


class TrapezoidPyramidSO(Solved):
    """Пирамида над трапецией: плоскость через середины боковых сторон ∥ SO — трапеция; площадь сечения"""
    number, topic = 14, SECTIONS
    fipi = {'182CF4': dict(ad=10, bc=8, so=8)}

    def answer(self, p):
        return Answer.num(sp.Integer(p['so']) * (p['ad'] + p['bc']) / 4)

    def check(self, p):
        ad, bc, so = map(float, (p['ad'], p['bc'], p['so']))
        t = 5.0
        A, D, B, C = (0.0, 0.0, 0.0), (ad, 0.0, 0.0), (1.5, t, 0.0), (1.5 + bc, t, 0.0)
        # O — точка пересечения диагоналей: AO:OC = AD:BC
        O = g.lerp(A, C, ad / (ad + bc))
        Sv = g.add(O, g.mul(g.unit((0.0, 0.6, 1.0)), so))     # SO ⊥ AD, но не обязательно ⊥ основанию
        pts = {'S': Sv, 'A': A, 'B': B, 'C': C, 'D': D}
        M, N = g.mid(A, B), g.mid(C, D)
        pl = g.plane_pv(M, g.sub(N, M), g.sub(Sv, O))
        sec = g.section(list(pts.values()), pl)
        assert len(sec) == 4
        return g.polygon_area(sec)

    def condition(self, p):
        return ('В основании пирамиды $SABCD$ лежит трапеция $ABCD$ с бо́льшим основанием $AD$. Диагонали трапеции пересекаются в точке $O$. '
                'Точки $M$ и $N$ — середины боковых сторон $AB$ и $CD$. Плоскость $\\alpha$ проходит через $M$ и $N$ параллельно прямой $SO$.\n\n'
                'а) Докажите, что сечение пирамиды плоскостью $\\alpha$ — трапеция.\n\n'
                f'б) Найдите площадь сечения, если $AD={p["ad"]}$, $BC={p["bc"]}$, $SO={p["so"]}$, а прямая $SO$ перпендикулярна прямой $AD$.')

    def solution(self, p):
        ad, bc, so = (sp.Integer(p[k]) for k in ('ad', 'bc', 'so'))
        k = (ad + bc) / (2 * ad)
        return (
            'а) $MN$ — средняя линия трапеции, она проходит через середины $P$ и $Q$ диагоналей $AC$ и $BD$. Так как $AO:OC=AD:BC>1$, '
            'середина $P$ диагонали $AC$ лежит между $A$ и $O$; аналогично $Q$ лежит между $D$ и $O$.\n\n'
            'Плоскость $\\alpha\\parallel SO$, поэтому пересекает плоскость $SAC$ по прямой $PP\'\\parallel SO$, $P\'\\in SA$, а плоскость $SBD$ — '
            'по прямой $QQ\'\\parallel SO$, $Q\'\\in SD$. Из подобия: $\\frac{AP\'}{AS}=\\frac{AP}{AO}$ и $\\frac{DQ\'}{DS}=\\frac{DQ}{DO}$. '
            'Но $\\frac{AP}{AO}=\\frac{AC/2}{AC\\cdot AD/(AD+BC)}=\\frac{AD+BC}{2AD}=\\frac{DQ}{DO}$, поэтому $P\'Q\'\\parallel AD\\parallel MN$. '
            'Сечение $MP\'Q\'N$ — трапеция ($P\'Q\'<AD$, а $MN$ — средняя линия, так что $P\'Q\'\\ne MN$).\n\n'
            f'б) $\\frac{{AP}}{{AO}}=\\frac{{AD+BC}}{{2AD}}={tx(k)}$, поэтому $PP\'=QQ\'={tx(k)}\\cdot SO={tx(k * so)}$. Отрезки $PP\'$ и $QQ\'$ '
            'равны и параллельны, $P\'Q\'=PQ=\\frac{AD-BC}{2}$' + f'$={tx((ad - bc) / 2)}$, $MN=\\frac{{AD+BC}}{{2}}={tx((ad + bc) / 2)}$. '
            'Высота трапеции $MP\'Q\'N$ — расстояние между $P\'Q\'$ и $MN$ — равна $PP\'$, так как $PP\'\\parallel SO\\perp AD\\parallel MN$.\n\n'
            f'$$S=\\frac{{MN+P\'Q\'}}{{2}}\\cdot PP\'=\\frac{{{tx((ad + bc) / 2)}+{tx((ad - bc) / 2)}}}{{2}}\\cdot {tx(k * so)}'
            f'={tx(so * (ad + bc) / 4)}.$$')

    def figure(self, p):
        ad, bc, so = map(float, (p['ad'], p['bc'], p['so']))
        t = ad * 0.5
        A, D, B, C = (0.0, 0.0, 0.0), (ad, 0.0, 0.0), ((ad - bc) / 2, t, 0.0), ((ad + bc) / 2, t, 0.0)
        O = g.lerp(A, C, ad / (ad + bc))
        Sv = (O[0], O[1], so)
        pts = {'S': Sv, 'A': A, 'B': B, 'C': C, 'D': D}
        M, N = g.mid(A, B), g.mid(C, D)
        pl = g.plane_pv(M, g.sub(N, M), g.sub(Sv, O))
        P1, Q1 = g.line_plane(Sv, A, pl), g.line_plane(Sv, D, pl)
        return g.draw(pts, extra={'O': O, 'M': M, 'N': N, 'P′': P1, 'Q′': Q1}, segments=[('S', 'O')],
                      section_names=['M', 'P′', 'Q′', 'N'])

    def sample(self, rng):
        ad = rng.randint(5, 14)
        bc = rng.randint(2, ad - 1)
        so = rng.randint(2, 12)
        if (so * (ad + bc)) % 4:
            return None
        return dict(ad=ad, bc=bc, so=so)


class PrismTrapezoidAMKN(Solved):
    """Прямая призма с параллелограммом в основании, AMKN — равнобедренная трапеция с основаниями 1 и 2: высота призмы"""
    number, topic = 14, VOLUMES
    fipi = {'ED4407': dict(vol=5, p=2, q=3)}

    def _v(self, p):
        an = sp.Integer(2)                 # большее основание трапеции AN
        ba = an / S(3)                     # треугольник ABN равнобедренный с углом 120°
        bc = ba / 2 * (p['p'] + p['q']) / p['p']
        sb = ba * bc * S(3) / 2
        return ba, bc, sb, sp.radsimp(p['vol'] / sb)

    def answer(self, p):
        return Answer.num(self._v(p)[3])

    def check(self, p):
        ba, bc, sb, h = (float(x) for x in self._v(p))
        A = (0.0, 0.0, 0.0)
        B = (ba, 0.0, 0.0)
        D = (bc * 0.5, bc * math.sqrt(3) / 2, 0.0)
        C = g.add(B, D)
        pts = {'A': A, 'B': B, 'C': C, 'D': D}
        pts.update({k + '1': (v[0], v[1], h) for k, v in list(pts.items())})
        M = g.mid(pts['A1'], pts['B1'])
        K = g.ratio(pts['B1'], pts['C1'], p['p'], p['q'])
        N = g.lerp(pts['B'], pts['C'], ba / bc)
        assert g.close(g.dist(A, N), 2) and g.close(g.dist(M, K), 1) and g.close(g.dist(A, M), g.dist(N, K))
        assert g.parallel(g.sub(N, A), g.sub(K, M))
        # условия задачи выполнены на построенной призме — высота из объёма
        return p['vol'] / g.norm(g.cross(g.sub(B, A), g.sub(D, A)))

    def condition(self, p):
        return ('В основании прямой призмы $ABCDA_1B_1C_1D_1$ лежит параллелограмм $ABCD$ с углом $60^\\circ$ при вершине $A$. '
                'На рёбрах $A_1B_1$, $B_1C_1$ и $BC$ отмечены точки $M$, $K$ и $N$ так, что четырёхугольник $AMKN$ — равнобедренная '
                'трапеция с основаниями 1 и 2.\n\nа) Докажите, что точка $M$ — середина ребра $A_1B_1$.\n\n'
                f'б) Найдите высоту призмы, если её объём равен ${p["vol"]}$ и точка $K$ делит ребро $B_1C_1$ в отношении '
                f'$B_1K:KC_1={p["p"]}:{p["q"]}$.')

    def solution(self, p):
        ba, bc, sb, h = self._v(p)
        return (
            'а) Отрезки $AN$ и $MK$ лежат в параллельных плоскостях оснований, поэтому основания трапеции — $AN$ и $MK$, $AN\\parallel MK$. '
            'Пусть $M\'$ и $K\'$ — проекции $M$ и $K$ на нижнее основание ($M\'\\in AB$, $K\'\\in BC$); $M\'K\'\\parallel AN$ и $M\'K\'=MK$. '
            'Треугольники $BM\'K\'$ и $BAN$ подобны с коэффициентом $\\lambda=\\frac{MK}{AN}$.\n\n'
            'Трапеция равнобедренная: $AM=NK$. Наклонные $AM$ и $NK$ имеют одинаковые проекции на основание по высоте призмы, поэтому '
            '$AM\'=NK\'$, то есть $(1-\\lambda)BA=(1-\\lambda)BN$, и $BA=BN$. Основание $MK$ меньше $AN$, значит, $MK=1$, $AN=2$, '
            '$\\lambda=\\frac12$ и $BM\'=\\frac12 BA$: $M$ — середина $A_1B_1$.\n\n'
            'б) В треугольнике $ABN$: $BA=BN$, $\\angle B=180^\\circ-60^\\circ=120^\\circ$, $AN=2$, поэтому $AN=BA\\sqrt3$, '
            f'$BA={tx(ba)}$. $BK\'=\\lambda BN=\\frac12 BA$, и $BK\'=\\frac{{{p["p"]}}}{{{p["p"] + p["q"]}}}BC$, откуда $BC={tx(bc)}$.\n\n'
            f'$S_{{ABCD}}=AB\\cdot BC\\sin 60^\\circ={tx(sb)}$, $$h=\\frac{{V}}{{S_{{ABCD}}}}=\\frac{{{p["vol"]}}}{{{tx(sb)}}}={tx(h)}.$$')

    def figure(self, p):
        ba, bc, sb, h = (float(x) for x in self._v(p))
        A, B = (0.0, 0.0, 0.0), (ba, 0.0, 0.0)
        D = (bc * 0.5, bc * math.sqrt(3) / 2, 0.0)
        pts = {'A': A, 'B': B, 'C': g.add(B, D), 'D': D}
        pts.update({k + '1': (v[0], v[1], h) for k, v in list(pts.items())})
        M, K = g.mid(pts['A1'], pts['B1']), g.ratio(pts['B1'], pts['C1'], p['p'], p['q'])
        N = g.lerp(pts['B'], pts['C'], ba / bc)
        return g.draw(pts, extra={'M': M, 'K': K, 'N': N}, section_names=['A', 'M', 'K', 'N'], elev=22)

    def sample(self, rng):
        pp, q = rng.choice([(1, 2), (2, 3), (1, 3), (1, 1), (2, 1), (3, 2)])
        return dict(vol=rng.randint(2, 12), p=pp, q=q)


class PrismTrapezoidN(Solved):
    """Прямая призма с параллелограммом в основании, B₁K:KC₁ = 1:2, AMKN — трапеция 2 и 3 ⇒ N — середина BC; площадь AMKN"""
    number, topic = 14, SECTIONS
    fipi = {'0549EB': dict(vol=12, h=2)}

    def _v(self, p):
        h, vol = sp.Integer(p['h']), sp.Integer(p['vol'])
        sbase = vol / h
        tri = sbase / 4                      # S_ABN = ¼ S_ABCD (BN = BC/2, ...)
        hb = 2 * tri / 3                     # высота из B к AN = 3
        x2 = hb ** 2 + r(9, 4)              # BA² = BN²
        leg2 = h ** 2 + x2 / 9               # AM² = h² + (BA/3)²
        th = S(leg2 - r(1, 4))
        return sbase, tri, hb, x2, leg2, th, sp.radsimp(r(5, 2) * th)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        sbase, tri, hb, x2, leg2, th, s = (float(x) for x in self._v(p))
        x = math.sqrt(x2)
        ang = 2 * math.asin(1.5 / x)          # угол ABN
        A, B = (0.0, 0.0, 0.0), (x, 0.0, 0.0)
        Nv = g.add(B, (x * math.cos(math.pi - ang), x * math.sin(math.pi - ang), 0.0))
        C = g.add(B, g.mul(g.sub(Nv, B), 2))
        D = g.add(A, g.sub(C, B))
        h = float(p['h'])
        pts = {'A': A, 'B': B, 'C': C, 'D': D}
        pts.update({k + '1': (v[0], v[1], h) for k, v in list(pts.items())})
        M, K = g.lerp(pts['A1'], pts['B1'], 1 / 3), g.ratio(pts['B1'], pts['C1'], 1, 2)
        assert g.close(g.dist(A, Nv), 3) and g.close(g.dist(M, K), 2) and g.close(g.dist(A, M), g.dist(Nv, K))
        assert g.close(g.norm(g.cross(g.sub(B, A), g.sub(D, A))) * h, p['vol'])
        return g.polygon_area([A, M, K, Nv])

    def condition(self, p):
        return ('В основании прямой призмы $ABCDA_1B_1C_1D_1$ лежит параллелограмм $ABCD$. На рёбрах $A_1B_1$, $B_1C_1$ и $BC$ '
                'отмечены точки $M$, $K$ и $N$, причём $B_1K:KC_1=1:2$, а четырёхугольник $AMKN$ — равнобедренная трапеция с основаниями 2 и 3.\n\n'
                'а) Докажите, что точка $N$ — середина ребра $BC$.\n\n'
                f'б) Найдите площадь трапеции $AMKN$, если объём призмы равен ${p["vol"]}$, а её высота равна ${p["h"]}$.')

    def solution(self, p):
        sbase, tri, hb, x2, leg2, th, s = self._v(p)
        return (
            'а) $AN$ и $MK$ лежат в параллельных плоскостях оснований, поэтому $AN\\parallel MK$ — основания трапеции. Проекции $M\'\\in AB$ '
            'и $K\'\\in BC$ точек $M$ и $K$: $M\'K\'\\parallel AN$, $M\'K\'=MK$, треугольники $BM\'K\'$ и $BAN$ подобны с коэффициентом '
            '$\\lambda=\\frac{MK}{AN}$. Из $AM=NK$ (трапеция равнобедренная) следует $AM\'=NK\'$, то есть $(1-\\lambda)BA=(1-\\lambda)BN$, '
            '$BA=BN$. Меньшее основание $MK=2$, $AN=3$, $\\lambda=\\frac23$. Тогда $BK\'=\\frac23 BN$, а $BK\'=\\frac13 BC$, '
            'откуда $BN=\\frac12 BC$: $N$ — середина $BC$.\n\n'
            f'б) Площадь основания $\\frac{{V}}{{h}}={tx(sbase)}$. $BN=\\frac12 BC$, поэтому $S_{{ABN}}=\\frac14 S_{{ABCD}}={tx(tri)}$. '
            f'Высота равнобедренного треугольника $ABN$, проведённая к $AN=3$, равна $\\frac{{2S_{{ABN}}}}{{3}}={tx(hb)}$, откуда '
            f'$BA^2={tx(hb ** 2)}+\\left(\\frac32\\right)^2={tx(x2)}$.\n\n'
            f'$AM\'=(1-\\lambda)BA=\\frac13 BA$, боковая сторона трапеции $AM^2=h^2+AM\'^2={p["h"] ** 2}+{tx(x2 / 9)}={tx(leg2)}$. '
            f'Высота трапеции $\\sqrt{{AM^2-\\left(\\frac{{3-2}}{{2}}\\right)^2}}={tx(th)}$.\n\n'
            f'$$S_{{AMKN}}=\\frac{{2+3}}{{2}}\\cdot {tx(th)}={tx(s)}.$$')

    def figure(self, p):
        return None

    def sample(self, rng):
        h = rng.randint(1, 5)
        return dict(vol=h * rng.choice([3, 6, 9, 12]), h=h)


class TriPyramidMNPerp(Solved):
    """Правильная треугольная пирамида: плоскость через MN ⊥ основанию делит медиану CE в отношении 5:1; периметр сечения"""
    number, topic = 14, SECTIONS
    fipi = {'c3497c': dict(a=6, s='4*sqrt(3)')}

    def _v(self, p):
        a, s = sp.Integer(p['a']), sp.sympify(p['s'])
        mx = S(s ** 2 / 4 - a ** 2 / 18)
        return a, s, mx, sp.radsimp(a / 2 + 5 * a / 6 + 2 * mx)

    def answer(self, p):
        return Answer.num(self._v(p)[3])

    def check(self, p):
        A, B, C, Sv = tri_pyramid(p['a'], float(sp.sympify(p['s'])))
        M, N = g.mid(Sv, A), g.mid(Sv, B)
        pl = g.plane_pv(M, g.sub(N, M), (0, 0, 1))
        E = g.mid(A, B)
        X = g.line_plane(C, E, pl)
        assert g.close(g.dist(C, X) / g.dist(X, E), 5)
        sec = g.section([A, B, C, Sv], pl)
        return sum(g.dist(sec[i], sec[(i + 1) % len(sec)]) for i in range(len(sec)))

    def condition(self, p):
        return (f'В правильной треугольной пирамиде $SABC$ сторона основания $AB$ равна ${p["a"]}$, а боковое ребро $SA$ равно '
                f'${tx(sp.sympify(p["s"]))}$. Точки $M$ и $N$ — середины рёбер $SA$ и $SB$. Плоскость $\\alpha$ содержит прямую $MN$ '
                'и перпендикулярна плоскости основания.\n\nа) Докажите, что плоскость $\\alpha$ делит медиану $CE$ основания в отношении '
                '$5:1$, считая от точки $C$.\n\nб) Найдите периметр сечения пирамиды плоскостью $\\alpha$.')

    def solution(self, p):
        a, s, mx, per = self._v(p)
        cosA = a / (2 * s)
        return (
            'а) Пусть $O$ — центр основания, $SO$ — высота. Проекции $M\'$ и $N\'$ точек $M$ и $N$ — середины $OA$ и $OB$, и $\\alpha$ '
            'пересекает основание по прямой $M\'N\'$ — средней линии треугольника $AOB$, параллельной $AB$. Она делит отрезок $OE$ '
            'пополам в точке $P$. $CO=\\frac23 CE$, $OP=\\frac16 CE$, поэтому $CP=\\frac56 CE$ и $CP:PE=5:1$.\n\n'
            'б) Прямая $M\'N\'$ пересекает $AC$ и $BC$ в точках $X$ и $Y$, $XY\\parallel AB$, $\\frac{CX}{CA}=\\frac{CP}{CE}=\\frac56$. '
            f'Сечение — трапеция $MNYX$: $MN=\\frac12 AB={tx(a / 2)}$, $XY=\\frac56 AB={tx(5 * a / 6)}$, $AX=\\frac16 AC={tx(a / 6)}$.\n\n'
            f'В треугольнике $AMX$: $AM=\\frac{{SA}}{{2}}={tx(s / 2)}$, $\\cos\\angle SAC=\\frac{{AC/2}}{{SA}}={tx(sp.radsimp(cosA))}$, '
            f'$MX^2=AM^2+AX^2-2\\cdot AM\\cdot AX\\cos\\angle SAC={tx(s ** 2 / 4)}+{tx(a ** 2 / 36)}-{tx(sp.radsimp(2 * s / 2 * a / 6 * cosA))}'
            f'={tx(mx ** 2)}$, $MX=NY={tx(mx)}$.\n\n'
            f'$$P={tx(a / 2)}+{tx(5 * a / 6)}+2\\cdot {tx(mx)}={tx(per)}.$$')

    def figure(self, p):
        A, B, C, Sv = tri_pyramid(p['a'], float(sp.sympify(p['s'])))
        M, N = g.mid(Sv, A), g.mid(Sv, B)
        X, Y = g.lerp(A, C, 1 / 6), g.lerp(B, C, 1 / 6)
        return g.draw({'A': A, 'B': B, 'C': C, 'S': Sv}, extra={'M': M, 'N': N, 'X': X, 'Y': Y},
                      section_names=['M', 'N', 'Y', 'X'], azim=195, elev=14)

    def sample(self, rng):
        a = rng.choice([6, 12, 18])
        s = rng.choice(['4*sqrt(3)', '2*sqrt(6)', '6', '8', '10', '12', '3*sqrt(3)', '5*sqrt(2)'])
        if float(sp.sympify(s)) <= a / math.sqrt(3):
            return None
        return dict(a=a, s=s)


class TriPyramidCKM(Solved):
    """Правильная треугольная пирамида: M на AB, K на SB, плоскость CKM ⊥ основанию; объём BCKM"""
    number, topic = 14, VOLUMES
    fipi = {'4679B2': dict(a=6, s2=21, am=4)}

    def _v(self, p):
        a, s2, am = sp.Integer(p['a']), sp.Integer(p['s2']), sp.Integer(p['am'])
        m = a - am                                 # BM
        lam = 3 * m / (a + m)                      # BK : BS
        so = S(s2 - a ** 2 / 3)
        sbcm = m * a * S(3) / 4
        return a, m, lam, so, sbcm, sp.radsimp(sbcm * lam * so / 3)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def _pts(self, p):
        a, m, lam, *_ = self._v(p)
        A, B, C, Sv = tri_pyramid(p['a'], math.sqrt(p['s2']))
        M = g.lerp(A, B, p['am'] / p['a'])
        K = g.lerp(B, Sv, float(lam))
        return A, B, C, Sv, M, K

    def check(self, p):
        A, B, C, Sv, M, K = self._pts(p)
        assert g.perpendicular(g.plane(C, K, M)[0], (0, 0, 1))
        return g.volume([B, C, K, M])

    def condition(self, p):
        lam = self._v(p)[2]
        sk = sp.nsimplify((1 - lam) / lam)
        return (f'В правильной треугольной пирамиде $SABC$ сторона основания $AB$ равна ${p["a"]}$, а боковое ребро $SA$ равно '
                f'${tx(S(p["s2"]))}$. На рёбрах $AB$ и $SB$ отмечены точки $M$ и $K$, причём $AM={p["am"]}$, $SK:KB={sk.p}:{sk.q}$.\n\n'
                'а) Докажите, что плоскость $CKM$ перпендикулярна плоскости $ABC$.\n\nб) Найдите объём пирамиды $BCKM$.')

    def solution(self, p):
        a, m, lam, so, sbcm, v = self._v(p)
        am = p['am']
        return (
            'а) Пусть $O$ — центр основания, $BE$ — медиана, $SO$ — высота; проекция $K\'$ точки $K$ лежит на $BO$ и '
            f'$\\frac{{BK\'}}{{BO}}=\\frac{{BK}}{{BS}}={tx(lam)}$. Пусть $CM$ пересекает $BE$ в точке $P$. По теореме Менелая для треугольника '
            '$ABE$ и прямой $CPM$: $\\frac{AM}{MB}\\cdot\\frac{BP}{PE}\\cdot\\frac{EC}{CA}=1$, то есть '
            f'$\\frac{{{am}}}{{{tx(m)}}}\\cdot\\frac{{BP}}{{PE}}\\cdot\\frac12=1$, $\\frac{{BP}}{{PE}}={tx(2 * m / am)}$, '
            f'$\\frac{{BP}}{{BE}}={tx(2 * m / (a + m))}$ и $\\frac{{BP}}{{BO}}=\\frac32\\cdot {tx(2 * m / (a + m))}={tx(lam)}$. Значит, $P=K\'$: '
            'перпендикуляр $KK\'$ к основанию лежит в плоскости $CKM$, и эта плоскость перпендикулярна $ABC$.\n\n'
            f'б) $OB=\\frac{{AB}}{{\\sqrt3}}$, $SO=\\sqrt{{SB^2-OB^2}}=\\sqrt{{{p["s2"]}-{tx(a ** 2 / 3)}}}={tx(so)}$, '
            f'$KK\'={tx(lam)}\\cdot SO={tx(lam * so)}$. $S_{{BCM}}=\\frac12\\cdot BM\\cdot BC\\sin 60^\\circ={tx(sbcm)}$.\n\n'
            f'$$V_{{BCKM}}=\\frac13 S_{{BCM}}\\cdot KK\'=\\frac13\\cdot {tx(sbcm)}\\cdot {tx(lam * so)}={tx(v)}.$$')

    def figure(self, p):
        A, B, C, Sv, M, K = self._pts(p)
        return g.draw({'A': A, 'B': B, 'C': C, 'S': Sv}, extra={'M': M, 'K': K}, section_names=['M', 'K', 'C'], azim=195, elev=14)

    def sample(self, rng):
        a = rng.choice([3, 4, 6, 8, 9, 12])
        am = rng.randint(1, a - 1)
        lam = sp.Rational(3 * (a - am), 2 * a - am)
        if lam >= 1 or (1 - lam) / lam > 5 or ((1 - lam) / lam).q > 5:
            return None
        s2 = rng.randint(a * a // 3 + 1, a * a // 3 + 40)
        return dict(a=a, s2=s2, am=am)


class PrismRhombusMid(Solved):
    """Правильная четырёхугольная призма: сечение MB₁KD — ромб ⇒ M — середина AA₁; высота по площадям"""
    number, topic = 14, SECTIONS
    fipi = {'16C715': dict(sb=3, sr=6)}

    def _h(self, p):
        sb, sr = sp.Integer(p['sb']), sp.Integer(p['sr'])
        return sp.radsimp(S(2 * sr ** 2 / sb - 2 * sb))

    def answer(self, p):
        return Answer.num(self._h(p))

    def check(self, p):
        h = float(self._h(p))
        a = math.sqrt(p['sb'])
        pts = box(a, a, h)
        M, K = (0.0, 0.0, h / 2), (a, a, h / 2)
        sec = g.section(list(pts.values()), g.plane(pts['B1'], pts['D'], M))
        assert g.on_plane(g.plane(pts['B1'], pts['D'], M), K)
        sides = [g.dist(sec[i], sec[(i + 1) % 4]) for i in range(4)]
        assert max(sides) - min(sides) < 1e-9
        assert g.close(g.polygon_area(sec), p['sr'])
        return h

    def condition(self, p):
        return ('Дана правильная четырёхугольная призма $ABCDA_1B_1C_1D_1$. Плоскость $\\alpha$ проходит через вершины $B_1$ и $D$ и '
                'пересекает рёбра $AA_1$ и $CC_1$ в точках $M$ и $K$. Известно, что четырёхугольник $MB_1KD$ — ромб.\n\n'
                'а) Докажите, что точка $M$ — середина ребра $AA_1$.\n\n'
                f'б) Найдите высоту призмы, если площадь её основания равна ${p["sb"]}$, а площадь ромба $MB_1KD$ равна ${p["sr"]}$.')

    def solution(self, p):
        sb, sr = sp.Integer(p['sb']), sp.Integer(p['sr'])
        h = self._h(p)
        return (
            'а) Пусть $a$ — сторона основания, $h$ — высота призмы, $AM=x$. В ромбе $MB_1=MD$: '
            '$MB_1^2=A_1B_1^2+A_1M^2=a^2+(h-x)^2$, $MD^2=AD^2+AM^2=a^2+x^2$. Отсюда $h-x=x$, $x=\\frac h2$ — $M$ середина $AA_1$.\n\n'
            'б) Аналогично $K$ — середина $CC_1$, поэтому $MK\\parallel AC$ и $MK=AC=a\\sqrt2$, '
            f'$a^2={sb}$. Диагональ $B_1D=\\sqrt{{2a^2+h^2}}$. Площадь ромба $\\frac12\\cdot MK\\cdot B_1D=\\frac12\\sqrt{{2a^2}}\\cdot'
            f'\\sqrt{{2a^2+h^2}}={sr}$, откуда $2a^2(2a^2+h^2)={4 * sr ** 2}$, $2a^2+h^2={tx(4 * sr ** 2 / (2 * sb))}$, '
            f'$h^2={tx(h ** 2)}$, $h={tx(h)}$.')

    def figure(self, p):
        h = float(self._h(p))
        a = math.sqrt(p['sb'])
        pts = box(a, a, h)
        return g.draw(pts, extra={'M': (0.0, 0.0, h / 2), 'K': (a, a, h / 2)}, section_names=['M', 'B1', 'K', 'D'], elev=20)

    def sample(self, rng):
        sb = rng.choice([1, 2, 3, 4, 6, 8, 9])
        sr = rng.randint(sb + 1, 4 * sb + 6)
        if 2 * sr ** 2 / sb - 2 * sb <= 0:
            return None
        return dict(sb=sb, sr=sr)


class QuadPyramidMidMK(Solved):
    """Правильная четырёхугольная пирамида, M — середина AB, K — середина SD: MK ∥ SBC; высота/объём по углу MK с основанием"""
    number, topic = 14, ANGLES
    fipi = {'5F0c14': dict(a=24, phi=30, ask='volume'), '135c80': dict(a=12, phi=60, ask='height'),
            '325286': dict(a=24, phi=30, ask='height')}

    def _H(self, p):
        a = sp.Integer(p['a'])
        mk = a * S(10) / 4
        return a, mk, sp.radsimp(2 * mk * sp.tan(sp.rad(p['phi'])))

    def answer(self, p):
        a, mk, H = self._H(p)
        return Answer.num(H if p['ask'] == 'height' else sp.radsimp(a ** 2 * H / 3))

    def check(self, p):
        H = float(self._H(p)[2])
        pts = quad_pyramid(p['a'], h=H)
        M, K = g.mid(pts['A'], pts['B']), g.mid(pts['S'], pts['D'])
        assert abs(g.dot(g.sub(K, M), g.plane(pts['S'], pts['B'], pts['C'])[0])) < 1e-9
        assert g.close(g.deg(g.angle_line_plane(g.sub(K, M), ((0, 0, 1), 0))), p['phi'])
        return H if p['ask'] == 'height' else g.volume(list(pts.values()))

    def condition(self, p):
        if p['ask'] == 'volume':
            return ('В правильной четырёхугольной пирамиде $SABCD$ точка $M$ — середина ребра $AB$. Через $M$ проведена плоскость '
                    '$\\alpha$, параллельная плоскости $SBC$ и пересекающая ребро $SD$ в точке $K$.\n\nа) Докажите, что $K$ — середина '
                    f'ребра $SD$.\n\nб) Найдите объём пирамиды, если $AB={p["a"]}$, а угол между прямой $MK$ и плоскостью основания '
                    f'равен ${p["phi"]}^\\circ$.')
        return ('В правильной четырёхугольной пирамиде $SABCD$ точки $M$ и $K$ — середины рёбер $AB$ и $SD$.\n\n'
                'а) Докажите, что прямая $MK$ параллельна плоскости $SBC$.\n\n'
                f'б) Найдите высоту пирамиды, если $AB={p["a"]}$, а угол между прямой $MK$ и плоскостью основания равен ${p["phi"]}^\\circ$.')

    def solution(self, p):
        a, mk, H = self._H(p)
        phi = p['phi']
        if p['ask'] == 'volume':
            t = ('а) Плоскость $\\alpha\\parallel SBC$ пересекает основание по прямой $MN\\parallel BC$, $N\\in CD$; $M$ — середина $AB$, '
                 'значит, $N$ — середина $CD$. Плоскость $\\alpha$ пересекает грань $SCD$ по прямой $NK\\parallel SC$, поэтому $NK$ — '
                 'средняя линия треугольника $SCD$ и $K$ — середина $SD$.\n\n')
        else:
            t = ('а) Пусть $N$ — середина $CD$. $MN\\parallel BC$, $NK$ — средняя линия треугольника $SCD$, $NK\\parallel SC$. '
                 'Две пересекающиеся прямые плоскости $MNK$ параллельны плоскости $SBC$, поэтому $MNK\\parallel SBC$, и прямая $MK$, '
                 'лежащая в плоскости $MNK$, параллельна плоскости $SBC$.\n\n')
        t += ('б) Пусть $O$ — центр основания, $SO=h$. Проекция $K\'$ точки $K$ — середина $OD$, $KK\'=\\frac h2$, и угол между $MK$ '
              'и основанием — это $\\angle KMK\'$. Введём координаты с началом $O$ и осями, параллельными сторонам основания: '
              f'$M\\left(0;-\\frac{{a}}{{2}}\\right)$, $K\'\\left(-\\frac a4;\\frac a4\\right)$, '
              f'$MK\'=\\sqrt{{\\frac{{a^2}}{{16}}+\\frac{{9a^2}}{{16}}}}=\\frac{{a\\sqrt{{10}}}}{{4}}={tx(mk)}$.\n\n'
              f'$$\\frac h2=MK\'\\cdot\\operatorname{{tg}}{phi}^\\circ,\\qquad h=2\\cdot {tx(mk)}\\cdot {tx(sp.tan(sp.rad(phi)))}={tx(H)}.$$')
        if p['ask'] == 'height':
            return t
        return t + f'\n\n$$V=\\frac13\\cdot AB^2\\cdot h=\\frac13\\cdot {a ** 2}\\cdot {tx(H)}={tx(sp.radsimp(a ** 2 * H / 3))}.$$'

    def figure(self, p):
        pts = quad_pyramid(p['a'], h=float(self._H(p)[2]))
        M, K, N = g.mid(pts['A'], pts['B']), g.mid(pts['S'], pts['D']), g.mid(pts['C'], pts['D'])
        return g.draw(pts, extra={'M': M, 'K': K, 'N': N}, segments=[('M', 'K'), ('M', 'N'), ('N', 'K')], azim=140)

    def sample(self, rng):
        return dict(a=rng.choice([4, 6, 8, 12, 16, 20, 24]), phi=rng.choice([30, 45, 60]), ask=rng.choice(['height', 'volume']))


class OrthoTetra(Solved):
    """Пирамида ABCD: DA, DB, DC попарно перпендикулярны, AB = BC = CA ⇒ правильная; сечение MNB"""
    number, topic = 14, DIST
    fipi = {'5D991D': dict(d=6, p=1, q=2, ask='dist'), '429E53': dict(d=5, p=2, q=3, ask='area')}

    def _v(self, p):
        d = sp.Integer(p['d'])
        dm = d * r(p['p'], p['p'] + p['q'])
        return d, dm

    def answer(self, p):
        d, dm = self._v(p)
        if p['ask'] == 'dist':
            return Answer.num(sp.radsimp(1 / S(2 / dm ** 2 + 1 / d ** 2)))
        mn, mb = dm * S(2), S(dm ** 2 + d ** 2)
        return Answer.num(sp.radsimp(mn / 2 * S(mb ** 2 - mn ** 2 / 4)))

    def _pts(self, p):
        d = float(p['d'])
        D, A, B, C = (0.0, 0.0, 0.0), (d, 0.0, 0.0), (0.0, d, 0.0), (0.0, 0.0, d)
        t = p['p'] / (p['p'] + p['q'])
        return D, A, B, C, g.lerp(D, A, t), g.lerp(D, C, t)

    def check(self, p):
        D, A, B, C, M, N = self._pts(p)
        pl = g.plane(M, N, B)
        return g.dist_point_plane(D, pl) if p['ask'] == 'dist' else g.polygon_area([M, N, B])

    def condition(self, p):
        d = sp.Integer(p['d'])
        q = 'расстояние от точки $D$ до плоскости $MNB$' if p['ask'] == 'dist' else 'площадь сечения $MNB$'
        return (f'В пирамиде $ABCD$ рёбра $DA$, $DB$ и $DC$ попарно перпендикулярны, а $AB=BC=AC={tx(d * S(2))}$.\n\n'
                'а) Докажите, что эта пирамида правильная.\n\n'
                f'б) На рёбрах $DA$ и $DC$ отмечены точки $M$ и $N$, причём $DM:MA=DN:NC={p["p"]}:{p["q"]}$. Найдите {q}.')

    def solution(self, p):
        d, dm = self._v(p)
        t = ('а) По теореме Пифагора $AB^2=DA^2+DB^2$, $BC^2=DB^2+DC^2$, $AC^2=DA^2+DC^2$. Из $AB=BC=AC$ следует $DA=DB=DC$. '
             'Основание $ABC$ — правильный треугольник, боковые рёбра равны, поэтому вершина $D$ проецируется в центр основания: '
             'пирамида правильная.\n\n'
             f'б) $DA=DB=DC=\\frac{{AB}}{{\\sqrt2}}={d}$, $DM=DN={tx(dm)}$. ')
        a = self.answer(p)
        if p['ask'] == 'dist':
            return t + ('В тетраэдре $DMNB$ рёбра при вершине $D$ попарно перпендикулярны. Его объём $V=\\frac16\\,DM\\cdot DN\\cdot DB$, '
                        'а искомое расстояние $h=\\frac{3V}{S_{MNB}}$. Удобнее известная формула для такого тетраэдра: '
                        '$\\frac1{h^2}=\\frac1{DM^2}+\\frac1{DN^2}+\\frac1{DB^2}$ (она следует из того, что основание высоты — '
                        'ортоцентр треугольника $MNB$). Получаем\n\n'
                        f'$$\\frac1{{h^2}}=\\frac1{{{tx(dm ** 2)}}}+\\frac1{{{tx(dm ** 2)}}}+\\frac1{{{d ** 2}}}={tx(2 / dm ** 2 + 1 / d ** 2)},'
                        f'\\qquad h={a.display.strip("$")}.$$')
        mn, mb = dm * S(2), S(dm ** 2 + d ** 2)
        hh = S(mb ** 2 - mn ** 2 / 4)
        return t + (f'$MN=DM\\sqrt2={tx(mn)}$, $MB=NB=\\sqrt{{DM^2+DB^2}}={tx(mb)}$. Треугольник $MNB$ равнобедренный, его высота '
                    f'$\\sqrt{{MB^2-\\frac{{MN^2}}{{4}}}}=\\sqrt{{{tx(mb ** 2)}-{tx(mn ** 2 / 4)}}}={tx(hh)}$.\n\n'
                    f'$$S_{{MNB}}=\\frac12\\cdot {tx(mn)}\\cdot {tx(hh)}={a.display.strip("$")}.$$')

    def figure(self, p):
        D, A, B, C, M, N = self._pts(p)
        return g.draw({'D': D, 'A': A, 'B': B, 'C': C}, extra={'M': M, 'N': N}, section_names=['M', 'N', 'B'], azim=135, elev=25)

    def sample(self, rng):
        pp, q = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3), (2, 3), (3, 2)])
        return dict(d=(pp + q) * rng.randint(1, 3), p=pp, q=q, ask=rng.choice(['dist', 'area']))


class QuadPyramidABMN(Solved):
    """Сечение ABMN правильной четырёхугольной пирамиды с AB = BM = AN = k·MN: SM:MC = 1:(k−1); косинус угла с основанием"""
    number, topic = 14, ANGLES
    fipi = {'33A81c': dict(k=5)}

    def answer(self, p):
        k = sp.Integer(p['k'])
        return Answer.num(sp.radsimp(S((k + 1) / (3 * k - 1))))

    def check(self, p):
        k, a = p['k'], 1.0
        s = math.sqrt(k / (k - 1))
        pts = quad_pyramid(a, s)
        M, N = g.lerp(pts['S'], pts['C'], 1 / k), g.lerp(pts['S'], pts['D'], 1 / k)
        assert g.close(g.dist(pts['B'], M), a) and g.close(g.dist(M, N), a / k)
        return math.cos(g.angle_planes(g.plane(pts['A'], pts['B'], M), ((0, 0, 1), 0)))

    def condition(self, p):
        k = p['k']
        return ('В правильной четырёхугольной пирамиде $SABCD$ через ребро $AB$ проведена плоскость $\\alpha$, пересекающая боковые '
                f'рёбра $SC$ и $SD$ в точках $M$ и $N$. Известно, что $AB=BM=AN={k}MN$.\n\n'
                f'а) Докажите, что точки $M$ и $N$ делят рёбра $SC$ и $SD$ в отношении $1:{k - 1}$, считая от вершины $S$.\n\n'
                'б) Найдите косинус угла между плоскостью основания и плоскостью $\\alpha$.')

    def solution(self, p):
        k = sp.Integer(p['k'])
        s2 = k / (k - 1)
        h2 = s2 - r(1, 2)
        cos = sp.radsimp(S((k + 1) / (3 * k - 1)))
        return (
            'а) $AB\\parallel CD$, поэтому $AB\\parallel SCD$, и плоскость $\\alpha$, содержащая $AB$, пересекает грань $SCD$ по прямой '
            f'$MN\\parallel CD$. Из подобия треугольников $SMN$ и $SCD$: $\\frac{{SM}}{{SC}}=\\frac{{MN}}{{CD}}=\\frac{{MN}}{{AB}}=\\frac1{{{k}}}$, '
            f'то есть $SM:MC=1:{k - 1}$ (аналогично для $N$).\n\n'
            f'б) Пусть $AB=a$, $SB=SC=s$. В треугольнике $BMC$: $MC=\\frac{{{k - 1}}}{{{k}}}s$, $\\cos\\angle SCB=\\frac{{a/2}}{{s}}$, '
            f'$BM^2=a^2+MC^2-2a\\cdot MC\\cdot\\frac{{a}}{{2s}}=a^2+\\frac{{{(k - 1) ** 2}}}{{{k ** 2}}}s^2-\\frac{{{k - 1}}}{{{k}}}a^2$. '
            f'Условие $BM=a$ даёт $\\frac{{{(k - 1) ** 2}}}{{{k ** 2}}}s^2=\\frac{{{k - 1}}}{{{k}}}a^2$, $s^2={tx(s2)}a^2$, и высота пирамиды '
            f'$h^2=s^2-\\frac{{a^2}}{{2}}={tx(h2)}a^2$.\n\n'
            'Пусть $P$ и $Q$ — середины $AB$ и $CD$, $R$ — середина $MN$, $O$ — центр основания. Плоскость $SPQ$ перпендикулярна $AB$, '
            'поэтому угол между $\\alpha$ и основанием равен $\\angle RPQ$. Введём координаты: $O$ — начало, ось $Oy$ по $PQ$, ось $Oz$ по $OS$: '
            f'$P\\left(0;-\\frac a2;0\\right)$, $R=S+\\frac1{{{k}}}(Q-S)=\\left(0;\\frac{{a}}{{{2 * k}}};{tx(r(k - 1, k))}h\\right)$, '
            f'$\\overrightarrow{{PR}}=\\left(0;{tx(r(k + 1, 2 * k))}a;{tx(r(k - 1, k))}h\\right)$.\n\n'
            f'$$\\cos\\angle RPQ=\\frac{{{tx(r(k + 1, 2 * k))}a}}{{\\sqrt{{{tx(r(k + 1, 2 * k) ** 2)}a^2+{tx(r(k - 1, k) ** 2)}\\cdot {tx(h2)}a^2}}}}={tx(cos)}.$$')

    def figure(self, p):
        k = p['k']
        pts = quad_pyramid(4.0, 4.0 * math.sqrt(k / (k - 1)))
        M, N = g.lerp(pts['S'], pts['C'], 1 / k), g.lerp(pts['S'], pts['D'], 1 / k)
        return g.draw(pts, extra={'M': M, 'N': N}, section_names=['A', 'B', 'M', 'N'])

    def sample(self, rng):
        return dict(k=rng.choice([3, 4, 6, 7, 9, 11]))


class PrismTrapezoidMKC(Solved):
    """Прямая призма над равнобедренной трапецией: A₁M = AD − BC, K — середина DD₁, ∠MKC = 90°"""
    number, topic = 14, ANGLES
    fipi = {'72412D': dict(x=3, y=2, ask='tan'), 'C87061': dict(x=3, y=2, ask='area')}

    def _v(self, p):
        x, y = sp.Integer(p['x']), sp.Integer(p['y'])
        e = (x - y) / 2
        t = e * S(3)
        h = 2 * S(y * e)
        dist = sp.radsimp(y * t / S((y + e) ** 2 + t ** 2))
        tan = sp.radsimp(h / 2 / dist)
        cos = sp.radsimp(1 / S(1 + tan ** 2))
        trap = (x + y) / 2 * t
        tri = (x - y) * (x - y) ** 2 / x * S(3) / 4
        sproj = sp.radsimp(trap - tri)
        return x, y, e, t, h, dist, tan, cos, trap, tri, sproj

    def answer(self, p):
        x, y, e, t, h, dist, tan, cos, trap, tri, sproj = self._v(p)
        return Answer.num(tan if p['ask'] == 'tan' else sp.radsimp(sproj / cos))

    def _pts(self, p):
        x, y, e, t, h, *_ = (float(v) for v in self._v(p))
        base = {'A': (0.0, 0.0), 'B': (e, t), 'C': (x - e, t), 'D': (x, 0.0)}
        pts = prism(base, h)
        M = (x - y, 0.0, h)
        K = (x, 0.0, h / 2)
        return pts, M, K

    def check(self, p):
        pts, M, K = self._pts(p)
        C = pts['C']
        assert g.perpendicular(g.sub(M, K), g.sub(C, K))
        pl = g.plane(M, K, C)
        assert abs(g.dot(pl[0], g.sub(pts['D'], pts['B']))) < 1e-9
        assert g.on_plane(pl, g.mid(pts['B'], pts['B1']))
        if p['ask'] == 'tan':
            return math.tan(g.angle_planes(pl, ((0, 0, 1), 0)))
        return g.polygon_area(g.section(list(pts.values()), pl))

    def condition(self, p):
        x, y = p['x'], p['y']
        cond = (f'В основании прямой призмы $ABCDA_1B_1C_1D_1$ лежит равнобедренная трапеция $ABCD$ с основаниями $AD={x}$ и $BC={y}$. '
                f'Точка $M$ делит ребро $A_1D_1$ в отношении $A_1M:MD_1={x - y}:{y}$, а точка $K$ — середина ребра $DD_1$.\n\n')
        if p['ask'] == 'tan':
            return cond + ('а) Докажите, что плоскость $MKC$ параллельна прямой $BD$.\n\nб) Найдите тангенс угла между плоскостью $MKC$ '
                           'и плоскостью основания призмы, если $\\angle MKC=90^\\circ$, $\\angle ADC=60^\\circ$.')
        return cond + ('а) Докажите, что плоскость $MKC$ делит отрезок $BB_1$ пополам.\n\nб) Найдите площадь сечения призмы плоскостью '
                       '$MKC$, если $\\angle MKC=90^\\circ$, $\\angle ADC=60^\\circ$.')

    def solution(self, p):
        x, y, e, t, h, dist, tan, cos, trap, tri, sproj = self._v(p)
        base = (f'$MD_1={y}=BC$. Прямая $MK$ пересекает прямую $AD$ в точке $X$; треугольники $KD_1M$ и $KDX$ равны ($KD=KD_1$, '
                'вертикальные углы, прямые углы при $D$ и $D_1$), поэтому $DX=D_1M=BC$. Так как $DX\\parallel BC$ и $DX=BC$, $BCXD$ — '
                'параллелограмм и $CX\\parallel BD$. Прямая $CX$ лежит в плоскости $MKC$, значит, $BD\\parallel MKC$.')
        if p['ask'] == 'tan':
            t1 = 'а) ' + base + '\n\n'
        else:
            t1 = ('а) ' + base + ' Плоскость $BDD_1$ содержит прямую $BD\\parallel MKC$, поэтому пересекает плоскость $MKC$ по прямой '
                  '$KL\\parallel BD$, $L\\in BB_1$. $BDKL$ — параллелограмм, $BL=DK=\\frac12 BB_1$: $L$ — середина $BB_1$.\n\n')
        t2 = (f'б) В трапеции с углом $60^\\circ$: боковая сторона $CD=\\frac{{AD-BC}}{{2\\cos 60^\\circ}}={tx(2 * e)}$, высота '
              f'${tx(t)}$. Пусть $AA_1=h$. $KM^2=MD_1^2+D_1K^2={y ** 2}+\\frac{{h^2}}{{4}}$, $KC^2=CD^2+DK^2={tx(4 * e ** 2)}+\\frac{{h^2}}{{4}}$, '
              f'$MC^2=h^2+M\'C^2$, где $M\'$ — проекция $M$ ($AM\'={x - y}$); $M\'C^2={tx((x - y - (x - e)) ** 2 + t ** 2)}$. '
              f'По теореме Пифагора для треугольника $MKC$: ${tx(y ** 2 + 4 * e ** 2)}+\\frac{{h^2}}{{2}}=h^2+{tx((x - y - (x - e)) ** 2 + t ** 2)}$, '
              f'откуда $h={tx(h)}$.\n\n'
              'Плоскость $MKC$ пересекает основание по прямой $CX$. Пусть $DH\\perp CX$; по теореме о трёх перпендикулярах $KH\\perp CX$ и '
              '$\\angle KHD$ — линейный угол между плоскостью сечения и основанием. В треугольнике $DCX$: $DX=' + f'{y}$, '
              f'высота из $C$ равна ${tx(t)}$, $CX=BD=\\sqrt{{{tx((y + e) ** 2)}+{tx(t ** 2)}}}={tx(S((y + e) ** 2 + t ** 2))}$, поэтому '
              f'$DH=\\frac{{DX\\cdot {tx(t)}}}{{CX}}={tx(dist)}$. $\\operatorname{{tg}}\\angle KHD=\\frac{{DK}}{{DH}}=\\frac{{{tx(h / 2)}}}{{{tx(dist)}}}={tx(tan)}$.')
        if p['ask'] == 'tan':
            return t1 + t2
        return t1 + t2 + (
            '\n\nСечение: плоскость пересекает верхнее основание по прямой $MT\\parallel CX\\parallel B_1D_1$, $T\\in A_1B_1$, '
            f'$\\frac{{A_1T}}{{A_1B_1}}=\\frac{{A_1M}}{{A_1D_1}}={tx(r(p["x"] - p["y"], p["x"]))}$; сечение — пятиугольник $MTLCK$. '
            'Его проекция на основание — трапеция $ABCD$ без треугольника $AM\'T\'$:\n\n'
            f'$$S_{{\\text{{пр}}}}={tx(trap)}-\\frac12\\cdot {x - y}\\cdot {tx((x - y) ** 2 / x)}\\cdot\\frac{{\\sqrt3}}{{2}}={tx(sproj)}.$$\n\n'
            f'$\\cos\\angle KHD=\\frac{{1}}{{\\sqrt{{1+\\operatorname{{tg}}^2}}}}={tx(cos)}$, $$S=\\frac{{S_{{\\text{{пр}}}}}}{{\\cos\\angle KHD}}='
            f'{tx(sp.radsimp(sproj / cos))}.$$')

    def figure(self, p):
        pts, M, K = self._pts(p)
        pl = g.plane(M, K, pts['C'])
        sec = g.section(list(pts.values()), pl)
        L = g.mid(pts['B'], pts['B1'])
        T = g.line_plane(pts['A1'], pts['B1'], pl)
        return g.draw(pts, extra={'M': M, 'K': K, 'L': L, 'T': T}, section_names=['M', 'T', 'L', 'C', 'K'] if len(sec) == 5 else [],
                      elev=22)

    def sample(self, rng):
        x = rng.randint(3, 9)
        y = rng.randint(1, x - 1)
        return dict(x=x, y=y, ask=rng.choice(['tan', 'area']))


class PrismPerpFace(Solved):
    """Правильная треугольная призма: плоскость через M ∈ AA₁ и K/C₁ перпендикулярно грани ABB₁A₁"""
    number, topic = 14, SECTIONS
    fipi = {'55B421': dict(a=12, p=2, q=1, ask='area'), 'ce2ec7': dict(s='sqrt(39)', p=1, q=2, ask='edge')}

    def _k(self, p):
        tt = r(p['p'], p['p'] + p['q'])                 # A₁M : AA₁
        return tt, S(tt ** 2 + r(1, 4)) * S(3) / 4      # S = a²·k

    def answer(self, p):
        tt, k = self._k(p)
        if p['ask'] == 'area':
            return Answer.num(sp.radsimp(sp.Integer(p['a']) ** 2 * k))
        return Answer.num(sp.radsimp(S(sp.sympify(p['s']) / k)))

    def check(self, p):
        tt, k = self._k(p)
        a = float(p['a']) if p['ask'] == 'area' else float(sp.radsimp(S(sp.sympify(p['s']) / k)))
        pts = prism(tri_base(a), a)
        M = g.lerp(pts['A1'], pts['A'], float(tt))
        K = g.mid(pts['A1'], pts['B1'])
        face = g.plane(pts['A'], pts['B'], pts['B1'])
        pl = g.plane_pv(M, g.sub(K, M), face[0])
        assert g.on_plane(pl, pts['C1'])
        sec = g.section(list(pts.values()), pl)
        area = g.polygon_area(sec)
        return area if p['ask'] == 'area' else (a if g.close(area, float(sp.sympify(p['s']))) else -1)

    def condition(self, p):
        pp, q = p['p'], p['q']
        if p['ask'] == 'area':
            return (f'В правильной треугольной призме $ABCA_1B_1C_1$ отмечены точки $M$ и $K$ на рёбрах $AA_1$ и $A_1B_1$, причём '
                    f'$A_1M:MA={pp}:{q}$, $A_1K=KB_1$. Через $M$ и $K$ проведена плоскость $\\alpha$, перпендикулярная грани $ABB_1A_1$.\n\n'
                    'а) Докажите, что плоскость $\\alpha$ проходит через вершину $C_1$.\n\n'
                    f'б) Найдите площадь сечения призмы плоскостью $\\alpha$, если все рёбра призмы равны ${p["a"]}$.')
        return (f'В правильной треугольной призме $ABCA_1B_1C_1$ все рёбра равны. На ребре $AA_1$ отмечена точка $M$, $AM:MA_1={q}:{pp}$. '
                'Через точки $M$ и $C_1$ проведена плоскость $\\alpha$, перпендикулярная грани $ABB_1A_1$.\n\n'
                'а) Докажите, что плоскость $\\alpha$ делит ребро $A_1B_1$ пополам.\n\n'
                f'б) Найдите высоту призмы, если площадь сечения призмы плоскостью $\\alpha$ равна ${tx(sp.sympify(p["s"]))}$.')

    def solution(self, p):
        tt, k = self._k(p)
        key = ('Пусть $K$ — середина $A_1B_1$. В правильном треугольнике $A_1B_1C_1$ медиана $C_1K$ — высота: $C_1K\\perp A_1B_1$; '
               'кроме того, $C_1K\\perp AA_1$ (боковое ребро перпендикулярно основанию). Значит, $C_1K$ перпендикулярна грани $ABB_1A_1$. ')
        if p['ask'] == 'area':
            t = ('а) ' + key + 'Плоскость $\\alpha$ перпендикулярна грани и проходит через $K$, поэтому содержит перпендикуляр к грани, '
                 'проведённый через $K$, — прямую $KC_1$. Значит, $C_1\\in\\alpha$.\n\n')
        else:
            t = ('а) ' + key + 'Плоскость $\\alpha$ проходит через $C_1$ перпендикулярно грани, поэтому содержит перпендикуляр $C_1K$ к ней, '
                 'и пересекает ребро $A_1B_1$ в его середине $K$.\n\n')
        t += ('б) Сечение — треугольник $MKC_1$ (плоскость отсекает тетраэдр $A_1MKC_1$), и $C_1K\\perp MK$. Пусть ребро призмы равно $a$: '
              f'$A_1M={tx(tt)}a$, $A_1K=\\frac a2$, $MK=a\\sqrt{{{tx(tt ** 2)}+\\frac14}}={tx(S(tt ** 2 + r(1, 4)))}a$, $C_1K=\\frac{{\\sqrt3}}{{2}}a$.\n\n'
              f'$$S_{{MKC_1}}=\\frac12\\cdot MK\\cdot C_1K={tx(k)}a^2.$$')
        if p['ask'] == 'area':
            return t + f'\n\nПри $a={p["a"]}$: $S={tx(sp.radsimp(sp.Integer(p["a"]) ** 2 * k))}$.'
        s = sp.sympify(p['s'])
        return t + f'\n\n${tx(k)}a^2={tx(s)}$, $a^2={tx(sp.radsimp(s / k))}$, $a={tx(sp.radsimp(S(s / k)))}$.'

    def figure(self, p):
        tt, k = self._k(p)
        pts = prism(tri_base(3.0), 3.0)
        M = g.lerp(pts['A1'], pts['A'], float(tt))
        K = g.mid(pts['A1'], pts['B1'])
        return g.draw(pts, extra={'M': M, 'K': K}, section_names=['M', 'K', 'C1'], elev=22)

    def sample(self, rng):
        pp, q = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3)])
        if rng.random() < 0.5:
            return dict(a=rng.choice([2, 4, 6, 8, 12]), p=pp, q=q, ask='area')
        a = rng.choice([2, 4, 6, 'sqrt(2)', '2*sqrt(3)', '2*sqrt(6)'])
        tt = r(pp, pp + q)
        s = sp.radsimp(sp.sympify(a) ** 2 * S(tt ** 2 + r(1, 4)) * S(3) / 4)
        return dict(s=str(s), p=pp, q=q, ask='edge')


class QuadPyramidEqTriangle(Solved):
    """Сечение правильной четырёхугольной пирамиды плоскостью ⊥ основанию — правильный треугольник ⇒ α ⊥ AC; отношение SK:KA"""
    number, topic = 14, SECTIONS
    fipi = {'eFF32e': dict(area='4*sqrt(3)', vol='18*sqrt(3)')}

    def _v(self, p):
        area, vol = sp.sympify(p['area']), sp.sympify(p['vol'])
        t = S(4 * area / S(3))
        ao = sp.nsimplify(sp.root(3 * vol / (2 * S(3)), 3))
        return t, ao

    def answer(self, p):
        t, ao = self._v(p)
        return Answer.ratio(ao - t / 2, t / 2)

    def check(self, p):
        t, ao = (float(x) for x in self._v(p))
        a = ao * math.sqrt(2)
        H = math.sqrt(3) * ao
        pts = quad_pyramid(a, h=H)
        assert g.close(g.volume(list(pts.values())), float(sp.sympify(p['vol'])))
        # плоскость ⊥ AC на расстоянии t/2 от A
        A, C = pts['A'], pts['C']
        u = g.unit(g.sub(C, A))
        pl = (u, g.dot(u, A) + t / 2)
        sec = g.section(list(pts.values()), pl)
        sides = [g.dist(sec[i], sec[(i + 1) % 3]) for i in range(3)]
        assert len(sec) == 3 and max(sides) - min(sides) < 1e-9
        K = g.line_plane(pts['S'], A, pl)
        return g.dist(pts['S'], K) / g.dist(K, A)

    def condition(self, p):
        return ('Плоскость $\\alpha$ перпендикулярна плоскости основания $ABCD$ правильной четырёхугольной пирамиды $SABCD$ и пересекает '
                f'ребро $SA$ в точке $K$. Сечение пирамиды плоскостью $\\alpha$ — правильный треугольник площадью ${tx(sp.sympify(p["area"]))}$.\n\n'
                'а) Докажите, что плоскость $\\alpha$ перпендикулярна прямой $AC$.\n\n'
                f'б) В каком отношении точка $K$ делит ребро $SA$, считая от точки $S$, если объём пирамиды равен ${tx(sp.sympify(p["vol"]))}$?')

    def solution(self, p):
        t, ao = self._v(p)
        vol = sp.sympify(p['vol'])
        return (
            'а) Сечение — треугольник $KPQ$, где $P$ и $Q$ лежат на сторонах основания, а $K$ — на ребре $SA$. Проекция $K\'$ точки $K$ на '
            'основание лежит на $AC$ (проекции $SA$) и на прямой $PQ$ ($\\alpha\\perp$ основанию). Из $KP=KQ$ следует $K\'P=K\'Q$ (равные '
            'наклонные имеют равные проекции), то есть $K\'$ — середина $PQ$. В треугольнике $APQ$ отрезок $AK\'$ — медиана и биссектриса '
            '($AC$ — биссектриса угла $A$ квадрата), поэтому треугольник равнобедренный, а медиана — высота: $PQ\\perp AC$. Плоскость $\\alpha$ '
            'содержит $PQ\\perp AC$ и перпендикуляр $KK\'\\perp AC$, значит, $\\alpha\\perp AC$.\n\n'
            f'б) Сторона треугольника $t$: $\\frac{{\\sqrt3}}{{4}}t^2={tx(sp.sympify(p["area"]))}$, $t={tx(t)}$. В равнобедренном прямоугольном '
            f'треугольнике $APQ$: $AK\'=\\frac{{PQ}}{{2}}={tx(t / 2)}$; высота сечения $KK\'=\\frac{{\\sqrt3}}{{2}}t={tx(t * S(3) / 2)}$.\n\n'
            'Пусть $O$ — центр основания, $SO=H$, $AO=x$. Из подобия треугольников $AKK\'$ и $ASO$: $\\frac{H}{x}=\\frac{KK\'}{AK\'}=\\sqrt3$, '
            f'$H=x\\sqrt3$. Площадь основания $2x^2$, $V=\\frac13\\cdot 2x^2\\cdot x\\sqrt3=\\frac{{2\\sqrt3}}{{3}}x^3={tx(vol)}$, откуда '
            f'$x^3={tx(sp.radsimp(3 * vol / (2 * S(3))))}$, $x={tx(ao)}$.\n\n'
            f'$\\frac{{SK}}{{KA}}=\\frac{{OK\'}}{{K\'A}}=\\frac{{{tx(ao)}-{tx(t / 2)}}}{{{tx(t / 2)}}}$, то есть $SK:KA={self.answer(p).display.strip("$")}$.')

    def figure(self, p):
        t, ao = (float(x) for x in self._v(p))
        pts = quad_pyramid(ao * math.sqrt(2), h=math.sqrt(3) * ao)
        A, C = pts['A'], pts['C']
        u = g.unit(g.sub(C, A))
        pl = (u, g.dot(u, A) + t / 2)
        P, Q, K = g.line_plane(A, pts['B'], pl), g.line_plane(A, pts['D'], pl), g.line_plane(pts['S'], A, pl)
        return g.draw(pts, extra={'P': P, 'Q': Q, 'K': K}, section_names=['P', 'K', 'Q'], segments=[('A', 'C')], azim=120)

    def sample(self, rng):
        ao = rng.randint(2, 6)
        t = rng.randint(1, 2 * ao - 1)
        return dict(area=str(sp.Integer(t) ** 2 * S(3) / 4), vol=str(2 * S(3) * ao ** 3 / 3))


class TetraPerpMN(Solved):
    """Правильный тетраэдр: MN ⊥ AB, CD; сечение плоскостью ⊥ MN через K ∈ BC — прямоугольник BK × KC"""
    number, topic = 14, SECTIONS
    fipi = {'0E8DDE': dict(bk=1, kc=3)}

    def answer(self, p):
        return Answer.num(sp.Integer(p['bk'] * p['kc']))

    def check(self, p):
        a = float(p['bk'] + p['kc'])
        A, B, C = (0.0, 0.0, 0.0), (a, 0.0, 0.0), (a / 2, a * math.sqrt(3) / 2, 0.0)
        O = g.centroid(A, B, C)
        D = (O[0], O[1], a * math.sqrt(2 / 3))
        M, N = g.mid(A, B), g.mid(C, D)
        assert g.perpendicular(g.sub(N, M), g.sub(B, A)) and g.perpendicular(g.sub(N, M), g.sub(D, C))
        K = g.ratio(B, C, p['bk'], p['kc'])
        return g.polygon_area(g.section([A, B, C, D], g.plane_nd(K, g.sub(N, M))))

    def condition(self, p):
        return ('В правильном тетраэдре $ABCD$ точки $M$ и $N$ — середины рёбер $AB$ и $CD$. Плоскость $\\alpha$ перпендикулярна прямой $MN$ '
                'и пересекает ребро $BC$ в точке $K$.\n\nа) Докажите, что прямая $MN$ перпендикулярна рёбрам $AB$ и $CD$.\n\n'
                f'б) Найдите площадь сечения тетраэдра плоскостью $\\alpha$, если $BK={p["bk"]}$, $KC={p["kc"]}$.')

    def solution(self, p):
        bk, kc = p['bk'], p['kc']
        return (
            'а) $MC$ и $MD$ — медианы равных правильных треугольников $ABC$ и $ABD$, поэтому $MC=MD$, и медиана $MN$ равнобедренного '
            'треугольника $MCD$ является высотой: $MN\\perp CD$. Аналогично $NA=NB$ и $MN\\perp AB$.\n\n'
            'б) $AB\\perp MN$ и $CD\\perp MN$, поэтому плоскость $\\alpha\\perp MN$ параллельна $AB$ и $CD$. Она пересекает грань $BCD$ по '
            'прямой $KL\\parallel CD$, грань $ABC$ — по прямой $KP\\parallel AB$; сечение — параллелограмм со сторонами, параллельными $AB$ и $CD$. '
            'В правильном тетраэдре противоположные рёбра перпендикулярны ($AB\\perp CD$: проекция $D$ — центр $ABC$, а $CO\\perp AB$), '
            f'поэтому сечение — прямоугольник. Ребро тетраэдра $BC={bk + kc}$.\n\n'
            f'$KL=CD\\cdot\\frac{{BK}}{{BC}}=BK={bk}$, $KP=AB\\cdot\\frac{{KC}}{{BC}}=KC={kc}$, $$S=KL\\cdot KP={bk}\\cdot {kc}={bk * kc}.$$')

    def figure(self, p):
        a = float(p['bk'] + p['kc'])
        A, B, C = (0.0, 0.0, 0.0), (a, 0.0, 0.0), (a / 2, a * math.sqrt(3) / 2, 0.0)
        O = g.centroid(A, B, C)
        D = (O[0], O[1], a * math.sqrt(2 / 3))
        M, N = g.mid(A, B), g.mid(C, D)
        K = g.ratio(B, C, p['bk'], p['kc'])
        pl = g.plane_nd(K, g.sub(N, M))
        L, P = g.line_plane(B, D, pl), g.line_plane(A, C, pl)
        Q = g.line_plane(A, D, pl)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D}, extra={'M': M, 'N': N, 'K': K, 'L': L, 'P': P, 'Q': Q},
                      segments=[('M', 'N')], section_names=['K', 'L', 'Q', 'P'])

    def sample(self, rng):
        a = rng.randint(3, 10)
        bk = rng.randint(1, a - 1)
        return dict(bk=bk, kc=a - bk)


class QuadPyramidKN(Solved):
    """Правильная четырёхугольная пирамида: плоскость через KN ∥ BC параллельна SA, а значит и SAD; угол с SBC"""
    number, topic = 14, ANGLES
    fipi = {'142CDC': dict(a=6, s=7, p=1, q=2), '876DD3': dict(a=4, s=7, p=1, q=3)}

    def answer(self, p):
        a, s = sp.Integer(p['a']), sp.Integer(p['s'])
        se2 = s ** 2 - a ** 2 / 4
        return Answer.angle(sp.Abs(2 * se2 - a ** 2) / (2 * se2), 'arccos')

    def check(self, p):
        pts = quad_pyramid(p['a'], p['s'])
        N = g.ratio(pts['D'], pts['C'], p['p'], p['q'])
        K = g.ratio(pts['S'], pts['C'], p['p'], p['q'])
        pl = g.plane_pv(N, g.sub(K, N), g.sub(pts['C'], pts['B']))
        assert abs(g.dot(pl[0], g.sub(pts['A'], pts['S']))) < 1e-9
        return g.angle_planes(pl, g.plane(pts['S'], pts['B'], pts['C']))

    def condition(self, p):
        pp, q = p['p'], p['q']
        return (f'В правильной четырёхугольной пирамиде $SABCD$ сторона основания $AB$ равна ${p["a"]}$, а боковое ребро $SA$ равно ${p["s"]}$. '
                f'На рёбрах $CD$ и $SC$ отмечены точки $N$ и $K$, причём $DN:NC=SK:KC={pp}:{q}$. Плоскость $\\alpha$ содержит прямую $KN$ '
                'и параллельна прямой $BC$.\n\nа) Докажите, что плоскость $\\alpha$ параллельна прямой $SA$.\n\n'
                'б) Найдите угол между плоскостями $\\alpha$ и $SBC$.')

    def solution(self, p):
        a, s = sp.Integer(p['a']), sp.Integer(p['s'])
        pp, q = p['p'], p['q']
        se2 = s ** 2 - a ** 2 / 4
        c = (2 * se2 - a ** 2) / (2 * se2)
        return (
            f'а) Плоскость $\\alpha\\parallel BC$ пересекает основание по прямой $NP\\parallel BC$ ($P\\in AB$, $AP:PB=DN:NC={pp}:{q}$) и грань '
            f'$SBC$ — по прямой $KL\\parallel BC$ ($L\\in SB$, $SL:LB=SK:KC={pp}:{q}$). Тогда $\\frac{{BP}}{{BA}}=\\frac{{BL}}{{BS}}=\\frac{{{q}}}{{{pp + q}}}$, '
            'и $PL\\parallel AS$. Прямая $PL$ лежит в $\\alpha$, значит, $\\alpha\\parallel SA$.\n\n'
            'б) Плоскость $\\alpha$ параллельна пересекающимся прямым $SA$ и $AD$ ($AD\\parallel BC$), поэтому $\\alpha\\parallel SAD$, и угол между '
            '$\\alpha$ и $SBC$ равен углу между плоскостями $SAD$ и $SBC$. Пусть $E$ и $F$ — середины $BC$ и $AD$: $SE\\perp BC$, $SF\\perp AD$, '
            'а линия пересечения плоскостей $SAD$ и $SBC$ параллельна $BC$; поэтому угол между плоскостями равен углу между $SE$ и $SF$.\n\n'
            f'$SE=SF=\\sqrt{{SB^2-\\frac{{BC^2}}{{4}}}}=\\sqrt{{{tx(se2)}}}$, $EF={a}$. '
            f'$$\\cos\\angle ESF=\\frac{{SE^2+SF^2-EF^2}}{{2\\,SE\\cdot SF}}=\\frac{{{tx(2 * se2)}-{a ** 2}}}{{{tx(2 * se2)}}}={tx(c)}.$$ '
            + ('Угол между плоскостями острый, поэтому он равен ' if c < 0 else 'Искомый угол ') + f'{self.answer(p).display}.')

    def figure(self, p):
        pts = quad_pyramid(p['a'], p['s'])
        N = g.ratio(pts['D'], pts['C'], p['p'], p['q'])
        K = g.ratio(pts['S'], pts['C'], p['p'], p['q'])
        P = g.ratio(pts['A'], pts['B'], p['p'], p['q'])
        L = g.ratio(pts['S'], pts['B'], p['p'], p['q'])
        return g.draw(pts, extra={'N': N, 'K': K, 'P': P, 'L': L}, section_names=['P', 'L', 'K', 'N'])

    def sample(self, rng):
        a = rng.choice([2, 4, 6, 8, 10])
        s = rng.randint(a // 2 + 2, a + 6)
        pp, q = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3)])
        return dict(a=a, s=s, p=pp, q=q)


class RectPyramidAPCQ(Solved):
    """Пирамида над прямоугольником (BC = AB√2), высота в центр: AP, CQ ⊥ SB ⇒ P — середина BQ; угол между гранями SBA и SBC"""
    number, topic = 14, ANGLES
    fipi = {'C185DD': dict(x='2*sqrt(2)', s=4)}

    def _v(self, p):
        x, s = sp.sympify(p['x']), sp.Integer(p['s'])
        bp = x ** 2 / (2 * s)
        ap2 = x ** 2 - bp ** 2
        cq2 = 2 * x ** 2 - 4 * bp ** 2
        pr2 = cq2 / 4
        ar2 = 3 * x ** 2 / 2
        c = sp.radsimp((ap2 + pr2 - ar2) / (2 * S(ap2) * S(pr2)))
        return x, s, bp, ap2, cq2, pr2, ar2, c

    def answer(self, p):
        return Answer.angle(self._v(p)[-1], 'arccos')

    def check(self, p):
        x, s = float(sp.sympify(p['x'])), float(p['s'])
        y = x * math.sqrt(2)
        A, B, C, D = (0.0, 0.0, 0.0), (x, 0.0, 0.0), (x, y, 0.0), (0.0, y, 0.0)
        O = g.centroid(A, B, C, D)
        Sv = (O[0], O[1], math.sqrt(s * s - (x * x + y * y) / 4))
        # двугранный угол при ребре SB: между перпендикулярами к SB в гранях
        u = g.unit(g.sub(Sv, B))
        pa = g.sub(A, g.add(B, g.mul(u, g.dot(g.sub(A, B), u))))
        pc = g.sub(C, g.add(B, g.mul(u, g.dot(g.sub(C, B), u))))
        bp, bq = g.dot(g.sub(A, B), u), g.dot(g.sub(C, B), u)
        assert g.close(bq, 2 * bp)
        return math.acos(g.dot(pa, pc) / g.norm(pa) / g.norm(pc))

    def condition(self, p):
        x = sp.sympify(p['x'])
        return (f'Основанием четырёхугольной пирамиды $SABCD$ является прямоугольник $ABCD$, причём $AB={tx(x)}$, $BC={tx(x * S(2))}$. '
                'Основанием высоты пирамиды является центр прямоугольника. Из вершин $A$ и $C$ опущены перпендикуляры $AP$ и $CQ$ на ребро $SB$.\n\n'
                'а) Докажите, что $P$ — середина отрезка $BQ$.\n\n'
                f'б) Найдите угол между гранями $SBA$ и $SBC$, если $SD={p["s"]}$.')

    def solution(self, p):
        x, s, bp, ap2, cq2, pr2, ar2, c = self._v(p)
        return (
            'а) Высота падает в центр прямоугольника, поэтому все боковые рёбра равны: $SA=SB=SC=SD$. В равнобедренном треугольнике $SAB$ '
            '$\\cos\\angle SBA=\\frac{AB/2}{SB}$, и $BP=AB\\cos\\angle SBA=\\frac{AB^2}{2SB}$. Аналогично $BQ=\\frac{BC^2}{2SB}$. '
            'Так как $BC^2=2AB^2$, $BQ=2BP$: $P$ — середина $BQ$.\n\n'
            f'б) $SB=SD={s}$. $BP=\\frac{{AB^2}}{{2SB}}={tx(bp)}$, $BQ={tx(2 * bp)}$. $AP=\\sqrt{{AB^2-BP^2}}={tx(S(ap2))}$, '
            f'$CQ=\\sqrt{{BC^2-BQ^2}}={tx(S(cq2))}$. В грани $SBC$ проведём $PR\\parallel QC$, $R\\in BC$: $PR\\perp SB$, $R$ — середина $BC$ '
            f'(так как $P$ — середина $BQ$), $PR=\\frac12 CQ={tx(S(pr2))}$. Угол $APR$ — линейный угол двугранного угла при ребре $SB$.\n\n'
            f'$AR^2=AB^2+BR^2={tx(ar2)}$. По теореме косинусов $$\\cos\\angle APR=\\frac{{AP^2+PR^2-AR^2}}{{2\\,AP\\cdot PR}}='
            f'\\frac{{{tx(ap2)}+{tx(pr2)}-{tx(ar2)}}}{{2\\cdot {tx(S(ap2))}\\cdot {tx(S(pr2))}}}={tx(c)}.$$')

    def figure(self, p):
        x, s = float(sp.sympify(p['x'])), float(p['s'])
        y = x * math.sqrt(2)
        A, B, C, D = (0.0, 0.0, 0.0), (x, 0.0, 0.0), (x, y, 0.0), (0.0, y, 0.0)
        O = g.centroid(A, B, C, D)
        Sv = (O[0], O[1], math.sqrt(s * s - (x * x + y * y) / 4))
        u = g.unit(g.sub(Sv, B))
        P = g.add(B, g.mul(u, g.dot(g.sub(A, B), u)))
        Q = g.add(B, g.mul(u, g.dot(g.sub(C, B), u)))
        return g.draw({'S': Sv, 'A': A, 'B': B, 'C': C, 'D': D}, extra={'P': P, 'Q': Q}, segments=[('A', 'P'), ('C', 'Q')], azim=200)

    def sample(self, rng):
        x = rng.choice(['2', '2*sqrt(2)', '4', '3*sqrt(2)', '6', 'sqrt(2)'])
        xv = float(sp.sympify(x))
        s = rng.randint(math.floor(xv * math.sqrt(3) / 2) + 1, math.floor(xv * 2) + 4)
        return dict(x=x, s=s)


class QuadPyramidONM(Solved):
    """Все рёбра правильной четырёхугольной пирамиды равны: плоскость через O ∥ SA, SN:ND задано; отрезок в грани SBC"""
    number, topic = 14, SECTIONS
    fipi = {'616CD3': dict(a=4, p=1, q=3)}

    def answer(self, p):
        a = sp.Integer(p['a'])
        cp = a * r(p['p'], p['p'] + p['q'])
        return Answer.num(sp.radsimp(S(a ** 2 / 4 + cp ** 2 - a / 2 * cp)))

    def check(self, p):
        pts = quad_pyramid(p['a'], p['a'])
        O = (0.0, 0.0, 0.0)
        N = g.ratio(pts['S'], pts['D'], p['p'], p['q'])
        pl = g.plane_pv(O, g.sub(pts['A'], pts['S']), g.sub(N, O))
        M = g.line_plane(pts['S'], pts['C'], pl)
        assert g.close(g.dist(pts['S'], M), g.dist(M, pts['C']))
        face = g.plane(pts['S'], pts['B'], pts['C'])
        on = [q for q in g.section(list(pts.values()), pl) if g.on_plane(face, q)]
        return g.dist(on[0], on[1])

    def condition(self, p):
        return (f'Все рёбра правильной четырёхугольной пирамиды $SABCD$ с основанием $ABCD$ равны ${p["a"]}$, точка $O$ — центр основания. '
                'Плоскость, параллельная прямой $SA$ и проходящая через точку $O$, пересекает рёбра $SC$ и $SD$ в точках $M$ и $N$, '
                f'причём $SN:ND={p["p"]}:{p["q"]}$.\n\nа) Докажите, что $M$ — середина ребра $SC$.\n\n'
                'б) Найдите длину отрезка, по которому плоскость $OMN$ пересекает грань $SBC$.')

    def solution(self, p):
        a = sp.Integer(p['a'])
        pp, q = p['p'], p['q']
        cp = a * r(pp, pp + q)
        ans = self.answer(p)
        return (
            'а) Плоскость параллельна $SA$, поэтому пересекает плоскость $SAC$ по прямой $OM\\parallel SA$. $O$ — середина $AC$, значит, $OM$ — '
            'средняя линия треугольника $SAC$ и $M$ — середина $SC$.\n\n'
            f'б) Плоскость пересекает грань $SAD$ по прямой $NQ\\parallel SA$, $Q\\in AD$, $\\frac{{DQ}}{{DA}}=\\frac{{DN}}{{DS}}=\\frac{{{q}}}{{{pp + q}}}$, '
            f'$AQ={tx(cp)}$. Прямая $QO$ при симметрии относительно $O$ переходит в себя и пересекает $BC$ в точке $P$ с $CP=AQ={tx(cp)}$. '
            'Плоскость пересекает грань $SBC$ по отрезку $MP$.\n\n'
            f'Грань $SBC$ — правильный треугольник, $MC=\\frac{{{a}}}{{2}}$, $\\angle C=60^\\circ$: '
            f'$$MP^2=MC^2+CP^2-MC\\cdot CP={tx(a ** 2 / 4)}+{tx(cp ** 2)}-{tx(a / 2 * cp)}={tx(a ** 2 / 4 + cp ** 2 - a / 2 * cp)},$$ '
            f'$MP={ans.display.strip("$")}$.')

    def figure(self, p):
        pts = quad_pyramid(p['a'], p['a'])
        O = (0.0, 0.0, 0.0)
        N = g.ratio(pts['S'], pts['D'], p['p'], p['q'])
        pl = g.plane_pv(O, g.sub(pts['A'], pts['S']), g.sub(N, O))
        M = g.line_plane(pts['S'], pts['C'], pl)
        Q, P = g.line_plane(pts['A'], pts['D'], pl), g.line_plane(pts['B'], pts['C'], pl)
        return g.draw(pts, extra={'O': O, 'M': M, 'N': N, 'Q': Q, 'P': P}, section_names=['Q', 'P', 'M', 'N'], azim=140)

    def sample(self, rng):
        pp, q = rng.choice([(1, 1), (1, 2), (1, 3), (2, 1), (3, 1), (2, 3)])
        return dict(a=rng.choice([2, 4, 6, 8, 12]), p=pp, q=q)


class BoxPerpBisector(Solved):
    """Параллелепипед: плоскость ⊥ AC₁ через её середину проходит через D₁ (AD₁ = AB); отношение на A₁B₁"""
    number, topic = 14, SECTIONS
    fipi = {'0B28A5': dict(c=5, b=3, h=4)}

    def answer(self, p):
        return Answer.ratio(p['b'] ** 2, p['h'] ** 2)

    def check(self, p):
        pts = box(p['c'], p['b'], p['h'])
        Mv = g.mid(pts['A'], pts['C1'])
        pl = g.plane_nd(Mv, g.sub(pts['C1'], pts['A']))
        assert g.on_plane(pl, pts['D1'])
        X = g.line_plane(pts['A1'], pts['B1'], pl)
        return g.dist(pts['A1'], X) / g.dist(X, pts['B1'])

    def condition(self, p):
        return (f'В прямоугольном параллелепипеде $ABCDA_1B_1C_1D_1$ $AB={p["c"]}$, $BC={p["b"]}$, $AA_1={p["h"]}$. Через середину $M$ '
                'диагонали $AC_1$ проведена плоскость $\\alpha$, перпендикулярная этой диагонали.\n\n'
                'а) Докажите, что плоскость $\\alpha$ содержит точку $D_1$.\n\n'
                'б) Найдите отношение, в котором плоскость $\\alpha$ делит ребро $A_1B_1$, считая от точки $A_1$.')

    def solution(self, p):
        c, b, h = p['c'], p['b'], p['h']
        x = r(c ** 2 + b ** 2 - h ** 2, 2 * c)
        return (
            'а) Плоскость, проходящая через середину отрезка $AC_1$ перпендикулярно ему, — множество точек, равноудалённых от $A$ и $C_1$. '
            f'$D_1A=\\sqrt{{AD^2+DD_1^2}}=\\sqrt{{{b ** 2}+{h ** 2}}}={c}$, $D_1C_1=AB={c}$. Значит, $D_1A=D_1C_1$ и $D_1\\in\\alpha$.\n\n'
            f'б) Пусть $X\\in A_1B_1$, $A_1X=x$. $X\\in\\alpha\\iff XA=XC_1$: $x^2+AA_1^2=(A_1B_1-x)^2+B_1C_1^2$, то есть '
            f'$x^2+{h ** 2}=({c}-x)^2+{b ** 2}$, ${2 * c}x={c ** 2 + b ** 2 - h ** 2}$, $x={tx(x)}$, $XB_1={tx(c - x)}$.\n\n'
            f'Отношение $A_1X:XB_1={self.answer(p).display.strip("$")}$.')

    def figure(self, p):
        pts = box(p['c'], p['b'], p['h'])
        Mv = g.mid(pts['A'], pts['C1'])
        pl = g.plane_nd(Mv, g.sub(pts['C1'], pts['A']))
        X = g.line_plane(pts['A1'], pts['B1'], pl)
        names, extra, spare = [], {'M': Mv, 'X': X}, iter('YZUVW')
        for q in g.section(list(pts.values()), pl):
            known = [n for n, v in {**pts, 'X': X}.items() if g.dist(v, q) < 1e-9]
            if known:
                names.append(known[0])
            else:
                n = next(spare)
                extra[n] = q
                names.append(n)
        return g.draw(pts, extra=extra, segments=[('A', 'C1')], section_names=names, elev=22)

    def sample(self, rng):
        b, h, c = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13), (6, 8, 10), (8, 6, 10), (8, 15, 17), (15, 8, 17)])
        return dict(c=c, b=b, h=h)


class PrismPQ(Solved):
    """Прямая призма, равнобедренное основание AB: PQ ⊥ AB; плоскость через середину BC перпендикулярно PQ"""
    number, topic = 14, SECTIONS
    fipi = {'82F7A1': dict(b=5, ask='PQ'), 'FA228B': dict(b=5, ask='A1C1')}

    def _v(self, p):
        b = sp.Integer(p['b'])
        c2 = b ** 2 - 1          # AB = 2, BC = b, AA₁ = 2
        return b, c2

    def answer(self, p):
        b, c2 = self._v(p)
        if p['ask'] == 'PQ':
            return Answer.ratio(c2, 16)
        s = r(1, 2) - 8 / c2
        return Answer.ratio(s, 1 - s)

    def _pts(self, p):
        b, c2 = self._v(p)
        c = math.sqrt(float(c2))
        base = {'A': (-1.0, 0.0), 'B': (1.0, 0.0), 'C': (0.0, c)}
        pts = prism(base, 2.0)
        P = g.ratio(pts['A'], pts['B'], 1, 3)
        Q = g.mid(pts['A1'], pts['C1'])
        M = g.mid(pts['B'], pts['C'])
        return pts, P, Q, M

    def check(self, p):
        pts, P, Q, M = self._pts(p)
        pl = g.plane_nd(M, g.sub(Q, P))
        assert abs(g.dot(pl[0], g.sub(pts['B'], pts['A']))) < 1e-9
        assert g.on_plane(pl, g.mid(pts['A'], pts['C']))
        if p['ask'] == 'PQ':
            X = g.line_plane(P, Q, pl)
            return g.dist(P, X) / g.dist(X, Q)
        X = g.line_plane(pts['A1'], pts['C1'], pl)
        return g.dist(pts['A1'], X) / g.dist(X, pts['C1'])

    def condition(self, p):
        base = ('В основании прямой призмы $ABCA_1B_1C_1$ лежит равнобедренный треугольник $ABC$ с основанием $AB$. Точка $P$ делит ребро '
                '$AB$ в отношении $AP:PB=1:3$, а точка $Q$ — середина ребра $A_1C_1$. Через середину $M$ ребра $BC$ проведена плоскость '
                '$\\alpha$, перпендикулярная отрезку $PQ$.\n\n')
        if p['ask'] == 'PQ':
            return base + ('а) Докажите, что плоскость $\\alpha$ параллельна ребру $AB$.\n\nб) Найдите отношение, в котором плоскость $\\alpha$ '
                           f'делит отрезок $PQ$, считая от точки $P$, если $AB=AA_1$, $AB:BC=2:{p["b"]}$.')
        return base + ('а) Докажите, что плоскость $\\alpha$ делит ребро $AC$ пополам.\n\nб) Найдите отношение, в котором плоскость $\\alpha$ '
                       f'делит ребро $A_1C_1$, считая от точки $A_1$, если $AB=AA_1$, $AB:BC=2:{p["b"]}$.')

    def solution(self, p):
        b, c2 = self._v(p)
        key = ('Пусть $H$ — середина $AB$, $Q\'$ — проекция $Q$ на основание (середина $AC$). $AP=\\frac14 AB=\\frac12 AH$, поэтому $P$ — '
               'середина $AH$, и $PQ\'$ — средняя линия треугольника $AHC$: $PQ\'\\parallel CH\\perp AB$. По теореме о трёх перпендикулярах '
               '$PQ\\perp AB$, и плоскость $\\alpha\\perp PQ$ параллельна $AB$ (она не содержит $AB$, так как $M\\notin AB$)')
        if p['ask'] == 'PQ':
            t = 'а) ' + key + '.\n\n'
        else:
            t = ('а) ' + key + '. Значит, $\\alpha$ пересекает основание по прямой через $M$, параллельной $AB$, — средней линии '
                 'треугольника $ABC$, и проходит через середину $AC$.\n\n')
        t += (f'б) Введём координаты: $H$ — начало, $AB=AA_1=2$, $BC={b}$, $CH=\\sqrt{{{b ** 2}-1}}=c$, $c^2={c2}$. '
              '$A(-1;0;0)$, $B(1;0;0)$, $C(0;c;0)$, $P\\left(-\\frac12;0;0\\right)$, $Q\\left(-\\frac12;\\frac c2;2\\right)$, '
              '$M\\left(\\frac12;\\frac c2;0\\right)$, $\\overrightarrow{PQ}=\\left(0;\\frac c2;2\\right)$. Плоскость $\\alpha$: '
              '$\\frac c2\\left(y-\\frac c2\\right)+2z=0$.\n\n')
        if p['ask'] == 'PQ':
            tt = r(c2, c2 + 16)
            return t + ('Точка $P+t\\overrightarrow{PQ}=\\left(-\\frac12;\\frac{tc}{2};2t\\right)$ лежит в $\\alpha$: '
                        f'$\\frac{{c^2}}{{4}}(t-1)+4t=0$, $t=\\frac{{c^2}}{{c^2+16}}={tx(tt)}$. Отношение ${self.answer(p).display.strip("$")}$.')
        s = r(1, 2) - 8 / c2
        return t + ('$A_1(-1;0;2)$, $C_1(0;c;2)$; точка $A_1+s\\overrightarrow{A_1C_1}=(-1+s;\\,sc;\\,2)$ лежит в $\\alpha$: '
                    f'$\\frac c2\\left(sc-\\frac c2\\right)+4=0$, $s=\\frac12-\\frac{{8}}{{c^2}}={tx(s)}$. '
                    f'Отношение ${self.answer(p).display.strip("$")}$.')

    def figure(self, p):
        pts, P, Q, M = self._pts(p)
        pl = g.plane_nd(M, g.sub(Q, P))
        X = g.line_plane(P, Q, pl)
        return g.draw(pts, extra={'P': P, 'Q': Q, 'M': M, 'X': X}, segments=[('P', 'Q')], elev=20)

    def sample(self, rng):
        return dict(b=rng.choice([5, 6, 7, 9]), ask=rng.choice(['PQ', 'A1C1']))


class QuadPyramidPerpSC(Solved):
    """Плоскость через O ⊥ SC проходит через B и D; отношение SK:KC по площади сечения"""
    number, topic = 14, SECTIONS
    fipi = {'5c14cA': dict(a=1, area='sqrt(2)/3')}

    def _v(self, p):
        a, area = sp.Integer(p['a']), sp.sympify(p['area'])
        ok = sp.radsimp(S(2) * area / a)
        oc = a / S(2)
        n = sp.nsimplify(ok ** 2 / (oc ** 2 - ok ** 2))
        return a, area, ok, oc, n

    def answer(self, p):
        return Answer.ratio(self._v(p)[-1], 1)

    def check(self, p):
        a, area, ok, oc, n = self._v(p)
        cosC = math.sqrt(1 - float(ok) ** 2 / float(oc) ** 2)
        sc = float(oc) / cosC
        H = math.sqrt(sc * sc - float(oc) ** 2)
        pts = quad_pyramid(p['a'], h=H)
        pl = g.plane_nd((0.0, 0.0, 0.0), g.sub(pts['C'], pts['S']))
        assert g.on_plane(pl, pts['B']) and g.on_plane(pl, pts['D'])
        sec = g.section(list(pts.values()), pl)
        assert g.close(g.polygon_area(sec), float(area))
        K = g.line_plane(pts['S'], pts['C'], pl)
        return g.dist(pts['S'], K) / g.dist(K, pts['C'])

    def condition(self, p):
        return (f'В правильной четырёхугольной пирамиде $SABCD$ известно, что $AB={p["a"]}$. Через точку $O$ пересечения диагоналей основания '
                'перпендикулярно ребру $SC$ проведена плоскость $\\alpha$.\n\nа) Докажите, что плоскость $\\alpha$ проходит через вершины $B$ и $D$.\n\n'
                f'б) В каком отношении плоскость $\\alpha$ делит ребро $SC$, считая от вершины $S$, если площадь сечения равна ${tx(sp.sympify(p["area"]))}$?')

    def solution(self, p):
        a, area, ok, oc, n = self._v(p)
        return (
            'а) $BD\\perp AC$ (диагонали квадрата) и $BD\\perp SO$ ($SO$ — высота), поэтому $BD\\perp SAC$ и $BD\\perp SC$. Плоскость $\\alpha$ '
            'проходит через $O$ перпендикулярно $SC$, а прямая $BD$ проходит через $O$ и перпендикулярна $SC$, значит, $BD\\subset\\alpha$.\n\n'
            'б) Пусть $K$ — точка пересечения $\\alpha$ с $SC$; $OK\\perp SC$, сечение — треугольник $BKD$ с высотой $OK$ ($OK\\perp BD$, так как '
            f'$BD\\perp SAC$). $S=\\frac12\\cdot BD\\cdot OK$, $BD={tx(a * S(2))}$, откуда $OK={tx(ok)}$. $OC=\\frac{{AC}}{{2}}={tx(oc)}$.\n\n'
            'В прямоугольном треугольнике $SOC$ высота $OK$ делит гипотенузу на отрезки $SK=\\frac{SO^2}{SC}$ и $KC=\\frac{OC^2}{SC}$, поэтому '
            f'$\\frac{{SK}}{{KC}}=\\frac{{SO^2}}{{OC^2}}=\\operatorname{{tg}}^2\\angle OCS$. Из треугольника $OKC$: $\\sin\\angle OCS=\\frac{{OK}}{{OC}}={tx(sp.radsimp(ok / oc))}$, '
            f'$\\operatorname{{tg}}^2\\angle OCS=\\frac{{\\sin^2}}{{1-\\sin^2}}={tx(n)}$. Ответ: $SK:KC={self.answer(p).display.strip("$")}$.')

    def figure(self, p):
        a, area, ok, oc, n = (float(x) for x in self._v(p))
        H = oc * math.sqrt(n)
        pts = quad_pyramid(p['a'], h=H)
        K = g.line_plane(pts['S'], pts['C'], g.plane_nd((0.0, 0.0, 0.0), g.sub(pts['C'], pts['S'])))
        return g.draw(pts, extra={'O': (0.0, 0.0, 0.0), 'K': K}, section_names=['B', 'K', 'D'], segments=[('O', 'K'), ('A', 'C')], azim=140)

    def sample(self, rng):
        a = rng.choice([1, 2, 3, 4, 6])
        n = rng.choice([1, 2, 3, 4, 8])
        area = sp.radsimp(sp.Integer(a) ** 2 / 2 * S(sp.Rational(n, n + 1)))
        return dict(a=a, area=str(area))


class TrapezoidPyramidPK(Solved):
    """Плоскости PAB и PCD перпендикулярны основанию и друг другу (∠A + ∠D = 90°); объём KBCP"""
    number, topic = 14, VOLUMES
    fipi = {'9B8297': dict(b=4, h=9)}

    def answer(self, p):
        return Answer.num(r(p['b'] ** 2 * p['h'], 12))

    def check(self, p):
        b, h = float(p['b']), float(p['h'])
        k = b / math.sqrt(2)                   # KB = KC
        K = (0.0, 0.0, 0.0)
        B, C = (k, 0.0, 0.0), (0.0, k, 0.0)
        A, D = (k + b, 0.0, 0.0), (0.0, k + b, 0.0)   # AB = CD = b (как в задаче ФИПИ)
        P = (0.0, 0.0, h)
        assert g.perpendicular(g.plane(P, A, B)[0], g.plane(P, C, D)[0])
        return g.volume([K, B, C, P])

    def condition(self, p):
        return ('Основанием четырёхугольной пирамиды $PABCD$ является трапеция $ABCD$, причём $\\angle BAD+\\angle ADC=90^\\circ$. '
                'Плоскости $PAB$ и $PCD$ перпендикулярны плоскости основания, $K$ — точка пересечения прямых $AB$ и $CD$.\n\n'
                'а) Докажите, что плоскости $PAB$ и $PCD$ перпендикулярны.\n\n'
                f'б) Найдите объём пирамиды $KBCP$, если $AB=BC=CD={p["b"]}$, а высота пирамиды $PABCD$ равна ${p["h"]}$.')

    def solution(self, p):
        b, h = p['b'], p['h']
        return (
            'а) Плоскости $PAB$ и $PCD$ перпендикулярны основанию и пересекаются по прямой $PK$ ($K$ — общая точка прямых $AB$ и $CD$), '
            'поэтому $PK\\perp ABC$. Значит, $KA\\perp PK$ и $KD\\perp PK$, и $\\angle AKD$ — линейный угол двугранного угла между '
            'плоскостями. В треугольнике $AKD$: $\\angle AKD=180^\\circ-(\\angle A+\\angle D)=90^\\circ$, плоскости перпендикулярны.\n\n'
            f'б) $PK$ — высота пирамиды: $PK={h}$. $BC\\parallel AD$, треугольник $KBC$ подобен $KAD$ и прямоугольный, а $AB=CD$ — трапеция '
            'равнобедренная, поэтому $KB=KC$ и $\\angle KBC=45^\\circ$. '
            f'$KB=KC=\\frac{{BC}}{{\\sqrt2}}$, $S_{{KBC}}=\\frac12 KB^2=\\frac{{BC^2}}{{4}}={tx(r(b ** 2, 4))}$.\n\n'
            f'$$V_{{KBCP}}=\\frac13 S_{{KBC}}\\cdot PK=\\frac13\\cdot {tx(r(b ** 2, 4))}\\cdot {h}={tx(r(b ** 2 * h, 12))}.$$')

    def figure(self, p):
        b, h = float(p['b']), float(p['h'])
        k = b / math.sqrt(2)
        B, C = (k, 0.0, 0.0), (0.0, k, 0.0)
        A, D = (k + b, 0.0, 0.0), (0.0, k + b, 0.0)
        P = (0.0, 0.0, h)
        return g.draw({'P': P, 'A': A, 'B': B, 'C': C, 'D': D}, extra={'K': (0.0, 0.0, 0.0)},
                      segments=[('K', 'B'), ('K', 'C'), ('K', 'P')], azim=225, elev=32)

    def sample(self, rng):
        return dict(b=rng.choice([2, 4, 6, 8]), h=rng.choice([3, 6, 9, 12]))


def _proj_area(pts2):
    """Площадь многоугольника на плоскости по формуле шнурования (sympy)"""
    s = 0
    for (x1, y1), (x2, y2) in zip(pts2, pts2[1:] + pts2[:1]):
        s += x1 * y2 - x2 * y1
    return sp.Abs(sp.nsimplify(s)) / 2


class QuadPyramidCMN(Solved):
    """M — середина SA, SN:NB = 1:2: плоскость CMN ∥ SD; площадь сечения (через площадь проекции)"""
    number, topic = 14, SECTIONS
    fipi = {'1D76E2': dict(a=6, s=6)}

    def _v(self, p):
        a, s = sp.Integer(p['a']), sp.Integer(p['s'])
        k = a / 2
        H = S(s ** 2 - a ** 2 / 2)
        A, B, C, D = sp.Matrix([-k, -k, 0]), sp.Matrix([k, -k, 0]), sp.Matrix([k, k, 0]), sp.Matrix([-k, k, 0])
        Sv = sp.Matrix([0, 0, H])
        M = (Sv + A) / 2
        N = Sv + (B - Sv) / 3
        Y = (A + D) / 2
        n = (Y - C).cross(M - C)
        cos = sp.radsimp(sp.Abs(n[2]) / sp.sqrt(n.dot(n)))
        sproj = _proj_area([(C[0], C[1]), (N[0], N[1]), (M[0], M[1]), (Y[0], Y[1])])
        return a, s, H, M, N, Y, cos, sproj, sp.radsimp(sproj / cos)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        pts = quad_pyramid(p['a'], p['s'])
        M, N = g.mid(pts['S'], pts['A']), g.ratio(pts['S'], pts['B'], 1, 2)
        pl = g.plane(pts['C'], M, N)
        assert abs(g.dot(pl[0], g.sub(pts['D'], pts['S']))) < 1e-9
        return g.polygon_area(g.section(list(pts.values()), pl))

    def condition(self, p):
        tail = (f'если все рёбра пирамиды равны ${p["a"]}$' if p['a'] == p['s'] else
                f'если сторона основания равна ${p["a"]}$, а боковое ребро равно ${p["s"]}$')
        return ('Точка $M$ — середина ребра $SA$ правильной четырёхугольной пирамиды $SABCD$ с основанием $ABCD$. Точка $N$ лежит на ребре '
                '$SB$, $SN:NB=1:2$.\n\nа) Докажите, что плоскость $CMN$ параллельна прямой $SD$.\n\n'
                f'б) Найдите площадь сечения пирамиды плоскостью $CMN$, {tail}.')

    def solution(self, p):
        a, s, H, M, N, Y, cos, sproj, ans = self._v(p)
        k = a / 2
        return (
            'а) Прямая $MN$ пересекает прямую $AB$ в точке $X$. По теореме Менелая для треугольника $SAB$: '
            '$\\frac{SM}{MA}\\cdot\\frac{AX}{XB}\\cdot\\frac{BN}{NS}=1$, $1\\cdot\\frac{AX}{XB}\\cdot 2=1$, $\\frac{AX}{XB}=\\frac12$: '
            '$X$ лежит на продолжении $BA$ за точку $A$, $XA=AB$. Плоскость $CMN$ пересекает основание по прямой $XC$; треугольники $XAY$ и $XBC$ '
            'подобны с коэффициентом $\\frac12$ ($Y=XC\\cap AD$), поэтому $AY=\\frac12 BC$: $Y$ — середина $AD$. Тогда $MY$ — средняя линия '
            'треугольника $SAD$, $MY\\parallel SD$, и плоскость $CMN$ (содержащая $MY$) параллельна $SD$.\n\n'
            'б) Сечение — четырёхугольник $CNMY$. Введём координаты: начало — центр основания $O$, оси параллельны сторонам, '
            f'$SO=\\sqrt{{SA^2-\\frac{{AB^2}}{{2}}}}={tx(H)}$: $C({tx(k)};{tx(k)};0)$, $Y({tx(-k)};0;0)$, $M\\left({tx(M[0])};{tx(M[1])};{tx(M[2])}\\right)$, '
            f'$N\\left({tx(N[0])};{tx(N[1])};{tx(N[2])}\\right)$.\n\n'
            'Площадь проекции сечения на основание (четырёхугольник $CN\'M\'Y$) по формуле площади многоугольника через координаты: '
            f'$S_{{\\text{{пр}}}}={tx(sproj)}$. Нормаль к плоскости сечения $\\vec n=\\overrightarrow{{CY}}\\times\\overrightarrow{{CM}}$, косинус угла '
            f'между плоскостью сечения и основанием $\\cos\\varphi=\\frac{{|n_z|}}{{|\\vec n|}}={tx(cos)}$.\n\n'
            f'$$S=\\frac{{S_{{\\text{{пр}}}}}}{{\\cos\\varphi}}=\\frac{{{tx(sproj)}}}{{{tx(cos)}}}={tx(ans)}.$$')

    def figure(self, p):
        pts = quad_pyramid(p['a'], p['s'])
        M, N = g.mid(pts['S'], pts['A']), g.ratio(pts['S'], pts['B'], 1, 2)
        Y = g.mid(pts['A'], pts['D'])
        return g.draw(pts, extra={'M': M, 'N': N, 'Y': Y}, section_names=['C', 'N', 'M', 'Y'], azim=140)

    def sample(self, rng):
        a = rng.choice([2, 4, 6, 8, 12])
        return dict(a=a, s=rng.choice([a, a, rng.randint(a // 2 + 2, a + 6)]))


class TetraPQMN(Solved):
    """Тетраэдр: AM:MB = CN:NB, P, Q — середины DA, DC ⇒ P, Q, M, N в одной плоскости; отношение объёмов частей"""
    number, topic = 14, VOLUMES
    fipi = {'1F7CE6': dict(p=1, q=2)}

    def _v(self, p):
        pp, q = sp.Integer(p['p']), sp.Integer(p['q'])
        mu = q / (pp + q)
        big = q / (q - pp) * mu ** 2
        small = pp / (4 * (q - pp))
        v_bd = big - small
        return mu, big, small, v_bd, 1 - v_bd

    def answer(self, p):
        *_, v_bd, v_ac = self._v(p)
        lo, hi = sorted([v_bd, v_ac])
        return Answer.ratio(lo, hi)

    def check(self, p):
        A, B, C, D = (0.0, 0.0, 0.0), (4.0, 0.3, 0.0), (1.0, 3.0, 0.0), (1.5, 1.0, 3.0)
        M = g.ratio(A, B, p['p'], p['q'])
        N = g.ratio(C, B, p['p'], p['q'])
        P, Q = g.mid(D, A), g.mid(D, C)
        pl = g.plane(P, Q, M)
        assert g.on_plane(pl, N)
        v1, v2 = g.split_volumes([A, B, C, D], pl)
        lo, hi = sorted([v1, v2])
        return lo / hi

    def condition(self, p):
        return (f'На рёбрах $AB$ и $BC$ треугольной пирамиды $ABCD$ отмечены точки $M$ и $N$, причём $AM:MB=CN:NB={p["p"]}:{p["q"]}$. '
                'Точки $P$ и $Q$ — середины рёбер $DA$ и $DC$.\n\nа) Докажите, что точки $P$, $Q$, $M$ и $N$ лежат в одной плоскости.\n\n'
                'б) Найдите отношение объёмов многогранников, на которые плоскость $PQM$ разбивает пирамиду.')

    def solution(self, p):
        mu, big, small, v_bd, v_ac = self._v(p)
        pp, q = p['p'], p['q']
        return (
            f'а) $PQ$ — средняя линия треугольника $ADC$: $PQ\\parallel AC$. $\\frac{{BM}}{{BA}}=\\frac{{BN}}{{BC}}={tx(mu)}$, поэтому $MN\\parallel AC$. '
            'Прямые $PQ$ и $MN$ параллельны, значит, лежат в одной плоскости.\n\n'
            'б) Прямая $MP$ (в плоскости $ABD$) пересекает прямую $BD$ в точке $X$. По теореме Менелая для треугольника $ABD$: '
            f'$\\frac{{AM}}{{MB}}\\cdot\\frac{{BX}}{{XD}}\\cdot\\frac{{DP}}{{PA}}=1$, $\\frac{{BX}}{{XD}}=\\frac{{{q}}}{{{pp}}}$: $X$ лежит на продолжении '
            f'$BD$ за точку $D$, $\\frac{{BX}}{{BD}}={tx(r(q, q - pp))}$, $\\frac{{XD}}{{BD}}={tx(r(pp, q - pp))}$. Прямая $NQ$ проходит через ту же точку $X$.\n\n'
            'Часть пирамиды, содержащая вершины $B$ и $D$, — это тетраэдр $XBMN$ без тетраэдра $XDPQ$. Объёмы тетраэдров с общим трёхгранным '
            'углом относятся как произведения длин рёбер; пусть $V$ — объём $ABCD$:\n\n'
            f'$$V_{{XBMN}}=\\frac{{BX}}{{BD}}\\cdot\\frac{{BM}}{{BA}}\\cdot\\frac{{BN}}{{BC}}V={tx(big)}V,\\qquad '
            f'V_{{XDPQ}}=\\frac{{XD}}{{BD}}\\cdot\\frac{{DP}}{{DA}}\\cdot\\frac{{DQ}}{{DC}}V={tx(small)}V.$$\n\n'
            f'Объём части с вершинами $B$, $D$: ${tx(v_bd)}V$, другой части: ${tx(v_ac)}V$. Отношение {self.answer(p).display}.')

    def figure(self, p):
        A, B, C, D = (0.0, 0.0, 0.0), (4.0, 0.0, 0.0), (1.5, 3.0, 0.0), (1.8, 1.2, 3.2)
        M, N = g.ratio(A, B, p['p'], p['q']), g.ratio(C, B, p['p'], p['q'])
        P, Q = g.mid(D, A), g.mid(D, C)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D}, extra={'M': M, 'N': N, 'P': P, 'Q': Q}, section_names=['M', 'N', 'Q', 'P'])

    def sample(self, rng):
        pp, q = rng.choice([(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (2, 5)])
        return dict(p=pp, q=q)


class CubeB1N(Solved):
    """Куб, M и N — середины AB и AD: B₁N ⊥ CM; расстояние от C до плоскости через N, B₁ параллельно CM"""
    number, topic = 14, DIST
    fipi = {'A47BE8': dict(t=6)}

    def answer(self, p):
        a = 2 * sp.Integer(p['t']) / 3
        return Answer.num(sp.radsimp(a / S(5)))

    def check(self, p):
        a = 2 * p['t'] / 3
        pts = box(a, a, a)
        M, N = g.mid(pts['A'], pts['B']), g.mid(pts['A'], pts['D'])
        assert g.perpendicular(g.sub(N, pts['B1']), g.sub(M, pts['C'])) and g.close(g.dist(pts['B1'], N), p['t'])
        pl = g.plane_pv(N, g.sub(pts['B1'], N), g.sub(M, pts['C']))
        return g.dist_point_plane(pts['C'], pl)

    def condition(self, p):
        return ('В кубе $ABCDA_1B_1C_1D_1$ точки $M$ и $N$ — середины рёбер $AB$ и $AD$.\n\nа) Докажите, что прямые $B_1N$ и $CM$ перпендикулярны.\n\n'
                'б) Плоскость $\\alpha$ проходит через точки $N$ и $B_1$ параллельно прямой $CM$. Найдите расстояние от точки $C$ до плоскости '
                f'$\\alpha$, если $B_1N={p["t"]}$.')

    def solution(self, p):
        t = sp.Integer(p['t'])
        a = 2 * t / 3
        return (
            'а) $BN$ — проекция $B_1N$ на основание. Прямоугольные треугольники $ABN$ и $BCM$ равны ($AB=BC$, $AN=BM$), поэтому '
            '$\\angle ABN=\\angle BCM$, и $\\angle ABN+\\angle BMC=\\angle BCM+\\angle BMC=90^\\circ$: $BN\\perp CM$. По теореме о трёх '
            'перпендикулярах $B_1N\\perp CM$.\n\n'
            f'б) Пусть ребро куба $a$. $BN^2=a^2+\\frac{{a^2}}{{4}}$, $B_1N^2=a^2+BN^2=\\frac94 a^2$, $B_1N=\\frac32 a={t}$, $a={tx(a)}$.\n\n'
            '$CM\\perp BN$ и $CM\\perp BB_1$, поэтому $CM\\perp BB_1N$. Плоскость $\\alpha$ содержит $B_1N$ и параллельна $CM$, значит, '
            '$\\alpha\\perp BB_1N$. Прямая $CM\\parallel\\alpha$, и расстояние от $C$ до $\\alpha$ равно расстоянию от точки $K=CM\\cap BN$ до '
            '$\\alpha$, то есть от $K$ до прямой $B_1N$ в плоскости $BB_1N$.\n\n'
            '$BK$ — высота прямоугольного треугольника $BCM$: $BK=\\frac{BC\\cdot BM}{CM}=\\frac{a\\cdot a/2}{a\\sqrt5/2}=\\frac{a}{\\sqrt5}$, '
            '$KN=BN-BK=\\frac{a\\sqrt5}{2}-\\frac{a}{\\sqrt5}=\\frac{3a}{2\\sqrt5}$. Расстояние от $K$ до $B_1N$:\n\n'
            f'$$d=KN\\cdot\\sin\\angle B_1NB=KN\\cdot\\frac{{BB_1}}{{B_1N}}=\\frac{{3a}}{{2\\sqrt5}}\\cdot\\frac{{a}}{{3a/2}}=\\frac{{a}}{{\\sqrt5}}'
            f'={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        a = 2 * p['t'] / 3
        pts = box(a, a, a)
        M, N = g.mid(pts['A'], pts['B']), g.mid(pts['A'], pts['D'])
        return g.draw(pts, extra={'M': M, 'N': N}, segments=[('B1', 'N'), ('C', 'M')], elev=22)

    def sample(self, rng):
        return dict(t=rng.choice([3, 6, 9, 12, 15]))


class TetraCMK(Solved):
    """Правильный тетраэдр, AM = AK: плоскость CMK делит объём; косинус угла между AC и плоскостью CMK"""
    number, topic = 14, ANGLES
    fipi = {'69A4eD': dict(a=6, m=4)}

    def _v(self, p):
        a, m = sp.Integer(p['a']), sp.Integer(p['m'])
        v = a ** 3 / (6 * S(2))
        vs = sp.radsimp(m ** 2 / a ** 2 * v)
        cm2 = a ** 2 + m ** 2 - a * m
        hc = S(cm2 - m ** 2 / 4)
        area = sp.radsimp(m * hc / 2)
        d = sp.radsimp(3 * vs / area)
        sin = sp.radsimp(d / a)
        return a, m, v, vs, cm2, hc, area, d, sin, sp.radsimp(S(1 - sin ** 2))

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        a = float(p['a'])
        A, B, C = (0.0, 0.0, 0.0), (a, 0.0, 0.0), (a / 2, a * math.sqrt(3) / 2, 0.0)
        O = g.centroid(A, B, C)
        D = (O[0], O[1], a * math.sqrt(2 / 3))
        M, K = g.lerp(A, B, p['m'] / a), g.lerp(A, D, p['m'] / a)
        pl = g.plane(C, M, K)
        v1, v2 = g.split_volumes([A, B, C, D], pl)
        assert g.close(min(v1, v2) / max(v1, v2), min(p['m'] ** 2, a * a - p['m'] ** 2) / max(p['m'] ** 2, a * a - p['m'] ** 2))
        return math.cos(g.angle_line_plane(g.sub(C, A), pl))

    def condition(self, p):
        a, m = p['a'], p['m']
        q = sp.Rational(a * a - m * m, m * m)
        return (f'В правильном тетраэдре $ABCD$ все рёбра равны ${a}$. На рёбрах $AB$ и $AD$ отмечены точки $M$ и $K$ так, что $AM=AK={m}$.\n\n'
                f'а) Докажите, что плоскость $CMK$ делит тетраэдр на два многогранника, объёмы которых относятся как ${q.p}:{q.q}$.\n\n'
                'б) Найдите косинус угла между прямой $AC$ и плоскостью $CMK$.')

    def solution(self, p):
        a, m, v, vs, cm2, hc, area, d, sin, cos = self._v(p)
        q = sp.Rational(int(a) ** 2 - int(m) ** 2, int(m) ** 2)
        return (
            f'а) Тетраэдр $ACMK$ имеет с $ABCD$ общий трёхгранный угол при вершине $A$, поэтому '
            f'$\\frac{{V_{{ACMK}}}}{{V_{{ABCD}}}}=\\frac{{AM}}{{AB}}\\cdot\\frac{{AK}}{{AD}}={tx(m ** 2 / a ** 2)}$. Объём второй части '
            f'${tx(1 - m ** 2 / a ** 2)}V$, отношение ${q.p}:{q.q}$.\n\n'
            f'б) Синус угла между $AC$ и плоскостью $CMK$ равен $\\frac{{d}}{{AC}}$, где $d$ — расстояние от $A$ до плоскости $CMK$. '
            f'$V_{{ABCD}}=\\frac{{a^3}}{{6\\sqrt2}}={tx(sp.radsimp(v))}$, $V_{{ACMK}}={tx(vs)}$.\n\n'
            f'Треугольник $AMK$ правильный, $MK={m}$. В треугольнике $ACM$: $CM^2=AC^2+AM^2-AC\\cdot AM={tx(cm2)}$, $CK=CM$. Высота '
            f'равнобедренного треугольника $CMK$: $\\sqrt{{CM^2-\\frac{{MK^2}}{{4}}}}={tx(hc)}$, $S_{{CMK}}={tx(area)}$.\n\n'
            f'$d=\\frac{{3V_{{ACMK}}}}{{S_{{CMK}}}}={tx(d)}$, $\\sin\\varphi=\\frac{{d}}{{{a}}}={tx(sin)}$, '
            f'$$\\cos\\varphi=\\sqrt{{1-\\sin^2\\varphi}}={tx(cos)}.$$')

    def figure(self, p):
        a = float(p['a'])
        A, B, C = (0.0, 0.0, 0.0), (a, 0.0, 0.0), (a / 2, a * math.sqrt(3) / 2, 0.0)
        O = g.centroid(A, B, C)
        D = (O[0], O[1], a * math.sqrt(2 / 3))
        M, K = g.lerp(A, B, p['m'] / a), g.lerp(A, D, p['m'] / a)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D}, extra={'M': M, 'K': K}, section_names=['C', 'M', 'K'])

    def sample(self, rng):
        a = rng.choice([3, 4, 6, 8, 9, 12])
        m = rng.randint(1, a - 1)
        if 2 * m * m == a * a:
            return None
        return dict(a=a, m=m)


class QuadPyramidMNL(Solved):
    """M — середина SC, плоскость через M и N ∈ BC параллельно SA: BN:NC = DL:LS; отношение объёмов частей"""
    number, topic = 14, VOLUMES
    fipi = {'DE9364': dict(p=1, q=3)}

    def _f(self, p):
        t = r(p['p'], p['p'] + p['q'])
        f = (1 + t ** 2) / 4
        return t, f

    def answer(self, p):
        t, f = self._f(p)
        lo, hi = sorted([f, 1 - f])
        return Answer.ratio(lo, hi)

    def check(self, p):
        pts = quad_pyramid(4.0, 5.0)
        M = g.mid(pts['S'], pts['C'])
        N = g.ratio(pts['B'], pts['C'], p['p'], p['q'])
        pl = g.plane_pv(M, g.sub(N, M), g.sub(pts['A'], pts['S']))
        L = g.line_plane(pts['S'], pts['D'], pl)
        assert g.close(g.dist(pts['D'], L) / g.dist(L, pts['S']), p['p'] / p['q'])
        v1, v2 = g.split_volumes(list(pts.values()), pl)
        lo, hi = sorted([v1, v2])
        return lo / hi

    def condition(self, p):
        return ('Точка $M$ — середина бокового ребра $SC$ правильной четырёхугольной пирамиды $SABCD$. Точка $N$ лежит на стороне основания $BC$. '
                'Плоскость $\\alpha$ проходит через точки $M$ и $N$ параллельно боковому ребру $SA$.\n\n'
                'а) Плоскость $\\alpha$ пересекает боковое ребро $SD$ в точке $L$. Докажите, что $BN:NC=DL:LS$.\n\n'
                f'б) Плоскость $\\alpha$ делит пирамиду на два многогранника. Найдите отношение их объёмов, если $BN:NC={p["p"]}:{p["q"]}$.')

    def solution(self, p):
        t, f = self._f(p)
        pp, q = p['p'], p['q']
        return (
            'а) Плоскость $\\alpha\\parallel SA$ пересекает плоскость $SAC$ по прямой через $M$, параллельной $SA$, — средней линии треугольника $SAC$; '
            'она проходит через центр основания $O$. Значит, $\\alpha$ пересекает основание по прямой $NO$, которая пересекает $AD$ в точке $P$, '
            'симметричной $N$ относительно $O$: $AP=CN$, $DP=BN$. Плоскость $\\alpha$ пересекает грань $SAD$ по прямой $PL\\parallel SA$, '
            'поэтому $\\frac{DL}{LS}=\\frac{DP}{PA}=\\frac{BN}{NC}$.\n\n'
            'б) Пусть $a$ — сторона основания, $h$ — высота, $V=\\frac13 a^2h$. Часть пирамиды с вершинами $C$ и $D$ — многогранник $NCDPML$. '
            'Разобьём его на пирамиды с вершиной $M$: $MNCD$, $MNDP$ (их основания составляют трапецию $NCDP$) и тетраэдр $MDPL$.\n\n'
            '$NC+DP=NC+BN=a$, поэтому $S_{NCD}+S_{NDP}=\\frac12 a\\cdot NC+\\frac12 a\\cdot DP=\\frac{a^2}{2}$, и с высотой $\\frac h2$ '
            '(точка $M$ — середина $SC$): $V_{MNCD}+V_{MNDP}=\\frac13\\cdot\\frac{a^2}{2}\\cdot\\frac h2=\\frac{a^2h}{12}=\\frac V4$.\n\n'
            f'$V_{{MDPL}}=\\frac{{DL}}{{DS}}\\cdot V_{{MDPS}}$, $V_{{MDPS}}=\\frac12 V_{{CDPS}}$ ($M$ — середина $SC$), '
            f'$V_{{CDPS}}=\\frac13\\cdot\\frac12 a\\cdot DP\\cdot h=\\frac{{DP}}{{a}}\\cdot\\frac V2$. При $\\frac{{DP}}{{a}}=\\frac{{DL}}{{DS}}={tx(t)}$: '
            f'$V_{{MDPL}}={tx(t)}\\cdot\\frac12\\cdot {tx(t)}\\cdot\\frac V2={tx(t ** 2 / 4)}V$.\n\n'
            f'Объём части: $\\frac V4+{tx(t ** 2 / 4)}V={tx(f)}V$, второй части ${tx(1 - f)}V$. Отношение {self.answer(p).display}.')

    def figure(self, p):
        pts = quad_pyramid(4.0, 5.0)
        M = g.mid(pts['S'], pts['C'])
        N = g.ratio(pts['B'], pts['C'], p['p'], p['q'])
        pl = g.plane_pv(M, g.sub(N, M), g.sub(pts['A'], pts['S']))
        L, P = g.line_plane(pts['S'], pts['D'], pl), g.line_plane(pts['A'], pts['D'], pl)
        return g.draw(pts, extra={'M': M, 'N': N, 'L': L, 'P': P}, section_names=['N', 'M', 'L', 'P'], azim=140)

    def sample(self, rng):
        pp, q = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (1, 4)])
        return dict(p=pp, q=q)


class QuadPyramidMPQ(Solved):
    """M на SD, P, Q — середины BC и AD: сечение — равнобедренная трапеция; отношение объёмов"""
    number, topic = 14, VOLUMES
    fipi = {'6F3F6D': dict(p=2, q=1)}

    def _f(self, p):
        mu = r(p['q'], p['p'] + p['q'])          # MD : SD
        f = mu * (3 - mu) / 4
        return mu, f

    def answer(self, p):
        mu, f = self._f(p)
        lo, hi = sorted([f, 1 - f])
        return Answer.ratio(lo, hi)

    def check(self, p):
        pts = quad_pyramid(4.0, 5.0)
        M = g.ratio(pts['S'], pts['D'], p['p'], p['q'])
        P, Q = g.mid(pts['B'], pts['C']), g.mid(pts['A'], pts['D'])
        pl = g.plane(M, P, Q)
        sec = g.section(list(pts.values()), pl)
        assert len(sec) == 4
        v1, v2 = g.split_volumes(list(pts.values()), pl)
        lo, hi = sorted([v1, v2])
        return lo / hi

    def condition(self, p):
        return (f'На ребре $SD$ правильной четырёхугольной пирамиды $SABCD$ с основанием $ABCD$ отмечена точка $M$, $SM:MD={p["p"]}:{p["q"]}$. '
                'Точки $P$ и $Q$ — середины рёбер $BC$ и $AD$.\n\nа) Докажите, что сечение пирамиды плоскостью $MPQ$ — равнобедренная трапеция.\n\n'
                'б) Найдите отношение объёмов многогранников, на которые плоскость $MPQ$ разбивает пирамиду.')

    def solution(self, p):
        mu, f = self._f(p)
        pp, q = p['p'], p['q']
        return (
            'а) $PQ\\parallel CD$ (средняя линия квадрата), поэтому плоскость $MPQ$ пересекает грань $SCD$ по прямой $MK\\parallel CD$, $K\\in SC$, '
            f'$SK:KC=SM:MD={pp}:{q}$. Сечение $PQMK$ — трапеция ($MK\\parallel PQ$, $MK<CD=PQ$). Симметрия пирамиды относительно плоскости, '
            'проходящей через $S$ перпендикулярно $CD$, переводит $Q$ в $P$ и $M$ в $K$, поэтому $QM=PK$ — трапеция равнобедренная.\n\n'
            'б) Пусть $a$ — сторона основания, $h$ — высота, $V=\\frac13 a^2h$. Часть с вершинами $C$ и $D$ — многогранник $QPCDMK$; разобьём его '
            'на пирамиду $MQPCD$ и тетраэдр $MPCK$.\n\n'
            f'Высота точки $M$: $\\frac{{MD}}{{SD}}h={tx(mu)}h$; $V_{{MQPCD}}=\\frac13\\cdot\\frac{{a^2}}{{2}}\\cdot {tx(mu)}h={tx(mu / 2)}V$.\n\n'
            f'$V_{{MPCK}}=\\frac{{CK}}{{CS}}\\cdot V_{{MPCS}}$, $V_{{MPCS}}=\\frac{{SM}}{{SD}}\\cdot V_{{DPCS}}$, $V_{{DPCS}}=\\frac13\\cdot\\frac{{a^2}}{{4}}h=\\frac V4$. '
            f'Значит, $V_{{MPCK}}={tx(mu)}\\cdot {tx(1 - mu)}\\cdot\\frac V4={tx(mu * (1 - mu) / 4)}V$.\n\n'
            f'Объём части: ${tx(mu / 2)}V+{tx(mu * (1 - mu) / 4)}V={tx(f)}V$, второй — ${tx(1 - f)}V$. Отношение {self.answer(p).display}.')

    def figure(self, p):
        pts = quad_pyramid(4.0, 5.0)
        M = g.ratio(pts['S'], pts['D'], p['p'], p['q'])
        K = g.ratio(pts['S'], pts['C'], p['p'], p['q'])
        P, Q = g.mid(pts['B'], pts['C']), g.mid(pts['A'], pts['D'])
        return g.draw(pts, extra={'M': M, 'K': K, 'P': P, 'Q': Q}, section_names=['Q', 'P', 'K', 'M'], azim=140)

    def sample(self, rng):
        pp, q = rng.choice([(1, 1), (1, 2), (2, 1), (1, 3), (3, 1), (3, 2)])
        return dict(p=pp, q=q)


class TetraSquare(Solved):
    """Сечение тетраэдра KLMN — квадрат ⇒ AB ⊥ CD; расстояние от B до плоскости KLM по объёму"""
    number, topic = 14, DIST
    fipi = {'A2B731': dict(p=2, q=3, t=2, vol=25)}

    def _v(self, p):
        pp, q, t, vol = (sp.Integer(p[k]) for k in ('p', 'q', 't', 'vol'))
        cd = t * (pp + q) / pp
        ab = t * (pp + q) / q
        d = 6 * vol / (ab * cd)
        return cd, ab, d, pp / (pp + q) * d

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        cd, ab, d, ans = (float(x) for x in self._v(p))
        A, B = (-ab / 2, 0.0, 0.0), (ab / 2, 0.0, 0.0)
        C, D = (0.0, -cd / 2, d), (0.0, cd / 2, d)
        assert g.close(g.volume([A, B, C, D]), p['vol'])
        K = g.ratio(A, C, p['p'], p['q'])
        L = g.ratio(A, D, p['p'], p['q'])
        N = g.ratio(B, C, p['p'], p['q'])
        Mv = g.ratio(B, D, p['p'], p['q'])
        assert g.close(g.dist(K, L), p['t']) and g.close(g.dist(K, N), p['t']) and g.perpendicular(g.sub(L, K), g.sub(N, K))
        return g.dist_point_plane(B, g.plane(K, L, Mv))

    def condition(self, p):
        return (f'На рёбрах $AC$, $AD$, $BD$ и $BC$ тетраэдра $ABCD$ отмечены точки $K$, $L$, $M$ и $N$, причём $AK:KC={p["p"]}:{p["q"]}$. '
                f'Четырёхугольник $KLMN$ — квадрат со стороной ${p["t"]}$.\n\nа) Докажите, что прямые $AB$ и $CD$ перпендикулярны.\n\n'
                f'б) Найдите расстояние от вершины $B$ до плоскости $KLM$, если объём тетраэдра равен ${p["vol"]}$.')

    def solution(self, p):
        cd, ab, d, ans = self._v(p)
        pp, q = p['p'], p['q']
        return (
            'а) $KL\\parallel MN$, прямая $MN$ лежит в плоскости $BCD$, поэтому $KL\\parallel BCD$. Плоскость $ACD$, содержащая $KL$, пересекает '
            '$BCD$ по $CD$, значит, $KL\\parallel CD$. Аналогично $KN\\parallel LM$ даёт $KN\\parallel AB$. В квадрате $KL\\perp KN$, поэтому $CD\\perp AB$.\n\n'
            f'б) $\\frac{{KL}}{{CD}}=\\frac{{AK}}{{AC}}=\\frac{{{pp}}}{{{pp + q}}}$, $CD={tx(cd)}$; $\\frac{{KN}}{{AB}}=\\frac{{CK}}{{CA}}=\\frac{{{q}}}{{{pp + q}}}$, '
            f'$AB={tx(ab)}$. Объём тетраэдра через скрещивающиеся рёбра: $V=\\frac16\\,AB\\cdot CD\\cdot\\rho\\cdot\\sin 90^\\circ$, где $\\rho$ — '
            f'расстояние между $AB$ и $CD$: $\\rho=\\frac{{6V}}{{AB\\cdot CD}}={tx(d)}$.\n\n'
            'Плоскость $KLM$ параллельна $AB$ и $CD$ и делит расстояние между ними в отношении $AK:KC$ (считая от $AB$). Точка $B$ лежит на $AB$, '
            f'поэтому $$d(B,KLM)=\\frac{{{pp}}}{{{pp + q}}}\\cdot {tx(d)}={tx(ans)}.$$')

    def figure(self, p):
        cd, ab, d, ans = (float(x) for x in self._v(p))
        A, B = (-ab / 2, 0.0, 0.0), (ab / 2, 0.0, 0.0)
        C, D = (0.0, -cd / 2, d), (0.0, cd / 2, d)
        K, L = g.ratio(A, C, p['p'], p['q']), g.ratio(A, D, p['p'], p['q'])
        N, M = g.ratio(B, C, p['p'], p['q']), g.ratio(B, D, p['p'], p['q'])
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D}, extra={'K': K, 'L': L, 'M': M, 'N': N}, section_names=['K', 'L', 'M', 'N'], azim=130)

    def sample(self, rng):
        pp, q = rng.choice([(1, 1), (1, 2), (2, 3), (1, 3), (3, 2)])
        return dict(p=pp, q=q, t=rng.randint(1, 4), vol=rng.randint(2, 40))


class TriPyramidConcurrent(Solved):
    """M, K — середины AB, SC; MK и NL пересекаются ⇒ MN, KL, SB конкурентны; BL:LC = AN:NS"""
    number, topic = 14, SECTIONS
    fipi = {'BCEB84': dict(p=3, q=1)}

    def answer(self, p):
        return Answer.ratio(p['p'], p['q'])

    def check(self, p):
        A, B, C, Sv = tri_pyramid(6, 7)
        M, K = g.mid(A, B), g.mid(Sv, C)
        N = g.ratio(A, Sv, p['p'], p['q'])
        pl = g.plane(M, K, N)
        L = g.line_plane(B, C, pl)
        return g.dist(B, L) / g.dist(L, C)

    def condition(self, p):
        return ('В правильной треугольной пирамиде $SABC$ с основанием $ABC$ точки $M$ и $K$ — середины рёбер $AB$ и $SC$, а точки $N$ и $L$ '
                f'отмечены на рёбрах $SA$ и $BC$ так, что отрезки $MK$ и $NL$ пересекаются, а $AN:NS={p["p"]}:{p["q"]}$.\n\n'
                'а) Докажите, что прямые $MN$, $KL$ и $SB$ пересекаются в одной точке.\n\nб) Найдите отношение $BL:LC$.')

    def solution(self, p):
        pp, q = p['p'], p['q']
        return (
            'а) Отрезки $MK$ и $NL$ пересекаются, поэтому точки $M$, $N$, $K$, $L$ лежат в одной плоскости $\\beta$. Плоскость $\\beta$ пересекает '
            'грани $SAB$ и $SBC$ по прямым $MN$ и $KL$, а эти грани пересекаются по прямой $SB$. Прямые $MN$ и $SB$ не параллельны '
            f'($AM:MB=1:1\\ne AN:NS={pp}:{q}$), пусть они пересекаются в точке $R$. Точка $R$ лежит в $\\beta$ и в плоскости $SBC$, то есть на их '
            'общей прямой $KL$. Значит, $MN$, $KL$ и $SB$ проходят через $R$.\n\n'
            f'б) Теорема Менелая для треугольника $SAB$ и прямой $MNR$: $\\frac{{AM}}{{MB}}\\cdot\\frac{{BR}}{{RS}}\\cdot\\frac{{SN}}{{NA}}=1$, '
            f'$\\frac{{BR}}{{RS}}=\\frac{{{pp}}}{{{q}}}$. Для треугольника $SBC$ и прямой $RKL$: $\\frac{{SR}}{{RB}}\\cdot\\frac{{BL}}{{LC}}\\cdot\\frac{{CK}}{{KS}}=1$, '
            f'откуда $\\frac{{BL}}{{LC}}=\\frac{{RB}}{{SR}}=\\frac{{{pp}}}{{{q}}}$. Ответ: ${pp}:{q}$.')

    def figure(self, p):
        A, B, C, Sv = tri_pyramid(6, 7)
        M, K = g.mid(A, B), g.mid(Sv, C)
        N = g.ratio(A, Sv, p['p'], p['q'])
        L = g.line_plane(B, C, g.plane(M, K, N))
        return g.draw({'A': A, 'B': B, 'C': C, 'S': Sv}, extra={'M': M, 'K': K, 'N': N, 'L': L}, segments=[('M', 'K'), ('N', 'L')],
                      section_names=['M', 'L', 'K', 'N'], elev=25)

    def sample(self, rng):
        pp, q = rng.choice([(3, 1), (2, 1), (3, 2), (4, 1), (5, 2), (4, 3)])
        return dict(p=pp, q=q)


class TriPyramidRMK(Solved):
    """R на продолжении SB за S: RM, RK пересекают AS, BC в N, L; BL:LC задано ⇒ AN:NS"""
    number, topic = 14, SECTIONS
    fipi = {'637C89': dict(p=3, q=1)}

    def answer(self, p):
        return Answer.ratio(p['p'], p['q'])

    def check(self, p):
        A, B, C, Sv = tri_pyramid(6, 7)
        M, K = g.mid(A, B), g.mid(Sv, C)
        L = g.ratio(B, C, p['p'], p['q'])
        # R = KL ∩ SB (в плоскости SBC), N = RM ∩ AS
        pl = g.plane(M, K, L)
        R = g.line_plane(Sv, B, pl)
        assert g.dist(R, B) > g.dist(Sv, B)            # за точкой S
        N = g.line_plane(A, Sv, pl)
        assert g.dist_point_line(N, R, M) < 1e-9
        return g.dist(A, N) / g.dist(N, Sv)

    def condition(self, p):
        return ('В правильной треугольной пирамиде $SABC$ с основанием $ABC$ точки $M$ и $K$ — середины рёбер $AB$ и $SC$. На продолжении ребра '
                '$SB$ за точку $S$ отмечена точка $R$. Прямые $RM$ и $RK$ пересекают рёбра $AS$ и $BC$ в точках $N$ и $L$, причём '
                f'$BL:LC={p["p"]}:{p["q"]}$.\n\nа) Докажите, что отрезки $MK$ и $NL$ пересекаются.\n\nб) Найдите отношение $AN:NS$.')

    def solution(self, p):
        pp, q = p['p'], p['q']
        return (
            'а) Точки $N$ и $L$ лежат на прямых $RM$ и $RK$, поэтому $M$, $N$, $K$, $L$ лежат в плоскости $RMK$. Эта плоскость пересекает '
            'грани тетраэдра по отрезкам $MN$ (грань $SAB$), $NK$ ($SAC$), $KL$ ($SBC$), $LM$ ($ABC$), так что $MNKL$ — сечение тетраэдра, '
            'выпуклый четырёхугольник. Его диагонали $MK$ и $NL$ пересекаются.\n\n'
            f'б) Теорема Менелая для треугольника $SBC$ и прямой $RKL$: $\\frac{{SR}}{{RB}}\\cdot\\frac{{BL}}{{LC}}\\cdot\\frac{{CK}}{{KS}}=1$, то есть '
            f'$\\frac{{SR}}{{RB}}\\cdot\\frac{{{pp}}}{{{q}}}=1$, $\\frac{{BR}}{{RS}}=\\frac{{{pp}}}{{{q}}}$. Для треугольника $SAB$ и прямой $RNM$: '
            f'$\\frac{{SN}}{{NA}}\\cdot\\frac{{AM}}{{MB}}\\cdot\\frac{{BR}}{{RS}}=1$, $\\frac{{SN}}{{NA}}=\\frac{{{q}}}{{{pp}}}$. Ответ: $AN:NS={pp}:{q}$.')

    def figure(self, p):
        A, B, C, Sv = tri_pyramid(6, 7)
        M, K = g.mid(A, B), g.mid(Sv, C)
        L = g.ratio(B, C, p['p'], p['q'])
        pl = g.plane(M, K, L)
        N = g.line_plane(A, Sv, pl)
        return g.draw({'A': A, 'B': B, 'C': C, 'S': Sv}, extra={'M': M, 'K': K, 'N': N, 'L': L}, segments=[('M', 'K'), ('N', 'L')],
                      section_names=['M', 'L', 'K', 'N'], elev=25)

    def sample(self, rng):
        pp, q = rng.choice([(3, 1), (2, 1), (3, 2), (4, 1), (5, 2), (4, 3)])
        return dict(p=pp, q=q)


TEMPLATES = [c() for c in Solved.__subclasses__() if c.__module__ == __name__]
EXTRA = []
