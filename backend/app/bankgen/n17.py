"""
№ 17. Планиметрическая задача (вторая часть): доказательство и вычисление.

Каждый класс — семейство заданий ФИПИ с одной формулировкой. Ответ пишется формулой в решении,
а check получает его заново из координат (app.bankgen.geo2).
"""
import math
import re

import sympy as sp

from app.bankgen import geo2 as g
from app.bankgen.part2 import S, Answer, Solved, r, simp, tx

TRI, CIRC, QUAD = 'Треугольники', 'Окружности', 'Четырёхугольники'


def deg(x) -> sp.Expr:
    return sp.rad(x)


def sin(x):
    return sp.sin(sp.rad(x))


def cos(x):
    return sp.cos(sp.rad(x))


def f(x) -> float:
    return float(sp.sympify(x))


class CircleThroughBC(Solved):
    """Окружность через B и C пересекает AB, AC в C₁, B₁: подобие, сторона и радиус"""
    number, topic = 17, CIRC
    fipi = {'AA7FF7': dict(A=30, given='B1C1', v='5', k=5), '2EBDBF': dict(A=45, given='B1C1', v='6', k=8),
            '3CDB1B': dict(A=135, given='B1C1', v='10', k=7), '829956': dict(A=45, given='B1C1', v='6', k=8),
            '8F66A4': dict(A=150, given='BC', v='5*sqrt(5)', k=4), '2B52E7': dict(A=120, given='BC', v='10*sqrt(7)', k=3)}

    def _v(self, p):
        lam = S(p['k'] + 1)
        v = sp.sympify(p['v'])
        b1c1 = v if p['given'] == 'B1C1' else sp.radsimp(v / lam)
        bc = sp.radsimp(lam * b1c1)
        A = p['A']
        R = simp(b1c1 * S(sp.nsimplify(1 + lam ** 2 - 2 * lam * cos(A))) / (2 * sin(A)))
        return lam, b1c1, bc, R

    def answer(self, p):
        lam, b1c1, bc, R = self._v(p)
        other = f'BC={tx(bc)}' if p['given'] == 'B1C1' else f'B_1C_1={tx(b1c1)}'
        return Answer(f'${other}$, $R={tx(R)}$', sp.N(R, 30))

    def check(self, p):
        lam, b1c1, bc, R = (float(x) for x in self._v(p))
        A = p['A']
        x = bc / (2 * math.sin(math.radians(A / 2)))       # равнобедренный треугольник с AB = AC = x
        Av, Bv = (0.0, 0.0), g.polar(x, 0)
        Cv = g.polar(x, A)
        B1 = g.lerp(Av, Cv, 1 / lam)
        C1 = g.lerp(Av, Bv, 1 / lam)
        assert g.concyclic(Bv, Cv, B1, C1) and g.close(g.dist(B1, C1), b1c1)
        assert g.close(g.area(Av, Bv, Cv) - g.area(Av, B1, C1), p['k'] * g.area(Av, B1, C1))
        return g.circumradius(Bv, Cv, B1)

    def condition(self, p):
        k = p['k']
        times = {1: 'равна площади', 2: 'в два раза меньше площади', 3: 'в три раза меньше площади', 4: 'в четыре раза меньше площади',
                 5: 'в пять раз меньше площади', 7: 'в семь раз меньше площади', 8: 'в восемь раз меньше площади',
                 9: 'в девять раз меньше площади'}[k]
        given = f'$B_1C_1={tx(sp.sympify(p["v"]))}$' if p['given'] == 'B1C1' else f'$BC={tx(sp.sympify(p["v"]))}$'
        ask = 'длину стороны $BC$' if p['given'] == 'B1C1' else 'длину отрезка $B_1C_1$'
        return ('Окружность проходит через вершины $B$ и $C$ треугольника $ABC$ и пересекает стороны $AB$ и $AC$ в точках $C_1$ и $B_1$ '
                'соответственно.\n\nа) Докажите, что треугольник $ABC$ подобен треугольнику $AB_1C_1$.\n\n'
                f'б) Найдите {ask} и радиус окружности, если $\\angle A={p["A"]}^\\circ$, {given}, а площадь треугольника $AB_1C_1$ '
                f'{times} четырёхугольника $BCB_1C_1$.')

    def solution(self, p):
        lam, b1c1, bc, R = self._v(p)
        A, k = p['A'], p['k']
        under = sp.nsimplify(1 + lam ** 2 - 2 * lam * cos(A))
        return (
            'а) Четырёхугольник $BCB_1C_1$ вписан в окружность, поэтому $\\angle CB_1C_1+\\angle C_1BC=180^\\circ$, откуда '
            '$\\angle AB_1C_1=180^\\circ-\\angle CB_1C_1=\\angle ABC$. Угол $A$ у треугольников общий, значит, $\\triangle AB_1C_1\\sim\\triangle ABC$.\n\n'
            f'б) $S_{{ABC}}=S_{{AB_1C_1}}+S_{{BCB_1C_1}}={k + 1}S_{{AB_1C_1}}$, поэтому коэффициент подобия $\\lambda=\\frac{{BC}}{{B_1C_1}}=\\sqrt{{{k + 1}}}'
            f'={tx(lam)}$: $B_1C_1={tx(b1c1)}$, $BC={tx(bc)}$.\n\n'
            'Пусть $x=\\angle BB_1C$ и $y=\\angle B_1BC_1$ — вписанные углы, опирающиеся на хорды $BC$ и $B_1C_1$. Угол $BB_1C$ — внешний '
            'угол треугольника $ABB_1$: $x=\\angle A+y$. По теореме синусов $BC=2R\\sin x$, $B_1C_1=2R\\sin y$, откуда '
            '$\\sin(A+y)=\\lambda\\sin y$, то есть $\\sin A\\cos y=(\\lambda-\\cos A)\\sin y$ и $\\operatorname{ctg}y=\\frac{\\lambda-\\cos A}{\\sin A}$.\n\n'
            '$$R=\\frac{B_1C_1}{2\\sin y}=\\frac{B_1C_1}{2}\\sqrt{1+\\operatorname{ctg}^2y}=\\frac{B_1C_1\\sqrt{1+\\lambda^2-2\\lambda\\cos A}}{2\\sin A}'
            f'=\\frac{{{tx(b1c1)}\\sqrt{{{tx(under)}}}}}{{{tx(2 * sin(A))}}}={tx(R)}.$$')

    def figure(self, p):
        lam, b1c1, bc, R = (float(x) for x in self._v(p))
        A = p['A']
        x = bc / (2 * math.sin(math.radians(A / 2)))
        Av, Bv = (0.0, 0.0), g.polar(x * 0.95, 0)      # неравнобедренный для наглядности
        Cv = g.polar(x * 1.05, A)
        AB, AC = g.dist(Av, Bv), g.dist(Av, Cv)
        B1 = g.lerp(Av, Cv, (AB / lam) / AC)            # AB₁ = AB/λ, AC₁ = AC/λ
        C1 = g.lerp(Av, Bv, (AC / lam) / AB)
        O = g.circumcenter(Bv, Cv, B1)
        pts = {'A': Av, 'B': Bv, 'C': Cv, 'B1': B1, 'C1': C1}
        return g.draw(pts, polygons=[['A', 'B', 'C']], segments=[('B1', 'C1')], circles=[(O, g.dist(O, Bv))], dots=['B1', 'C1'])

    def sample(self, rng):
        A = rng.choice([30, 45, 60, 120, 135, 150])
        k = rng.choice([1, 2, 3, 4, 5, 7, 8])
        if rng.random() < 0.5:
            return dict(A=A, given='B1C1', v=str(rng.randint(2, 12)), k=k)
        return dict(A=A, given='BC', v=str(rng.randint(2, 10) * S(k + 1)), k=k)


class TrapezoidKite(Solved):
    """Равнобедренная трапеция с перпендикулярными диагоналями: ABCP — дельтоид, радиус вписанной окружности"""
    number, topic = 17, QUAD
    fipi = {'B45F0C': dict(bc=7, ad=23), 'D57CB9': dict(bc=7, ad=17)}

    def _v(self, p):
        bc, ad = sp.Integer(p['bc']), sp.Integer(p['ad'])
        h = (ad + bc) / 2
        nd = (ad - bc) / 2
        ab = S(h ** 2 + nd ** 2)
        return bc, ad, h, nd, ab, sp.radsimp(bc * h / (ab + bc))

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def _pts(self, p):
        bc, ad = float(p['bc']), float(p['ad'])
        h = (ad + bc) / 2
        A, D, B, C = (-ad / 2, 0.0), (ad / 2, 0.0), (-bc / 2, h), (bc / 2, h)
        M = g.foot(A, C, D)
        N = g.foot(C, A, D)
        P = g.intersect(A, M, C, N)
        return A, B, C, D, M, N, P

    def check(self, p):
        A, B, C, D, M, N, P = self._pts(p)
        assert g.perpendicular(g.sub(C, A), g.sub(D, B))
        ab, bc_, cp, pa = g.dist(A, B), g.dist(B, C), g.dist(C, P), g.dist(P, A)
        assert g.close(ab + cp, bc_ + pa)
        # радиус вписанной: центр на AC, расстояние до BC и до CP одинаково
        S_ = g.area(A, B, C, P)
        return S_ / ((ab + bc_ + cp + pa) / 2)

    def condition(self, p):
        return ('Диагонали равнобедренной трапеции $ABCD$ с основаниями $BC$ и $AD$ перпендикулярны. Окружность с диаметром $AD$ '
                'пересекает боковую сторону $CD$ в точке $M$, а окружность с диаметром $CD$ пересекает основание $AD$ в точке $N$. '
                'Отрезки $AM$ и $CN$ пересекаются в точке $P$.\n\nа) Докажите, что в четырёхугольник $ABCP$ можно вписать окружность.\n\n'
                f'б) Найдите радиус этой окружности, если $BC={p["bc"]}$, $AD={p["ad"]}$.')

    def solution(self, p):
        bc, ad, h, nd, ab, rr = self._v(p)
        return (
            'а) $M$ лежит на окружности с диаметром $AD$, поэтому $AM\\perp CD$; аналогично $CN\\perp AD$: $P$ — точка пересечения высот '
            'треугольника $ACD$. В равнобедренной трапеции с перпендикулярными диагоналями каждая диагональ образует с основаниями угол '
            '$45^\\circ$, поэтому треугольник $ANC$ прямоугольный равнобедренный: $AN=CN$.\n\n'
            'Прямоугольные треугольники $ANP$ и $CND$ равны: $AN=CN$, $\\angle NAP=\\angle NCD$ (оба дополняют $\\angle D$ до $90^\\circ$). '
            'Значит, $AP=CD=AB$ и $PN=ND$. Тогда $CP=CN-PN=AN-ND=\\frac{AD+BC}{2}-\\frac{AD-BC}{2}=BC$. Четырёхугольник $ABCP$ — '
            'дельтоид ($AB=AP$, $CB=CP$), и $AB+CP=BC+AP$: в него можно вписать окружность.\n\n'
            f'б) Высота трапеции $CN=AN=\\frac{{AD+BC}}{{2}}={tx(h)}$, $ND=\\frac{{AD-BC}}{{2}}={tx(nd)}$, '
            f'$AB=CD=\\sqrt{{CN^2+ND^2}}={tx(ab)}$. Дельтоид симметричен относительно $AC$, его площадь '
            f'$S=2S_{{ABC}}=BC\\cdot CN={tx(bc * h)}$, полупериметр $AB+BC={tx(ab + bc)}$.\n\n'
            f'$$r=\\frac{{S}}{{p}}=\\frac{{{tx(bc * h)}}}{{{tx(ab + bc)}}}={tx(rr)}.$$')

    def figure(self, p):
        A, B, C, D, M, N, P = self._pts(p)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'M': M, 'N': N, 'P': P}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('A', 'M'), ('C', 'N'), ('A', 'C'), ('B', 'D'), ('C', 'P')], dashed=[('B', 'P')], dots=['M', 'N', 'P'])

    def sample(self, rng):
        for _ in range(50):
            bc = rng.randint(1, 12)
            ad = rng.randint(bc + 2, bc + 30)
            h, nd = r(ad + bc, 2), r(ad - bc, 2)
            ab2 = h ** 2 + nd ** 2
            if S(ab2).is_Rational:
                return dict(bc=bc, ad=ad)
        return None


class TrapezoidBDIsosceles(Solved):
    """Диагональ BD делит трапецию на равнобедренные треугольники (основания AD и CD): AC — биссектриса, найти CD"""
    number, topic = 17, QUAD
    fipi = {'5CBC00': dict(ac='12', bd='13/2'), '00E23C': dict(ac='15', bd='17/2')}

    def _v(self, p):
        ac, b = sp.sympify(p['ac']), sp.sympify(p['bd'])
        c = ac / (2 * b)                              # cos θ, θ = ∠CAD
        c2 = 2 * c ** 2 - 1                           # cos 2θ
        ad = 2 * b * c2
        cd = sp.radsimp(S(ac ** 2 + ad ** 2 - 2 * ac * ad * c))
        return ac, b, c, c2, ad, cd

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def _pts(self, p):
        ac, b, c, c2, ad, cd = (float(x) for x in self._v(p))
        th2 = math.acos(c2)
        A, D = (0.0, 0.0), (ad, 0.0)
        B = (b * math.cos(th2), b * math.sin(th2))
        C = (B[0] + b, B[1])
        return A, B, C, D

    def check(self, p):
        A, B, C, D = self._pts(p)
        assert g.close(g.dist(B, D), f(p['bd'])) and g.close(g.dist(A, C), f(p['ac'])) and g.close(g.dist(A, B), g.dist(B, D))
        assert g.close(g.angle(B, A, C), g.angle(C, A, D))
        return g.dist(C, D)

    def condition(self, p):
        return ('Дана трапеция $ABCD$ с основаниями $AD$ и $BC$. Диагональ $BD$ разбивает её на два равнобедренных треугольника с основаниями '
                '$AD$ и $CD$.\n\nа) Докажите, что луч $AC$ — биссектриса угла $BAD$.\n\n'
                f'б) Найдите $CD$, если диагонали трапеции $AC={tx(sp.sympify(p["ac"]))}$ и $BD={tx(sp.sympify(p["bd"]))}$.')

    def solution(self, p):
        ac, b, c, c2, ad, cd = self._v(p)
        return (
            'а) Треугольник $ABD$ равнобедренный с основанием $AD$: $AB=BD$; треугольник $BCD$ — с основанием $CD$: $BC=BD$. Значит, $AB=BC$, '
            'и в треугольнике $ABC$ $\\angle BAC=\\angle BCA$. Но $\\angle BCA=\\angle CAD$ (накрест лежащие при $BC\\parallel AD$), поэтому '
            '$\\angle BAC=\\angle CAD$: $AC$ — биссектриса угла $BAD$.\n\n'
            f'б) $AB=BC=BD={tx(b)}$. Пусть $\\theta=\\angle CAD=\\angle BAC$. В равнобедренном треугольнике $ABC$: '
            f'$\\cos\\theta=\\frac{{AC/2}}{{AB}}={tx(c)}$. В равнобедренном треугольнике $ABD$ с углом $2\\theta$ при основании: '
            f'$AD=2AB\\cos 2\\theta$, $\\cos2\\theta=2\\cos^2\\theta-1={tx(c2)}$, $AD={tx(ad)}$.\n\n'
            f'По теореме косинусов в треугольнике $ACD$: $$CD^2=AC^2+AD^2-2\\,AC\\cdot AD\\cos\\theta={tx(ac ** 2)}+{tx(ad ** 2)}-{tx(2 * ac * ad * c)}'
            f'={tx(cd ** 2)},\\quad CD={tx(cd)}.$$')

    def figure(self, p):
        A, B, C, D = self._pts(p)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D}, polygons=[['A', 'B', 'C', 'D']], segments=[('A', 'C'), ('B', 'D')])

    def sample(self, rng):
        a, b, c = rng.choice([(5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41), (12, 35, 37)])
        # AC = 2·12k, BD = 13k: cos θ = 12/13
        k = rng.choice([sp.Rational(1, 2), 1, 2])
        ac, bd = 2 * b * k, c * k
        if (2 * (sp.Rational(b, c)) ** 2 - 1) <= 0:
            return None
        return dict(ac=str(ac), bd=str(bd))


class QuadrilateralPQW(Solved):
    """P, Q, W делят стороны четырёхугольника в одном отношении: треугольник PQW прямоугольный, площадь ABCD"""
    number, topic = 17, QUAD
    fipi = {'56C211': dict(m=3, n=4, pq=16, qw=12), 'A96557': dict(m=1, n=4, pq=16, qw=12)}

    def _v(self, p):
        m, n, pq, qw = (sp.Integer(p[k]) for k in ('m', 'n', 'pq', 'qw'))
        R = S(pq ** 2 + qw ** 2) / 2
        ac = pq * (m + n) / n
        bd = qw * (m + n) / m
        return m, n, pq, qw, R, ac, bd, ac * bd / 2

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        m, n, pq, qw, R, ac, bd, s = (float(x) for x in self._v(p))
        O = (0.0, 0.0)
        A, C = (-0.45 * ac, 0.0), (0.55 * ac, 0.0)
        B, D = (0.0, -0.4 * bd), (0.0, 0.6 * bd)
        P = g.ratio(A, B, m, n)
        Q = g.ratio(C, B, m, n)
        W = g.ratio(C, D, m, n)
        assert g.close(g.dist(P, Q), pq) and g.close(g.dist(Q, W), qw) and g.close(g.circumradius(P, Q, W), R)
        assert g.angle(P, W, Q) < 90
        return g.area(A, B, C, D)

    def condition(self, p):
        m, n = p['m'], p['n']
        R = self._v(p)[4]
        return (f'Точки $P$, $Q$, $W$ делят стороны выпуклого четырёхугольника $ABCD$ в отношении $AP:PB=CQ:QB=CW:WD={m}:{n}$. Радиус '
                f'окружности, описанной около треугольника $PQW$, равен ${tx(R)}$, $PQ={p["pq"]}$, $QW={p["qw"]}$, угол $PWQ$ — острый.\n\n'
                'а) Докажите, что треугольник $PQW$ — прямоугольный.\n\nб) Найдите площадь четырёхугольника $ABCD$.')

    def solution(self, p):
        m, n, pq, qw, R, ac, bd, s = self._v(p)
        sinw = pq / (2 * R)
        return (
            f'а) По теореме синусов $\\sin\\angle PWQ=\\frac{{PQ}}{{2R}}={tx(sinw)}$, угол острый, $\\cos\\angle PWQ={tx(S(1 - sinw ** 2))}$. '
            f'По теореме косинусов $PQ^2=QW^2+PW^2-2\\,QW\\cdot PW\\cos\\angle PWQ$: ${pq ** 2}={qw ** 2}+PW^2-{tx(2 * qw * S(1 - sinw ** 2))}\\,PW$. '
            f'Положительный корень $PW={tx(2 * R)}=2R$: $PW$ — диаметр описанной окружности, и $\\angle PQW=90^\\circ$.\n\n'
            f'б) $AP:PB=CQ:QB$, поэтому $PQ\\parallel AC$ и $PQ=AC\\cdot\\frac{{BQ}}{{BC}}=\\frac{{{n}}}{{{m + n}}}AC$, откуда $AC={tx(ac)}$. '
            f'$CQ:QB=CW:WD$, поэтому $QW\\parallel BD$ и $QW=\\frac{{{m}}}{{{m + n}}}BD$, $BD={tx(bd)}$. Так как $PQ\\perp QW$, диагонали '
            'четырёхугольника перпендикулярны, и\n\n'
            f'$$S_{{ABCD}}=\\frac12\\,AC\\cdot BD=\\frac12\\cdot {tx(ac)}\\cdot {tx(bd)}={tx(s)}.$$')

    def figure(self, p):
        m, n, pq, qw, R, ac, bd, s = (float(x) for x in self._v(p))
        A, C = (-0.45 * ac, 0.0), (0.55 * ac, 0.0)
        B, D = (0.0, -0.4 * bd), (0.0, 0.6 * bd)
        P, Q, W = g.ratio(A, B, m, n), g.ratio(C, B, m, n), g.ratio(C, D, m, n)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'P': P, 'Q': Q, 'W': W}, polygons=[['A', 'B', 'C', 'D'], ['P', 'Q', 'W']],
                      dashed=[('A', 'C'), ('B', 'D')], dots=['P', 'Q', 'W'])

    def sample(self, rng):
        a, b, c = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15), (8, 15, 17), (12, 16, 20)])
        if rng.random() < 0.5:
            a, b = b, a
        m, n = rng.choice([(1, 2), (2, 1), (1, 3), (3, 4), (2, 3), (1, 4)])
        if c % 2:
            a, b, c = 2 * a, 2 * b, 2 * c
        return dict(m=m, n=n, pq=a, qw=b)


class RightTriangleMK(Solved):
    """Прямая через середину гипотенузы ⊥ CM делит катет AC в отношении 1:2 ⇒ ∠A = 30°; найти KQ"""
    number, topic = 17, TRI
    fipi = {'5E7BDE': dict(b='sqrt(21)')}

    def answer(self, p):
        b = sp.sympify(p['b'])
        return Answer.num(sp.radsimp(2 * b * S(21) / 3))

    def check(self, p):
        b = f(p['b'])
        C, A, B = (0.0, 0.0), (b * math.sqrt(3), 0.0), (0.0, b)
        M = g.mid(A, B)
        # K на AC: KM ⊥ CM
        K = g.intersect(M, g.add(M, (M[1], -M[0])), A, C)
        assert g.close(g.dist(A, K) / g.dist(K, C), 0.5)
        P = g.intersect(M, K, B, C)
        Q = g.intersect(A, P, B, K)
        return g.dist(K, Q)

    def condition(self, p):
        return ('Прямая, проходящая через середину $M$ гипотенузы $AB$ прямоугольного треугольника $ABC$, перпендикулярна $CM$ и пересекает '
                'катет $AC$ в точке $K$. При этом $AK:KC=1:2$.\n\nа) Докажите, что $\\angle BAC=30^\\circ$.\n\n'
                f'б) Пусть прямые $MK$ и $BC$ пересекаются в точке $P$, а прямые $AP$ и $BK$ — в точке $Q$. Найдите $KQ$, если $BC={tx(sp.sympify(p["b"]))}$.')

    def solution(self, p):
        b = sp.sympify(p['b'])
        return (
            'а) $CM$ — медиана к гипотенузе: $CM=AM$, поэтому $\\angle MCA=\\angle A=\\alpha$. В прямоугольном треугольнике $CMK$ '
            '($\\angle M=90^\\circ$): $CK=\\frac{CM}{\\cos\\alpha}$. Кроме того, $AC=AB\\cos\\alpha=2CM\\cos\\alpha$ и $CK=\\frac23 AC$:\n\n'
            '$$\\frac{CM}{\\cos\\alpha}=\\frac43 CM\\cos\\alpha\\ \\Rightarrow\\ \\cos^2\\alpha=\\frac34,\\quad\\alpha=30^\\circ.$$\n\n'
            f'б) Введём координаты: $C(0;0)$, катет $CA$ по оси $Ox$, $CB$ по оси $Oy$; $BC=b={tx(b)}$, $AC=b\\sqrt3$. Тогда $A(b\\sqrt3;0)$, '
            '$B(0;b)$, $M\\left(\\frac{b\\sqrt3}{2};\\frac b2\\right)$, $K\\left(\\frac{2b\\sqrt3}{3};0\\right)$. Прямая $KM$ пересекает ось $Oy$ в точке '
            '$P(0;2b)$. Прямая $AP$: $\\frac{x}{b\\sqrt3}+\\frac{y}{2b}=1$, прямая $BK$: $\\frac{3x}{2b\\sqrt3}+\\frac yb=1$; решая систему, '
            'получаем $Q(2b\\sqrt3;-2b)$.\n\n'
            f'$$KQ=\\sqrt{{\\left(2b\\sqrt3-\\frac{{2b\\sqrt3}}{{3}}\\right)^2+4b^2}}=\\sqrt{{\\frac{{16b^2}}{{3}}+4b^2}}=\\frac{{2b\\sqrt{{21}}}}{{3}}'
            f'={tx(sp.radsimp(2 * b * S(21) / 3))}.$$')

    def figure(self, p):
        b = 1.0
        C, A, B = (0.0, 0.0), (b * math.sqrt(3), 0.0), (0.0, b)
        M = g.mid(A, B)
        K = (2 * math.sqrt(3) / 3, 0.0)
        P = (0.0, 2.0)
        Q = g.intersect(A, P, B, K)
        return g.draw({'A': A, 'B': B, 'C': C, 'M': M, 'K': K, 'P': P, 'Q': Q}, polygons=[['A', 'B', 'C']],
                      segments=[('C', 'M'), ('P', 'K'), ('A', 'P'), ('B', 'Q'), ('B', 'P'), ('A', 'Q')], dots=['M', 'K', 'P', 'Q'])

    def sample(self, rng):
        return dict(b=rng.choice(['sqrt(21)', '2*sqrt(21)', '3', 'sqrt(3)', '2*sqrt(7)', '6', 'sqrt(7)']))


class RectangleBM(Solved):
    """BM ⊥ AC, MB = MD ⇒ ∠ABM = ∠DBC = 30°; расстояние от центра до CM"""
    number, topic = 17, QUAD
    fipi = {'FAAE63': dict(bc=9)}

    def answer(self, p):
        return Answer.num(sp.radsimp(sp.Integer(p['bc']) * S(21) / 42))

    def check(self, p):
        b = float(p['bc'])
        a = b / math.sqrt(3)
        A, B, C, D = (0.0, 0.0), (0.0, a), (b, a), (b, 0.0)
        M = g.intersect(B, g.add(B, (C[1] - A[1], -(C[0] - A[0]))), A, D)     # прямая через B ⊥ AC
        assert g.close(g.dist(M, B), g.dist(M, D)) and g.perpendicular(g.sub(M, B), g.sub(C, A))
        O = g.mid(A, C)
        return g.dist_line(O, C, M)

    def condition(self, p):
        return ('Прямая, проходящая через вершину $B$ прямоугольника $ABCD$ перпендикулярно диагонали $AC$, пересекает сторону $AD$ в точке $M$, '
                'равноудалённой от вершин $B$ и $D$.\n\nа) Докажите, что $\\angle ABM=\\angle DBC=30^\\circ$.\n\n'
                f'б) Найдите расстояние от центра прямоугольника до прямой $CM$, если $BC={p["bc"]}$.')

    def solution(self, p):
        b = sp.Integer(p['bc'])
        a = b / S(3)
        return (
            'а) $BM\\perp AC$, поэтому $\\angle ABM=90^\\circ-\\angle BAC=\\angle ACB$. Диагонали прямоугольника равны и делятся пополам, '
            '$OB=OC$, поэтому $\\angle ACB=\\angle DBC$. Из $MB=MD$: $\\angle MBD=\\angle MDB=\\angle DBC$ (накрест лежащие). Итак, '
            '$\\angle ABM=\\angle MBD=\\angle DBC$, а в сумме они дают $90^\\circ$: каждый равен $30^\\circ$.\n\n'
            f'б) $AB=BC\\operatorname{{tg}}30^\\circ={tx(a)}$. Введём координаты: $A(0;0)$, $D({b};0)$, $B(0;{tx(a)})$, $C({b};{tx(a)})$. '
            f'$M(x;0)$ с $\\overrightarrow{{BM}}\\perp\\overrightarrow{{AC}}$: ${b}x-{tx(a ** 2)}=0$, $x={tx(a ** 2 / b)}$. Центр '
            f'$O\\left({tx(b / 2)};{tx(a / 2)}\\right)$. Прямая $CM$ имеет направляющий вектор $\\left({tx(b - a ** 2 / b)};{tx(a)}\\right)$, '
            'расстояние от $O$ до неё — модуль векторного произведения $\\overrightarrow{MO}$ и направляющего вектора, делённый на длину '
            f'направляющего вектора:\n\n$$d=\\frac{{{tx(b)}\\sqrt{{21}}}}{{42}}={tx(sp.radsimp(b * S(21) / 42))}.$$')

    def figure(self, p):
        b = 3.0
        a = b / 1.2      # на чертеже прямоугольник менее вытянут (не b/√3): иначе точки O и H сливаются
        A, B, C, D = (0.0, 0.0), (0.0, a), (b, a), (b, 0.0)
        M = (a * a / b, 0.0)
        O = g.mid(A, C)
        H = g.foot(O, C, M)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'M': M, 'O': O, 'H': H}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('A', 'C'), ('B', 'D'), ('B', 'M'), ('C', 'M')], dashed=[('O', 'H')], dots=['M', 'O', 'H'])

    def sample(self, rng):
        return dict(bc=rng.choice([3, 6, 12, 14, 21, 42]))


def _par_vals(p):
    """Отношения в семействе «ADA₁B₁ — параллелограмм»: BA₁ : BC = α"""
    m, n = p['m'], p['n']
    al = r(m, m + n)
    be = al / (1 + al)                    # AB₁ : AC
    ga = (1 - al) / (1 - al + be)         # AC₁ : AB
    return al, be, ga


class TriangleParallelogram(Solved):
    """ADA₁B₁ — параллелограмм; при AD ⊥ BC найти CD или радиус описанной окружности"""
    number, topic = 17, TRI
    fipi = {'AC2684': dict(m=2, n=3, ac=63, bc=25, ask='CD'), '4F4F44': dict(m=1, n=2, ac=16, bc=15, ask='R')}

    def _v(self, p):
        al, be, ga = _par_vals(p)
        a, b = sp.Integer(p['bc']), sp.Integer(p['ac'])
        cosC = (1 - al) * a / ((1 - be) * b)
        sinC = S(1 - cosC ** 2)
        C = sp.Matrix([0, 0])
        B = sp.Matrix([a, 0])
        A = sp.Matrix([b * cosC, b * sinC])
        D = A + (1 - al) * (B - A) + (al - be) * (C - A)
        cd = sp.radsimp(S(sp.nsimplify(D.dot(D))))
        ab = S(a ** 2 + b ** 2 - 2 * a * b * cosC)
        R = sp.radsimp(ab / (2 * sinC))
        return al, be, ga, cosC, sinC, cd, ab, R

    def answer(self, p):
        v = self._v(p)
        return Answer.num(v[5] if p['ask'] == 'CD' else v[7])

    def check(self, p):
        al, be, ga = (float(x) for x in _par_vals(p))
        a, b = float(p['bc']), float(p['ac'])
        cosC = float(self._v(p)[3])
        C, B = (0.0, 0.0), (a, 0.0)
        A = (b * cosC, b * math.sqrt(1 - cosC ** 2))
        B1 = g.lerp(A, C, be)
        C1 = g.lerp(A, B, ga)
        A1 = g.lerp(B, C, al)
        D = g.intersect(B, B1, C, C1)
        assert g.close(g.dist(A, D), g.dist(B1, A1)) and g.parallel(g.sub(D, A), g.sub(A1, B1))
        assert g.perpendicular(g.sub(D, A), g.sub(C, B))
        return g.dist(C, D) if p['ask'] == 'CD' else g.circumradius(A, B, C)

    def _ratios(self, p):
        al, be, ga = _par_vals(p)
        q = lambda x: f'{sp.nsimplify(x / (1 - x)).p}:{sp.nsimplify(x / (1 - x)).q}'  # noqa: E731
        return q(ga), q(al), q(be)

    def condition(self, p):
        rc1, ra1, rb1 = self._ratios(p)
        ask = 'длину $CD$' if p['ask'] == 'CD' else 'радиус окружности, описанной около треугольника $ABC$'
        return (f'На сторонах $AB$, $BC$ и $AC$ треугольника $ABC$ отмечены точки $C_1$, $A_1$ и $B_1$, причём $AC_1:C_1B={rc1}$, '
                f'$BA_1:A_1C={ra1}$, $AB_1:B_1C={rb1}$. Отрезки $BB_1$ и $CC_1$ пересекаются в точке $D$.\n\n'
                'а) Докажите, что четырёхугольник $ADA_1B_1$ — параллелограмм.\n\n'
                f'б) Найдите {ask}, если отрезки $AD$ и $BC$ перпендикулярны, $AC={p["ac"]}$, $BC={p["bc"]}$.')

    def solution(self, p):
        al, be, ga, cosC, sinC, cd, ab, R = self._v(p)
        a, b = p['bc'], p['ac']
        t = (
            'а) Отложим векторы от точки $A$: $\\vec b=\\overrightarrow{AB}$, $\\vec c=\\overrightarrow{AC}$. Тогда '
            f'$\\overrightarrow{{AB_1}}={tx(be)}\\vec c$, $\\overrightarrow{{AC_1}}={tx(ga)}\\vec b$, '
            f'$\\overrightarrow{{AA_1}}={tx(1 - al)}\\vec b+{tx(al)}\\vec c$. Точка $D$ на $BB_1$: $\\overrightarrow{{AD}}=(1-s)\\vec b+{tx(be)}s\\,\\vec c$, '
            f'на $CC_1$: $\\overrightarrow{{AD}}={tx(ga)}t\\,\\vec b+(1-t)\\vec c$. Приравнивая коэффициенты, находим $s={tx(al)}$: '
            f'$\\overrightarrow{{AD}}={tx(1 - al)}\\vec b+{tx(al - be)}\\vec c$.\n\n'
            f'Тогда $\\overrightarrow{{DA_1}}=\\overrightarrow{{AA_1}}-\\overrightarrow{{AD}}={tx(be)}\\vec c=\\overrightarrow{{AB_1}}$, то есть отрезки '
            '$DA_1$ и $AB_1$ равны и параллельны: $ADA_1B_1$ — параллелограмм.\n\n'
            f'б) В параллелограмме $B_1A_1\\parallel AD\\perp BC$, поэтому треугольник $CB_1A_1$ прямоугольный с прямым углом $A_1$: '
            f'$CA_1={tx((1 - al) * a)}$, $CB_1={tx((1 - be) * b)}$, $\\cos C=\\frac{{CA_1}}{{CB_1}}={tx(cosC)}$, $\\sin C={tx(sinC)}$.\n\n')
        if p['ask'] == 'CD':
            return t + ('Введём координаты: $C(0;0)$, $B({a};0)$, $A({tx(b * cosC)};{tx(b * sinC)})$. По найденному разложению '
                        f'$\\overrightarrow{{AD}}={tx(1 - al)}\\overrightarrow{{AB}}+{tx(al - be)}\\overrightarrow{{AC}}$ получаем координаты $D$ '
                        f'и $$CD={tx(cd)}.$$').replace('{a}', str(a))
        return t + (f'$AB^2=AC^2+BC^2-2\\,AC\\cdot BC\\cos C={tx(ab ** 2)}$, $AB={tx(ab)}$.\n\n'
                    f'$$R=\\frac{{AB}}{{2\\sin C}}=\\frac{{{tx(ab)}}}{{{tx(2 * sinC)}}}={tx(R)}.$$')

    def figure(self, p):
        al, be, ga = (float(x) for x in _par_vals(p))
        a, b = float(p['bc']), float(p['ac'])
        cosC = float(self._v(p)[3])
        C, B = (0.0, 0.0), (a, 0.0)
        A = (b * cosC, b * math.sqrt(1 - cosC ** 2))
        B1, C1, A1 = g.lerp(A, C, be), g.lerp(A, B, ga), g.lerp(B, C, al)
        D = g.intersect(B, B1, C, C1)
        return g.draw({'A': A, 'B': B, 'C': C, 'A1': A1, 'B1': B1, 'C1': C1, 'D': D}, polygons=[['A', 'B', 'C'], ['A', 'D', 'A1', 'B1']],
                      segments=[('B', 'B1'), ('C', 'C1')], dots=['A1', 'B1', 'C1', 'D'])

    def sample(self, rng):
        m, n = rng.choice([(1, 1), (1, 2), (2, 3), (1, 3), (3, 4), (2, 1)])
        al = r(m, m + n)
        be = al / (1 + al)
        for _ in range(40):
            a = rng.randint(4, 40)
            b = rng.randint(4, 70)
            cosC = (1 - al) * a / ((1 - be) * b)
            if 0 < cosC < 1:
                return dict(m=m, n=n, ac=b, bc=a, ask=rng.choice(['CD', 'R']))
        return None


class IsoscelesHMK(Solved):
    """Равнобедренный треугольник, высоты AH и CT, HM ⊥ AB, HK ⊥ AC, E = CT ∩ MK: EH ∥ AB, TH = ME"""
    number, topic = 17, TRI
    fipi = {'FcDc46': dict(s=13, base=10, ask='EK'), '8e946e': dict(s=5, base=6, ask='EK'),
            '80e34e': dict(s=13, base=10, ask='ME'), '0112D3': dict(s=17, base=16, ask='ME')}

    def _v(self, p):
        s, base = sp.Integer(p['s']), sp.Integer(p['base'])
        c = base / 2
        cosB = 1 - 2 * c ** 2 / s ** 2
        cosC = c / s
        return cosB, cosC, base * cosB, base * cosC ** 2

    def answer(self, p):
        cosB, cosC, th, ek = self._v(p)
        return Answer.num(th if p['ask'] == 'ME' else ek)

    def _pts(self, p):
        s, base = float(p['s']), float(p['base'])
        c = base / 2
        A, C, B = (-c, 0.0), (c, 0.0), (0.0, math.sqrt(s * s - c * c))
        H, T = g.foot(A, B, C), g.foot(C, A, B)
        M, K = g.foot(H, A, B), g.foot(H, A, C)
        E = g.intersect(C, T, M, K)
        return A, B, C, H, T, M, K, E

    def check(self, p):
        A, B, C, H, T, M, K, E = self._pts(p)
        assert g.parallel(g.sub(H, E), g.sub(B, A)) and g.close(g.dist(T, H), g.dist(M, E))
        return g.dist(M, E) if p['ask'] == 'ME' else g.dist(E, K)

    def condition(self, p):
        a = ('а) Докажите, что прямые $AB$ и $EH$ параллельны.' if p['ask'] == 'ME' else 'а) Докажите, что $TH=ME$.')
        b = 'отрезка $ME$' if p['ask'] == 'ME' else 'отрезка $EK$'
        return ('В равнобедренном остроугольном треугольнике $ABC$ ($AB=BC$) проведены высоты $AH$ и $CT$ к боковым сторонам $BC$ и $AB$. '
                'Отрезки $HM$ и $HK$ — перпендикуляры к прямым $AB$ и $AC$. Отрезки $CT$ и $MK$ пересекаются в точке $E$.\n\n'
                f'{a}\n\nб) Найдите длину {b}, если $AB={p["s"]}$ и $AC={p["base"]}$.')

    def solution(self, p):
        cosB, cosC, th, ek = self._v(p)
        s, base = p['s'], p['base']
        t = ('а) Точки $M$ и $K$ лежат на окружности с диаметром $AH$ ($\\angle AMH=\\angle AKH=90^\\circ$), поэтому '
             '$\\angle HMK=\\angle HAK=90^\\circ-\\angle C$. Прямые $HM$ и $CT$ перпендикулярны $AB$, значит, параллельны, и угол между прямыми '
             '$MK$ и $CT$ равен $\\angle HMK$: $\\angle KEC=90^\\circ-\\angle C$. В прямоугольном треугольнике $HKC$ $\\angle KHC=90^\\circ-\\angle C$. '
             'Значит, $\\angle KEC=\\angle KHC$, и точки $H$, $E$, $K$, $C$ лежат на одной окружности — с диаметром $HC$ ($\\angle HKC=90^\\circ$). '
             'Тогда $\\angle HEC=90^\\circ$: $EH\\perp CT$, а $CT\\perp AB$, поэтому $EH\\parallel AB$.\n\n'
             'Четырёхугольник $MTEH$: $MT\\parallel EH$, $MH\\parallel TE$ (оба перпендикулярны $AB$), углы прямые — это прямоугольник, его '
             'диагонали равны: $TH=ME$.\n\n')
        if p['ask'] == 'ME':
            return t + ('б) Точки $T$ и $H$ симметричны относительно оси треугольника, $TH\\parallel AC$, треугольник $BTH$ подобен $BAC$ с '
                        f'коэффициентом $\\frac{{BH}}{{BC}}=\\cos B$. $\\cos B=\\frac{{AB^2+BC^2-AC^2}}{{2AB\\cdot BC}}={tx(cosB)}$.\n\n'
                        f'$$ME=TH=AC\\cos B={base}\\cdot {tx(cosB)}={tx(th)}.$$')
        return t + ('б) Точки $H$, $E$, $K$, $C$ лежат на окружности с диаметром $HC$, поэтому $EK=HC\\sin\\angle ECK$. '
                    '$\\angle ECK=\\angle TCA=90^\\circ-\\angle A$, $\\sin\\angle ECK=\\cos A=\\cos C$; $HC=AC\\cos C$.\n\n'
                    f'$\\cos C=\\frac{{AC/2}}{{BC}}={tx(cosC)}$, $$EK=AC\\cos^2C={base}\\cdot {tx(cosC ** 2)}={tx(ek)}.$$')

    def figure(self, p):
        A, B, C, H, T, M, K, E = self._pts(p)
        return g.draw({'A': A, 'B': B, 'C': C, 'H': H, 'T': T, 'M': M, 'K': K, 'E': E}, polygons=[['A', 'B', 'C']],
                      segments=[('A', 'H'), ('C', 'T'), ('H', 'M'), ('H', 'K'), ('M', 'K')], dashed=[('E', 'H')],
                      dots=['H', 'T', 'M', 'K', 'E'])

    def sample(self, rng):
        for _ in range(50):
            s = rng.randint(3, 20)
            base = rng.randint(2, 2 * s - 1)
            if base * base < 2 * s * s:
                return dict(s=s, base=base, ask=rng.choice(['ME', 'EK']))
        return None


class NinePointCircle(Solved):
    """Середины сторон и основание высоты лежат на одной окружности; найти A₁H"""
    number, topic = 17, CIRC
    fipi = {'2AE241': dict(A=60, C=45, bc='2*sqrt(3)'), 'EA7D2B': dict(A=120, C=45, bc='6*sqrt(3)'),
            '9595A4': dict(A=30, C=45, bc='4*sqrt(3)'), 'BAD790': dict(A=120, C=15, bc='4*sqrt(3)')}

    def _v(self, p):
        A, C = p['A'], p['C']
        B = 180 - A - C
        a = sp.sympify(p['bc'])
        b = sp.radsimp(a * sin(B) / sin(A))
        ch = sp.radsimp(b * cos(C))
        return B, a, simp(b), simp(ch), simp(sp.Abs(ch - a / 2))

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        Av, Bv, Cv = g.triangle_angles(180 - p['A'] - p['C'], p['C'], f(p['bc']))
        A1, B1, C1 = g.mid(Bv, Cv), g.mid(Av, Cv), g.mid(Av, Bv)
        H = g.foot(Av, Bv, Cv)
        assert g.concyclic(A1, B1, C1, H)
        return g.dist(A1, H)

    def condition(self, p):
        return ('В треугольнике $ABC$ точки $A_1$, $B_1$ и $C_1$ — середины сторон $BC$, $AC$ и $AB$, $AH$ — высота, '
                f'$\\angle BAC={p["A"]}^\\circ$, $\\angle BCA={p["C"]}^\\circ$.\n\n'
                'а) Докажите, что точки $A_1$, $B_1$, $C_1$ и $H$ лежат на одной окружности.\n\n'
                f'б) Найдите $A_1H$, если $BC={tx(sp.sympify(p["bc"]))}$.')

    def solution(self, p):
        B, a, b, ch, ans = self._v(p)
        A, C = p['A'], p['C']
        return (
            'а) $B_1C_1$ — средняя линия, $B_1C_1\\parallel BC$, то есть $B_1C_1\\parallel HA_1$. $HC_1$ — медиана прямоугольного треугольника '
            '$AHB$, проведённая к гипотенузе: $HC_1=\\frac12 AB$; $A_1B_1$ — средняя линия треугольника $ABC$: $A_1B_1=\\frac12 AB$. '
            'Четырёхугольник $C_1B_1A_1H$ — трапеция с равными боковыми сторонами $HC_1=A_1B_1$, то есть равнобедренная (это не '
            'параллелограмм: тогда было бы $HA_1=C_1B_1=\\frac12 BC$ и $H$ совпала бы с $B$ или $C$). Равнобедренная трапеция вписана в '
            'окружность.\n\n'
            f'б) $\\angle B=180^\\circ-{A}^\\circ-{C}^\\circ={B}^\\circ$. По теореме синусов $AC=\\frac{{BC\\sin B}}{{\\sin A}}={tx(b)}$. '
            f'Угол $C$ острый, $CH=AC\\cos C={tx(ch)}$, $CA_1=\\frac{{BC}}{{2}}={tx(a / 2)}$.\n\n$$A_1H=|CH-CA_1|={tx(ans)}.$$')

    def figure(self, p):
        Av, Bv, Cv = g.triangle_angles(180 - p['A'] - p['C'], p['C'], 4.0)
        A1, B1, C1 = g.mid(Bv, Cv), g.mid(Av, Cv), g.mid(Av, Bv)
        H = g.foot(Av, Bv, Cv)
        O = g.circumcenter(A1, B1, C1)
        pts = {'A': Av, 'B': Bv, 'C': Cv, 'A1': A1, 'B1': B1, 'C1': C1, 'H': H}
        segs = [('A', 'H'), ('B1', 'C1'), ('A1', 'B1'), ('C1', 'H')]
        if H[0] < 0 or H[0] > 4.0:
            segs.append(('B', 'H') if H[0] < 0 else ('C', 'H'))
        return g.draw(pts, polygons=[['A', 'B', 'C']], segments=segs, circles=[(O, g.dist(O, A1))], dots=['A1', 'B1', 'C1', 'H'])

    def sample(self, rng):
        A, C = rng.choice([(60, 45), (120, 45), (30, 45), (120, 15), (60, 30), (30, 60), (45, 60), (75, 45), (105, 30), (135, 15)])
        k = rng.choice([1, 2, 3, 4])
        return dict(A=A, C=C, bc=str(2 * k * S(3)) if rng.random() < 0.5 else str(2 * k * S(2)))


class CyclicThreeChords(Solved):
    """Вписанный четырёхугольник, AB = BC = CD: BC ∥ AD; найти AD"""
    number, topic = 17, CIRC
    fipi = {'C5B743': dict(R=8, a=12)}

    def answer(self, p):
        R, a = sp.Integer(p['R']), sp.Integer(p['a'])
        return Answer.num(3 * a - a ** 3 / R ** 2)

    def check(self, p):
        R, a = float(p['R']), float(p['a'])
        th = 2 * math.degrees(math.asin(a / (2 * R)))
        A, B, C, D = (g.polar(R, 90 + 1.5 * th - k * th) for k in range(4))
        assert g.close(g.dist(A, B), a) and g.close(g.dist(C, D), a) and g.parallel(g.sub(C, B), g.sub(D, A))
        assert 3 * th < 360
        return g.dist(A, D)

    def condition(self, p):
        return (f'Четырёхугольник $ABCD$ вписан в окружность радиуса $R={p["R"]}$. Известно, что $AB=BC=CD={p["a"]}$.\n\n'
                'а) Докажите, что прямые $BC$ и $AD$ параллельны.\n\nб) Найдите $AD$.')

    def solution(self, p):
        R, a = sp.Integer(p['R']), sp.Integer(p['a'])
        s = a / (2 * R)
        return (
            'а) Равные хорды $AB$ и $CD$ стягивают равные дуги, поэтому вписанные углы $\\angle BCA$ и $\\angle CAD$, опирающиеся на них, '
            'равны. Это накрест лежащие углы при прямых $BC$, $AD$ и секущей $AC$, значит, $BC\\parallel AD$.\n\n'
            f'б) Пусть хорда ${a}$ стягивает дугу $2\\varphi$: $\\sin\\varphi=\\frac{{{a}}}{{2R}}={tx(s)}$. Три дуги $AB$, $BC$, $CD$ составляют '
            '$6\\varphi<360^\\circ$, а хорда $AD$ стягивает оставшуюся дугу $360^\\circ-6\\varphi$:\n\n'
            '$$AD=2R\\sin\\frac{360^\\circ-6\\varphi}{2}=2R\\sin3\\varphi=2R(3\\sin\\varphi-4\\sin^3\\varphi)='
            f'{2 * R}\\left(3\\cdot {tx(s)}-4\\cdot {tx(s ** 3)}\\right)={tx(3 * a - a ** 3 / R ** 2)}.$$')

    def figure(self, p):
        R, a = 4.0, 4.0 * p['a'] / p['R']
        th = 2 * math.degrees(math.asin(a / (2 * R)))
        A, B, C, D = (g.polar(R, 90 + 1.5 * th - k * th) for k in range(4))
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'O': (0.0, 0.0)}, polygons=[['A', 'B', 'C', 'D']], circles=[((0.0, 0.0), R)],
                      dots=['O'])

    def sample(self, rng):
        for _ in range(40):
            R = rng.randint(2, 12)
            a = rng.randint(1, 2 * R - 1)
            if a < R * math.sqrt(3) and 3 * a * R * R - a ** 3 > 0:
                return dict(R=R, a=a)
        return None


class OrthicAngle(Solved):
    """Высоты AH, BN, CK: ∠KNH = 60° ⇒ ∠B = 60°; радиус описанной окружности по AK и BH"""
    number, topic = 17, TRI
    fipi = {'6D7942': dict(ak=1, bh=2)}

    def _v(self, p):
        ak, bh = sp.Integer(p['ak']), sp.Integer(p['bh'])
        c = 2 * bh
        a = 2 * (c - ak)
        b = S(a ** 2 + c ** 2 - a * c)
        return c, a, b, sp.radsimp(b / S(3))

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        c, a, b, R = (float(x) for x in self._v(p))
        A, B, C = g.triangle(a, b, c)
        H, N, K = g.foot(A, B, C), g.foot(B, A, C), g.foot(C, A, B)
        assert g.close(g.dist(A, K), p['ak']) and g.close(g.dist(B, H), p['bh']) and g.close(g.angle(K, N, H), 60)
        assert max(g.angle(B, A, C), g.angle(A, B, C), g.angle(A, C, B)) < 90
        return g.circumradius(A, B, C)

    def condition(self, p):
        return ('В остроугольном треугольнике $ABC$ отрезки $AH$, $BN$ и $CK$ — высоты. Известно, что '
                f'$AK={p["ak"]}$, $BH={p["bh"]}$, а $\\angle KNH=60^\\circ$.\n\nа) Докажите, что $\\angle ABC=60^\\circ$.\n\n'
                'б) Найдите радиус окружности, описанной около треугольника $ABC$.')

    def solution(self, p):
        c, a, b, R = self._v(p)
        return (
            'а) Точки $K$ и $N$ лежат на окружности с диаметром $BC$, поэтому $\\angle ANK=\\angle ABC$ (внешний угол вписанного '
            'четырёхугольника $BCNK$). Точки $H$ и $N$ лежат на окружности с диаметром $AB$, поэтому $\\angle CNH=\\angle ABC$. '
            'Тогда $\\angle KNH=180^\\circ-2\\angle ABC=60^\\circ$, $\\angle ABC=60^\\circ$.\n\n'
            f'б) В прямоугольном треугольнике $ABH$: $BH=AB\\cos60^\\circ$, $AB={tx(c)}$. $AK=AC\\cos A$, $BH=AB\\cos B$, и '
            f'$AC\\cos A+BC\\cos B=AB$: ${p["ak"]}+\\frac{{BC}}{{2}}={tx(c)}$, $BC={tx(a)}$. По теореме косинусов '
            f'$AC^2=AB^2+BC^2-AB\\cdot BC={tx(b ** 2)}$, $AC={tx(b)}$.\n\n$$R=\\frac{{AC}}{{2\\sin60^\\circ}}=\\frac{{{tx(b)}}}{{\\sqrt3}}={tx(R)}.$$')

    def figure(self, p):
        c, a, b, R = (float(x) for x in self._v(p))
        A, B, C = g.triangle(a, b, c)
        H, N, K = g.foot(A, B, C), g.foot(B, A, C), g.foot(C, A, B)
        return g.draw({'A': A, 'B': B, 'C': C, 'H': H, 'N': N, 'K': K}, polygons=[['A', 'B', 'C'], ['K', 'N', 'H']],
                      segments=[('A', 'H'), ('B', 'N'), ('C', 'K')], dots=['H', 'N', 'K'])

    def sample(self, rng):
        for _ in range(60):
            ak, bh = rng.randint(1, 6), rng.randint(1, 8)
            c = 2 * bh
            a = 2 * (c - ak)
            if a <= 0:
                continue
            b2 = a * a + c * c - a * c
            if max(a, c) ** 2 < b2 + min(a, c) ** 2 and b2 < a * a + c * c:
                return dict(ak=ak, bh=bh)
        return None


class TrapezoidPointM(Solved):
    """AD = 2BC, ∠ABM = ∠DCM = 90° ⇒ AM = DM; угол BAD по углу ADC"""
    number, topic = 17, QUAD
    fipi = {'4E19FD': dict(d=70)}

    def answer(self, p):
        return Answer(f'${135 - p["d"]}^\\circ$', math.radians(135 - p['d']))

    def check(self, p):
        d = p['d']

        def build(a):
            Pv = (0.0, 0.0)
            Av = g.polar(1.0, 0)
            # треугольник PAD: ∠A = a, ∠D = d, ∠P = 180 − a − d
            ang_p = 180 - a - d
            Dv = g.polar(math.sin(math.radians(a)) / math.sin(math.radians(d)), ang_p)
            return Pv, Av, Dv
        def gap(a):
            Pv, Av, Dv = build(a)
            M = g.circumcenter(Pv, Av, Dv)
            return g.dist_line(M, Av, Dv) - g.dist(Av, Dv) / 2

        lo, hi = 1.0, 179.0 - d - 1.0   # ∠P = 180 − a − d > 1° ⇒ ищем ∠A делением пополам: расстояние от M до AD = AD/2
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if gap(lo) * gap(mid) <= 0 else (mid, hi)
        Pv, Av, Dv = build(lo)
        B, C = g.mid(Pv, Av), g.mid(Pv, Dv)
        M = g.circumcenter(Pv, Av, Dv)
        assert g.perpendicular(g.sub(M, B), g.sub(Av, B)) and g.close(g.dist(M, Av), g.dist(M, Dv))
        return math.radians(lo)

    def condition(self, p):
        return ('В трапеции $ABCD$ основание $AD$ в два раза больше основания $BC$. Внутри трапеции взяли точку $M$ так, что углы $ABM$ и '
                '$DCM$ прямые.\n\nа) Докажите, что $AM=DM$.\n\n'
                f'б) Найдите угол $BAD$, если угол $ADC$ равен ${p["d"]}^\\circ$, а расстояние от точки $M$ до прямой $AD$ равно стороне $BC$.')

    def solution(self, p):
        d = p['d']
        return (
            'а) Пусть прямые $AB$ и $CD$ пересекаются в точке $P$. Так как $BC\\parallel AD$ и $BC=\\frac12 AD$, $BC$ — средняя линия '
            'треугольника $PAD$: $B$ и $C$ — середины $PA$ и $PD$. $MB\\perp PA$ и проходит через её середину — это серединный перпендикуляр, '
            'поэтому $MP=MA$; аналогично $MP=MD$. Значит, $AM=DM$.\n\n'
            'б) $M$ равноудалена от $P$, $A$, $D$ — это центр описанной окружности треугольника $PAD$ (радиус $R$). Расстояние от центра '
            'до хорды $AD$ равно $R\\cos\\angle P$ (точка $M$ внутри треугольника, угол $P$ острый), а $AD=2R\\sin\\angle P$. Условие '
            '«расстояние равно $BC=\\frac{AD}{2}$» даёт $R\\cos\\angle P=R\\sin\\angle P$, $\\angle P=45^\\circ$.\n\n'
            f'$$\\angle BAD=180^\\circ-\\angle P-\\angle ADC=180^\\circ-45^\\circ-{d}^\\circ={135 - d}^\\circ.$$')

    def figure(self, p):
        d = p['d']
        a = 135 - d
        Av, Dv = (0.0, 0.0), (2.0, 0.0)
        hP = 2.0 * math.sin(math.radians(a)) * math.sin(math.radians(d)) / math.sin(math.radians(45))
        Pv = (hP / math.tan(math.radians(a)), hP)
        B, C = g.mid(Pv, Av), g.mid(Pv, Dv)
        M = g.circumcenter(Pv, Av, Dv)
        return g.draw({'A': Av, 'B': B, 'C': C, 'D': Dv, 'M': M, 'P': Pv}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('B', 'M'), ('C', 'M'), ('A', 'M'), ('D', 'M')], dashed=[('B', 'P'), ('C', 'P')],
                      right=[('B', 'A', 'M'), ('C', 'M', 'D')], dots=['M'])

    def sample(self, rng):
        d = rng.choice([55, 60, 65, 70, 75, 80])
        a = 135 - d
        if math.sin(math.radians(a)) * math.sin(math.radians(d)) <= 1 / math.sqrt(2) or a >= 90:
            return None
        return dict(d=d)


def _tangent_polygon(r_, angles):
    """Описанный многоугольник: внутренние углы по порядку обхода (первая сторона — нижняя касательная y = −r)"""
    normals, n = [], -90.0
    for a in angles:
        normals.append(n)
        n += 180 - a
    lines = [((math.cos(math.radians(t)), math.sin(math.radians(t))), r_) for t in normals]
    verts = []
    for i in range(len(lines)):
        (n1, d1), (n2, d2) = lines[i - 1], lines[i]
        det = n1[0] * n2[1] - n1[1] * n2[0]
        verts.append(((d1 * n2[1] - d2 * n1[1]) / det, (n1[0] * d2 - n2[0] * d1) / det))
    return verts[1:] + verts[:1]      # verts[k] — вершина между сторонами k и k+1, угол angles[k]


class TangentialKLMN(Solved):
    """Описанный четырёхугольник KLMN, ∠N = 90°, L/2 + M = 90°: точка касания A на MN лежит на LO; найти MN"""
    number, topic = 17, CIRC
    fipi = {'4963Fe': dict(L=120, M=30, la=1), '548cBA': dict(L=60, M=60, la=3)}

    def _v(self, p):
        L, M, la = p['L'], p['M'], sp.Integer(p['la'])
        rr = simp(la / (1 / sin(sp.Rational(L, 2)) + 1))
        mn = simp(rr * (sp.cot(deg(sp.Rational(M, 2))) + 1))
        return rr, mn

    def answer(self, p):
        return Answer.num(self._v(p)[1])

    def _pts(self, p, rr):
        L, M = p['L'], p['M']
        K = 360 - 90 - L - M
        # первая сторона NM — нижняя, обход против часовой: M, L, K, N
        Mv, Lv, Kv, Nv = _tangent_polygon(rr, [M, L, K, 90])
        return Nv, Mv, Lv, Kv

    def check(self, p):
        rr = float(self._v(p)[0])
        Nv, Mv, Lv, Kv = self._pts(p, rr)
        A = (0.0, -rr)
        assert g.close(g.angle(Mv, Nv, Kv), 90) and g.close(g.angle(Kv, Lv, Mv), p['L']) and g.close(g.angle(Lv, Mv, Nv), p['M'])
        assert abs(g.cross(g.sub(Lv, (0.0, 0.0)), g.sub(A, (0.0, 0.0)))) < 1e-9 and g.close(g.dist(Lv, A), p['la'])
        return g.dist(Mv, Nv)

    def condition(self, p):
        L, M = p['L'], p['M']
        K = 270 - L - M
        angs = f'$\\angle NKL=\\angle KLM={L}^\\circ$' if K == L else (f'$\\angle LMN=\\angle KLM={L}^\\circ$' if M == L else
                                                                     f'$\\angle KLM={L}^\\circ$, $\\angle LMN={M}^\\circ$')
        return ('В четырёхугольник $KLMN$ вписана окружность с центром $O$. Она касается стороны $MN$ в точке $A$. Известно, что '
                f'$\\angle MNK=90^\\circ$, {angs}.\n\nа) Докажите, что точка $A$ лежит на прямой $LO$.\n\n'
                f'б) Найдите длину стороны $MN$, если $LA={p["la"]}$.')

    def solution(self, p):
        L, M, la = p['L'], p['M'], p['la']
        rr, mn = self._v(p)
        K = 270 - L - M
        return (
            f'а) Углы четырёхугольника: $\\angle N=90^\\circ$, $\\angle L={L}^\\circ$, $\\angle M={M}^\\circ$, $\\angle K={K}^\\circ$. '
            'Центр вписанной окружности лежит на биссектрисах углов: $\\angle OLM=\\frac12\\angle L$, $\\angle OML=\\frac12\\angle M$. '
            f'В треугольнике $LOM$: $\\angle LOM=180^\\circ-{tx(sp.Rational(L, 2))}^\\circ-{tx(sp.Rational(M, 2))}^\\circ={tx(180 - sp.Rational(L + M, 2))}^\\circ$. '
            f'В прямоугольном треугольнике $OAM$ ($OA\\perp MN$): $\\angle MOA=90^\\circ-{tx(sp.Rational(M, 2))}^\\circ={tx(90 - sp.Rational(M, 2))}^\\circ$. '
            '$\\angle LOM+\\angle MOA=180^\\circ$, поэтому точки $L$, $O$, $A$ лежат на одной прямой.\n\n'
            f'б) Пусть $r$ — радиус окружности. $LO=\\frac{{r}}{{\\sin{tx(sp.Rational(L, 2))}^\\circ}}$, $LA=LO+OA=r\\left(\\frac1{{\\sin{tx(sp.Rational(L, 2))}^\\circ}}+1\\right)={la}$, '
            f'$r={tx(rr)}$. Отрезки касательных: $NA=r$ (угол $N$ прямой, $ONAK\'$ — квадрат), $MA=r\\operatorname{{ctg}}{tx(sp.Rational(M, 2))}^\\circ$.\n\n'
            f'$$MN=r\\left(\\operatorname{{ctg}}{tx(sp.Rational(M, 2))}^\\circ+1\\right)={tx(mn)}.$$')

    def figure(self, p):
        rr = 1.0
        Nv, Mv, Lv, Kv = self._pts(p, rr)
        A = (0.0, -rr)
        return g.draw({'K': Kv, 'L': Lv, 'M': Mv, 'N': Nv, 'O': (0.0, 0.0), 'A': A}, polygons=[['N', 'M', 'L', 'K']],
                      circles=[((0.0, 0.0), rr)], dashed=[('L', 'A')], dots=['O', 'A'])

    def sample(self, rng):
        L = rng.choice([60, 80, 100, 120, 140])
        M = 90 - L // 2
        if 270 - L - M >= 180:
            return None
        return dict(L=L, M=M, la=rng.randint(1, 6))


class Angle120Orthocenter(Solved):
    """∠A = 120°: AH = AO; площадь треугольника AHO"""
    number, topic = 17, TRI
    fipi = {'41A5F8': dict(bc='sqrt(15)', B=45), '3B468E': dict(bc='3', B=15)}

    def _v(self, p):
        a, B = sp.sympify(p['bc']), p['B']
        C = 60 - B
        R = simp(a / S(3))
        return a, B, C, R, simp(R ** 2 * sin(abs(B - C)) / 2)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        a, B, C, R, s = self._v(p)
        Av, Bv, Cv = g.triangle_angles(B, C, f(a))
        H, O = g.orthocenter(Av, Bv, Cv), g.circumcenter(Av, Bv, Cv)
        assert g.close(g.dist(Av, H), g.dist(Av, O))
        return g.area(Av, H, O)

    def condition(self, p):
        return ('В треугольнике $ABC$ угол $A$ равен $120^\\circ$. Прямые, содержащие высоты $BM$ и $CN$, пересекаются в точке $H$. '
                'Точка $O$ — центр окружности, описанной около треугольника $ABC$.\n\nа) Докажите, что $AH=AO$.\n\n'
                f'б) Найдите площадь треугольника $AHO$, если $BC={tx(sp.sympify(p["bc"]))}$, $\\angle ABC={p["B"]}^\\circ$.')

    def solution(self, p):
        a, B, C, R, s = self._v(p)
        return (
            'а) Пусть $BB\'$ — диаметр описанной окружности. Тогда $B\'C\\perp BC$ и $B\'A\\perp AB$, то есть $B\'C\\parallel AH$ (обе '
            'перпендикулярны $BC$) и $B\'A\\parallel CH$ (обе перпендикулярны $AB$): $AHCB\'$ — параллелограмм, $AH=B\'C$. Если $A_1$ — '
            'середина $BC$, то $OA_1$ — средняя линия треугольника $BB\'C$: $B\'C=2\\,OA_1$. Центральный угол $BOC$ равен '
            '$2(180^\\circ-120^\\circ)=120^\\circ$, поэтому $OA_1=R\\cos60^\\circ=\\frac R2$, и $AH=2\\cdot\\frac R2=R=AO$.\n\n'
            f'б) $R=\\frac{{BC}}{{2\\sin120^\\circ}}=\\frac{{BC}}{{\\sqrt3}}={tx(R)}$, $\\angle C=60^\\circ-{B}^\\circ={C}^\\circ$. Треугольник $AOB$ '
            'равнобедренный с углом $AOB=2\\angle C$, поэтому прямая $AO$ образует с $AB$ угол $90^\\circ-\\angle C$, а высота $AH$ образует '
            'с $AB$ угол $90^\\circ-\\angle B$. Угол между прямыми $AH$ и $AO$ равен $|\\angle B-\\angle C|$ (или дополняет его до $180^\\circ$, '
            f'синус тот же), $|B-C|={abs(B - C)}^\\circ$.\n\n'
            f'$$S_{{AHO}}=\\frac12\\,AH\\cdot AO\\cdot\\sin{abs(B - C)}^\\circ=\\frac12\\cdot {tx(R ** 2)}\\cdot {tx(sin(abs(B - C)))}={tx(s)}.$$')

    def figure(self, p):
        a, B, C, R, s = self._v(p)
        Av, Bv, Cv = g.triangle_angles(B, C, 4.0)
        H, O = g.orthocenter(Av, Bv, Cv), g.circumcenter(Av, Bv, Cv)
        Mv, Nv = g.foot(Bv, Av, Cv), g.foot(Cv, Av, Bv)
        return g.draw({'A': Av, 'B': Bv, 'C': Cv, 'H': H, 'O': O, 'M': Mv, 'N': Nv}, polygons=[['A', 'B', 'C'], ['A', 'H', 'O']],
                      dashed=[('B', 'H'), ('C', 'H'), ('A', 'M'), ('A', 'N')], dots=['H', 'O', 'M', 'N'])

    def sample(self, rng):
        B = rng.choice([15, 45])          # |B − C| = 30°
        return dict(bc=rng.choice(['3', 'sqrt(3)', '2*sqrt(3)', 'sqrt(6)', 'sqrt(15)', '6']), B=B)


class ParallelogramCircle(Solved):
    """Окружность через три вершины параллелограмма: равные отрезки, отношение хорд, сторона"""
    number, topic = 17, CIRC
    fipi = {'0BC5F1': dict(kind='ABC', A=30, ask='KE:AC'), '813416': dict(kind='ABD', A=60, ask='KE:BD'),
            '909839': dict(kind='ABD', ab=1, bc=2, cos='2/3', ask='CD:DN'),
            '73BE23': dict(kind='ABD2', ce=10, dk=9, cos='1/5', ask='AD')}

    def answer(self, p):
        if p['ask'] in ('KE:AC', 'KE:BD'):
            return Answer.num(simp(2 * cos(p['A'])))
        c = sp.Rational(p['cos'])
        if p['ask'] == 'CD:DN':
            x, y = sp.Integer(p['ab']), sp.Integer(p['bc'])
            return Answer.ratio(x, 2 * y * c - x)
        x = sp.Integer(p['ce']) / (2 * c)
        return Answer.num((x - p['dk']) / (2 * c))

    def _para(self, ab, ad, ang):
        A = (0.0, 0.0)
        B = g.polar(ab, ang)
        D = (ad, 0.0)
        return A, B, g.add(B, D), D

    def check(self, p):
        if p['kind'] == 'ABC':
            A, B, C, D = self._para(1.3, 1.0, p['A'])
            O = g.circumcenter(A, B, C)
            R = g.dist(O, A)
            E = g.second(A, D, O, R, A)
            K = g.second(C, D, O, R, C)
            assert g.dist(A, E) > g.dist(A, D) and g.dist(C, K) > g.dist(C, D) and g.close(g.dist(B, K), g.dist(B, E))
            return g.dist(K, E) / g.dist(A, C)
        if p['ask'] == 'KE:BD':
            A, B, C, D = self._para(1.0, 1.4, p['A'])
            O = g.circumcenter(A, B, D)
            R = g.dist(O, A)
            E = g.second(B, C, O, R, B)
            K = g.second(C, D, O, R, D)
            assert g.dist(B, E) < g.dist(B, C) and g.dist(C, K) > g.dist(C, D) and g.close(g.dist(A, E), g.dist(A, K))
            return g.dist(K, E) / g.dist(B, D)
        c = float(sp.Rational(p['cos']))
        ang = math.degrees(math.acos(c))
        if p['ask'] == 'CD:DN':
            A, B, C, D = self._para(float(p['ab']), float(p['bc']), ang)
            O = g.circumcenter(A, B, D)
            R = g.dist(O, A)
            Mv = g.second(B, C, O, R, B)
            N = g.second(C, D, O, R, D)
            assert g.dist(C, N) > g.dist(C, D) and g.close(g.dist(A, Mv), g.dist(A, N))
            return g.dist(C, D) / g.dist(D, N)
        x = float(p['ce']) / (2 * c)
        y = (x - p['dk']) / (2 * c)
        A, B, C, D = self._para(x, y, ang)
        O = g.circumcenter(A, B, D)
        R = g.dist(O, A)
        E = g.second(B, C, O, R, B)
        K = g.second(C, D, O, R, D)
        assert g.close(g.dist(C, E), p['ce']) and g.close(g.dist(D, K), p['dk']) and g.close(g.dist(A, E), g.dist(A, K))
        return y

    def condition(self, p):
        if p['kind'] == 'ABC':
            return ('Окружность проходит через вершины $A$, $B$ и $C$ параллелограмма $ABCD$, пересекает продолжение стороны $AD$ за точку $D$ '
                    'в точке $E$ и продолжение стороны $CD$ за точку $D$ в точке $K$.\n\nа) Докажите, что $BK=BE$.\n\n'
                    f'б) Найдите отношение $KE:AC$, если $\\angle BAD={p["A"]}^\\circ$.')
        if p['ask'] == 'KE:BD':
            return ('Окружность проходит через вершины $A$, $B$ и $D$ параллелограмма $ABCD$, пересекает сторону $BC$ в точках $B$ и $E$ и '
                    'продолжение стороны $CD$ за точку $D$ в точке $K$.\n\nа) Докажите, что $AE=AK$.\n\n'
                    f'б) Найдите отношение $KE:BD$, если $\\angle BAD={p["A"]}^\\circ$.')
        if p['ask'] == 'CD:DN':
            return ('Окружность проходит через вершины $A$, $B$ и $D$ параллелограмма $ABCD$, пересекает сторону $BC$ в точках $B$ и $M$ и '
                    'продолжение стороны $CD$ за точку $D$ в точке $N$.\n\nа) Докажите, что $AM=AN$.\n\n'
                    f'б) Найдите отношение $CD:DN$, если $AB:BC={p["ab"]}:{p["bc"]}$, а $\\cos\\angle BAD={tx(sp.Rational(p["cos"]))}$.')
        return ('Окружность проходит через вершины $A$, $B$ и $D$ параллелограмма $ABCD$, пересекает сторону $BC$ в точках $B$ и $E$ и '
                'сторону $CD$ в точках $K$ и $D$.\n\nа) Докажите, что $AE=AK$.\n\n'
                f'б) Найдите $AD$, если $CE={p["ce"]}$, $DK={p["dk"]}$ и $\\cos\\angle BAD={tx(sp.Rational(p["cos"]))}$.')

    def solution(self, p):
        if p['kind'] == 'ABC':
            A = p['A']
            return (
                'а) Вписанный четырёхугольник $ABCE$ — трапеция ($BC\\parallel AE$), а вписанная трапеция равнобедренная, поэтому её диагонали '
                'равны: $BE=AC$. Аналогично $ABCK$ — вписанная трапеция ($AB\\parallel CK$), $BK=AC$. Значит, $BK=BE$.\n\n'
                'б) Пусть $\\alpha=\\angle BAD$, $R$ — радиус окружности. $\\angle ABC=180^\\circ-\\alpha$, $AC=2R\\sin(180^\\circ-\\alpha)=2R\\sin\\alpha$. '
                'В треугольнике $CDE$: $\\angle CDE=180^\\circ-\\angle ADC=\\alpha$, а $\\angle CED=\\angle BAE=\\alpha$ (углы при основании '
                'равнобедренной трапеции $ABCE$). Значит, $\\angle DCE=180^\\circ-2\\alpha$, и вписанный угол $KCE$ опирается на хорду $KE$: '
                '$KE=2R\\sin(180^\\circ-2\\alpha)=2R\\sin2\\alpha$.\n\n'
                f'$$\\frac{{KE}}{{AC}}=\\frac{{\\sin2\\alpha}}{{\\sin\\alpha}}=2\\cos\\alpha=2\\cos{A}^\\circ={tx(simp(2 * cos(A)))}.$$')
        pre = ('а) $ABED$ — вписанная трапеция ($AD\\parallel BE$), она равнобедренная, и её диагонали равны: $AE=BD$. Четырёхугольник с '
               'вершинами $A$, $B$, $D$, $K$ — тоже вписанная трапеция ($AB\\parallel DK$), поэтому $AK=BD$. Значит, $AE=AK$.\n\n')
        if p['ask'] == 'KE:BD':
            A = p['A']
            return pre + (
                'б) Пусть $\\alpha=\\angle BAD$. $\\angle BCD=\\alpha$; $\\angle DEB=180^\\circ-\\alpha$ (вписанный четырёхугольник $ABED$), поэтому '
                '$\\angle DEC=\\alpha$ и в треугольнике $CDE$ $\\angle CDE=180^\\circ-2\\alpha$, $\\angle KDE=2\\alpha$. Хорды через радиус: '
                '$KE=2R\\sin2\\alpha$, $BD=2R\\sin\\alpha$.\n\n'
                f'$$\\frac{{KE}}{{BD}}=2\\cos\\alpha=2\\cos{A}^\\circ={tx(simp(2 * cos(A)))}.$$')
        c = sp.Rational(p['cos'])
        if p['ask'] == 'CD:DN':
            x, y = p['ab'], p['bc']
            dn = 2 * y * c - x
            return pre + (
                'б) Пусть $AB=x$, $AD=BC=y$, $\\alpha=\\angle BAD$. В равнобедренной трапеции $ABDN$ с основаниями $AB$ и $DN$ проекции '
                'боковых сторон на прямую $AB$ равны $y\\cos\\alpha$; точка $N$ лежит за $D$, поэтому $DN=2y\\cos\\alpha-x$. При '
                f'$x:y={x}:{y}$: $DN={tx(dn)}$ (в долях $AB$), $CD=AB={x}$.\n\n'
                f'$$CD:DN={x}:{tx(dn)}={self.answer(p).display.strip("$")}.$$')
        x = sp.Integer(p['ce']) / (2 * c)
        y = (x - p['dk']) / (2 * c)
        return pre + (
            'б) Пусть $AB=CD=x$, $AD=BC=y$, $\\cos\\alpha=\\cos\\angle BAD$. В равнобедренной трапеции $ABED$ ($AD\\parallel BE$) '
            '$BE=AD-2AB\\cos\\alpha=y-2x\\cos\\alpha$, поэтому $CE=BC-BE=2x\\cos\\alpha$. В равнобедренной трапеции $ABKD$ ($AB\\parallel DK$) '
            '$DK=AB-2AD\\cos\\alpha=x-2y\\cos\\alpha$.\n\n'
            f'$2x\\cdot {tx(c)}={p["ce"]}$, $x={tx(x)}$; ${tx(x)}-2y\\cdot {tx(c)}={p["dk"]}$, $$AD=y={tx(y)}.$$')

    def figure(self, p):
        if p['kind'] == 'ABC':
            A, B, C, D = self._para(1.3, 1.0, p['A'])
            O = g.circumcenter(A, B, C)
            R = g.dist(O, A)
            E, K = g.second(A, D, O, R, A), g.second(C, D, O, R, C)
            return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'K': K}, polygons=[['A', 'B', 'C', 'D']],
                          segments=[('D', 'E'), ('D', 'K'), ('B', 'E'), ('B', 'K'), ('K', 'E')], circles=[(O, R)], dots=['E', 'K'])
        if p['ask'] == 'KE:BD':
            A, B, C, D = self._para(1.0, 1.4, p['A'])
        elif p['ask'] == 'CD:DN':
            c = float(sp.Rational(p['cos']))
            A, B, C, D = self._para(float(p['ab']), float(p['bc']), math.degrees(math.acos(c)))
        else:
            c = float(sp.Rational(p['cos']))
            x = float(p['ce']) / (2 * c)
            A, B, C, D = self._para(x, (x - p['dk']) / (2 * c), math.degrees(math.acos(c)))
        O = g.circumcenter(A, B, D)
        R = g.dist(O, A)
        E, K = g.second(B, C, O, R, B), g.second(C, D, O, R, D)
        e, k = ('M', 'N') if p['ask'] == 'CD:DN' else ('E', 'K')
        segs = [('A', e), ('A', k)] + ([('D', k)] if g.dist(C, K) > g.dist(C, D) else [])
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, e: E, k: K}, polygons=[['A', 'B', 'C', 'D']], segments=segs,
                      circles=[(O, R)], dots=[e, k])

    def sample(self, rng):
        kind = rng.choice(['ABC', 'KE', 'CDDN', 'AD'])
        if kind == 'ABC':
            return dict(kind='ABC', A=rng.choice([30, 45, 60]), ask='KE:AC')
        if kind == 'KE':
            return dict(kind='ABD', A=rng.choice([30, 45, 60]), ask='KE:BD')
        c = rng.choice(['1/5', '1/4', '1/3', '2/3', '3/4', '2/5', '3/5'])
        cv = sp.Rational(c)
        if kind == 'CDDN':
            x, y = rng.randint(1, 4), rng.randint(1, 5)
            if 2 * y * cv - x <= 0:
                return None
            return dict(kind='ABD', ab=x, bc=y, cos=c, ask='CD:DN')
        x = rng.randint(4, 30)
        ce = 2 * x * cv
        y = rng.randint(2, 30)
        dk = x - 2 * y * cv
        if not (ce.q == 1 and dk.q == 1 and dk > 0 and ce < y):
            return None
        return dict(kind='ABD2', ce=int(ce), dk=int(dk), cos=c, ask='AD')


class TrapezoidBisectorsO(Solved):
    """Равнобедренная трапеция, биссектрисы углов A и C пересекаются в O; прямая через O ∥ основаниям"""
    number, topic = 17, QUAD
    fipi = {'B58CFA': dict(ask='AM:MB', rho='17/31'), 'E87882': dict(ask='BC:AD', t='1/3')}

    def _from_t(self, t):
        u = t / (1 - t)
        sina, cosa = 2 * u / (1 + u ** 2), (1 - u ** 2) / (1 + u ** 2)
        cot = cosa / sina
        D = 1 / sina + 2 * t * cot
        C = D - 2 * cot
        return u, sina, cosa, cot, D, C

    def _t(self, p):
        if p['ask'] == 'BC:AD':
            return sp.Rational(p['t'])
        rho = sp.Rational(p['rho'])
        k = 2 / (1 - rho)
        return simp((k - S(k ** 2 - 2 * k + 2)) / 2)

    def answer(self, p):
        t = self._t(p)
        if p['ask'] == 'AM:MB':
            return Answer.ratio(t, 1 - t)
        u, sina, cosa, cot, D, C = self._from_t(t)
        return Answer.ratio(C, D)

    def check(self, p):
        t = float(self._t(p))
        u, sina, cosa, cot, D, C = (float(x) for x in self._from_t(sp.nsimplify(t)))
        h = 1.0
        A, Dv = (-D / 2, 0.0), (D / 2, 0.0)
        B, Cv = (-C / 2, h), (C / 2, h)
        # биссектрисы углов A и C
        bA = g.add(g.mul(g.sub(B, A), 1 / g.dist(A, B)), g.mul(g.sub(Dv, A), 1 / g.dist(A, Dv)))
        bC = g.add(g.mul(g.sub(B, Cv), 1 / g.dist(B, Cv)), g.mul(g.sub(Dv, Cv), 1 / g.dist(Dv, Cv)))
        O = g.intersect(A, g.add(A, bA), Cv, g.add(Cv, bC))
        assert g.close(g.dist(A, O), g.dist(Cv, O))
        M = g.intersect(O, g.add(O, (1.0, 0.0)), A, B)
        N = g.intersect(O, g.add(O, (1.0, 0.0)), Cv, Dv)
        assert g.close(g.dist(M, N), g.dist(A, B)) and g.close(g.dist(A, M), g.dist(M, O))
        if p['ask'] == 'AM:MB':
            assert g.close(C / D, float(sp.Rational(p['rho'])))
            return g.dist(A, M) / g.dist(M, B)
        return C / D

    def condition(self, p):
        if p['ask'] == 'AM:MB':
            rho = sp.Rational(p['rho'])
            return ('Биссектрисы углов $BAD$ и $BCD$ равнобедренной трапеции $ABCD$ пересекаются в точке $O$. На боковых сторонах $AB$ и $CD$ '
                    'отмечены точки $M$ и $N$ так, что $AM=MO$, $CN=NO$.\n\nа) Докажите, что точки $M$, $O$ и $N$ лежат на одной прямой.\n\n'
                    f'б) Найдите отношение $AM:MB$, если $AO=CO$ и $BC:AD={rho.p}:{rho.q}$.')
        t = sp.Rational(p['t'])
        return ('Биссектрисы углов $BAD$ и $BCD$ равнобедренной трапеции $ABCD$ пересекаются в точке $O$. Через точку $O$ проведена прямая, '
                'параллельная основаниям $BC$ и $AD$.\n\nа) Докажите, что отрезок этой прямой внутри трапеции равен её боковой стороне.\n\n'
                f'б) Найдите отношение длин оснований трапеции, если $AO=CO$ и данная прямая делит сторону $AB$ в отношении '
                f'$AM:MB={t.p}:{t.q - t.p}$.')

    def solution(self, p):
        t = self._t(p)
        u, sina, cosa, cot, D, C = self._from_t(t)
        if p['ask'] == 'AM:MB':
            a = ('а) $AM=MO$, поэтому $\\angle MOA=\\angle MAO=\\angle OAD$, и $MO\\parallel AD$ (накрест лежащие углы). Аналогично из $CN=NO$: '
                 '$\\angle NOC=\\angle NCO=\\angle OCB$, $NO\\parallel BC\\parallel AD$. Через $O$ проходит единственная прямая, параллельная $AD$, '
                 'значит, $M$, $O$, $N$ лежат на одной прямой.\n\n')
        else:
            a = ('а) Пусть прямая пересекает $AB$ и $CD$ в точках $M$ и $N$. $\\angle MOA=\\angle OAD=\\angle MAO$, поэтому $AM=MO$; '
                 'аналогично $CN=NO$. Трапеция равнобедренная и $MN\\parallel AD$, поэтому $BM=CN$ (симметрия). '
                 '$MN=MO+ON=AM+BM=AB$.\n\n')
        b = ('б) Как и в пункте а), отрезок $MN$ (через $O$ параллельно основаниям) равен боковой стороне $AB$, $AM=MO$, $CN=NO$. Пусть '
             '$\\alpha=\\angle BAD$, $h$ — высота трапеции, $t=\\frac{AM}{AB}$; точка $O$ находится на высоте $th$ над $AD$. '
             'Из прямоугольных треугольников с гипотенузами $AO$ и $CO$: $AO=\\frac{th}{\\sin\\frac\\alpha2}$, '
             '$CO=\\frac{(1-t)h}{\\cos\\frac\\alpha2}$ (биссектриса угла $C=180^\\circ-\\alpha$ образует с основанием угол $90^\\circ-\\frac\\alpha2$). '
             'Условие $AO=CO$: $\\operatorname{tg}\\frac\\alpha2=\\frac{t}{1-t}$.\n\n'
             'Длина отрезка $MN$ на высоте $th$: $AD-2th\\operatorname{ctg}\\alpha=AB=\\frac{h}{\\sin\\alpha}$, а $AD-BC=2h\\operatorname{ctg}\\alpha$.\n\n')
        if p['ask'] == 'BC:AD':
            return a + b + (f'При $t={tx(t)}$: $\\operatorname{{tg}}\\frac\\alpha2={tx(u)}$, $\\sin\\alpha={tx(sina)}$, $\\operatorname{{ctg}}\\alpha={tx(cot)}$. '
                            f'$AD=\\frac{{h}}{{\\sin\\alpha}}+2th\\operatorname{{ctg}}\\alpha={tx(D)}h$, $BC=AD-2h\\operatorname{{ctg}}\\alpha={tx(C)}h$.\n\n'
                            f'$$BC:AD={self.answer(p).display.strip("$")}.$$')
        rho = sp.Rational(p['rho'])
        k = 2 / (1 - rho)
        return a + b + (
            f'Из $BC:AD={tx(rho)}$: $AD\\left(1-{tx(rho)}\\right)=2h\\operatorname{{ctg}}\\alpha$, $AD={tx(k)}h\\operatorname{{ctg}}\\alpha$. '
            f'Подставляя во второе равенство: $\\cos\\alpha\\left({tx(k)}-2t\\right)=1$, а $\\cos\\alpha=\\frac{{1-u^2}}{{1+u^2}}=\\frac{{1-2t}}{{1-2t+2t^2}}$ '
            f'($u=\\frac{{t}}{{1-t}}$). Получаем $(1-2t)\\left({tx(k)}-2t\\right)=1-2t+2t^2$, то есть $2t^2-{tx(2 * k)}t+{tx(k - 1)}=0$, '
            f'$t={tx(t)}$ (второй корень больше 1).\n\n$$AM:MB={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        t = self._t(p)
        u, sina, cosa, cot, D, C = (float(x) for x in self._from_t(t))
        A, Dv, B, Cv = (-D / 2, 0.0), (D / 2, 0.0), (-C / 2, 1.0), (C / 2, 1.0)
        bA = g.add(g.mul(g.sub(B, A), 1 / g.dist(A, B)), g.mul(g.sub(Dv, A), 1 / g.dist(A, Dv)))
        bC = g.add(g.mul(g.sub(B, Cv), 1 / g.dist(B, Cv)), g.mul(g.sub(Dv, Cv), 1 / g.dist(Dv, Cv)))
        O = g.intersect(A, g.add(A, bA), Cv, g.add(Cv, bC))
        M = g.intersect(O, g.add(O, (1.0, 0.0)), A, B)
        N = g.intersect(O, g.add(O, (1.0, 0.0)), Cv, Dv)
        return g.draw({'A': A, 'B': B, 'C': Cv, 'D': Dv, 'O': O, 'M': M, 'N': N}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('A', 'O'), ('C', 'O'), ('M', 'N')], dots=['O', 'M', 'N'])

    def sample(self, rng):
        t = sp.Rational(*rng.choice([(1, 3), (1, 4), (2, 5), (3, 7), (1, 5), (2, 7), (3, 8)]))
        u, sina, cosa, cot, D, C = self._from_t(t)
        if C <= 0:
            return None
        if rng.random() < 0.5:
            return dict(ask='BC:AD', t=str(t))
        return dict(ask='AM:MB', rho=str(sp.nsimplify(C / D)))


class ParallelogramAMMC(Solved):
    """M на BC, AM = MC: центр вписанной окружности AMD на AC; её радиус"""
    number, topic = 17, CIRC
    fipi = {'2412FA': dict(ab=5, bc=10, A=60)}

    def _v(self, p):
        ab, bc, A = sp.Integer(p['ab']), sp.Integer(p['bc']), p['A']
        Bx, By = ab * cos(A), ab * sin(A)
        Cx = Bx + bc
        # M = (m, By): m² + By² = (Cx − m)² ⇒ m = (Cx² − By²)/(2Cx)
        m = simp((Cx ** 2 - By ** 2) / (2 * Cx))
        am = simp(Cx - m)
        md = simp(S((bc - m) ** 2 + By ** 2))
        area = simp(bc * By / 2)
        rr = simp(2 * area / (am + md + bc))
        return By, Cx, m, am, md, area, rr

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        ab, bc, A = float(p['ab']), float(p['bc']), p['A']
        Av, Bv = (0.0, 0.0), g.polar(ab, A)
        Dv = (bc, 0.0)
        Cv = g.add(Bv, Dv)
        # M на BC с AM = MC
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            M = g.lerp(Bv, Cv, mid)
            lo, hi = (lo, mid) if g.dist(Av, M) > g.dist(M, Cv) else (mid, hi)   # AM − MC растёт
        M = g.lerp(Bv, Cv, lo)
        I = g.incenter(Av, M, Dv)
        assert g.parallel(g.sub(Cv, Av), g.sub(I, Av))
        return g.inradius(Av, M, Dv)

    def condition(self, p):
        return ('На стороне $BC$ параллелограмма $ABCD$ выбрана точка $M$ такая, что $AM=MC$.\n\n'
                'а) Докажите, что центр вписанной в треугольник $AMD$ окружности лежит на диагонали $AC$.\n\n'
                f'б) Найдите радиус вписанной в треугольник $AMD$ окружности, если $AB={p["ab"]}$, $BC={p["bc"]}$, $\\angle BAD={p["A"]}^\\circ$.')

    def solution(self, p):
        By, Cx, m, am, md, area, rr = self._v(p)
        ab, bc, A = p['ab'], p['bc'], p['A']
        return (
            'а) $AM=MC$, поэтому $\\angle MAC=\\angle MCA$, а $\\angle MCA=\\angle CAD$ (накрест лежащие при $BC\\parallel AD$). Значит, $AC$ — '
            'биссектриса угла $MAD$ треугольника $AMD$, и центр вписанной окружности, лежащий на биссектрисах, лежит на $AC$.\n\n'
            f'б) Введём координаты: $A(0;0)$, $D({bc};0)$, $B\\left({tx(ab * cos(A))};{tx(By)}\\right)$, $C\\left({tx(Cx)};{tx(By)}\\right)$. '
            f'Точка $M(m;{tx(By)})$ на $BC$ с $AM=MC$: $m^2+{tx(By ** 2)}=({tx(Cx)}-m)^2$, $m={tx(m)}$. Тогда $AM=MC={tx(am)}$, '
            f'$MD=\\sqrt{{({bc}-m)^2+{tx(By ** 2)}}}={tx(md)}$, $S_{{AMD}}=\\frac12\\cdot AD\\cdot {tx(By)}={tx(area)}$.\n\n'
            f'$$r=\\frac{{2S}}{{AM+MD+AD}}=\\frac{{{tx(2 * area)}}}{{{tx(am)}+{tx(md)}+{bc}}}={tx(rr)}.$$')

    def figure(self, p):
        By, Cx, m, am, md, area, rr = (float(x) for x in self._v(p))
        ab, bc, A = float(p['ab']), float(p['bc']), p['A']
        Av, Bv, Dv = (0.0, 0.0), g.polar(ab, A), (bc, 0.0)
        Cv = g.add(Bv, Dv)
        M = (m, By)
        I = g.incenter(Av, M, Dv)
        return g.draw({'A': Av, 'B': Bv, 'C': Cv, 'D': Dv, 'M': M, 'I': I}, polygons=[['A', 'B', 'C', 'D'], ['A', 'M', 'D']],
                      segments=[('A', 'C')], circles=[(I, rr)], dots=['M', 'I'])

    def sample(self, rng):
        A = rng.choice([60, 90, 120, 60])
        ab, bc = rng.randint(2, 8), rng.randint(3, 12)
        By = ab * math.sin(math.radians(A))
        Cx = ab * math.cos(math.radians(A)) + bc
        m = (Cx ** 2 - By ** 2) / (2 * Cx)
        if not (ab * math.cos(math.radians(A)) < m < Cx):
            return None
        return dict(ab=ab, bc=bc, A=A)


class TangentAngleDiameter(Solved):
    """Окружность касается сторон угла N в A и B, BC — диаметр: AC ∥ NO; ∠ANB = 2∠ABC"""
    number, topic = 17, CIRC
    fipi = {'6B82FF': dict(ac=10, ab=24, ask='NO'), '8377A1': dict(ac=14, ab=36, ask='dist')}

    def answer(self, p):
        ac, ab = sp.Integer(p['ac']), sp.Integer(p['ab'])
        ok = ac / 2
        if p['ask'] == 'NO':
            return Answer.num((ab ** 2 + ac ** 2) / 4 / ok)
        return Answer.num((ab / 2) ** 2 / ok)

    def check(self, p):
        ac, ab = float(p['ac']), float(p['ab'])
        rr = math.hypot(ac, ab) / 2
        O = (0.0, 0.0)
        half = math.asin((ab / 2) / rr)
        A, B = g.polar(rr, 90 + math.degrees(half)), g.polar(rr, 90 - math.degrees(half))
        C = (-B[0], -B[1])
        assert g.close(g.dist(A, C), ac) and g.close(g.dist(A, B), ab)
        tA, tB = g.add(A, (A[1], -A[0])), g.add(B, (B[1], -B[0]))
        N = g.intersect(A, tA, B, tB)
        assert g.parallel(g.sub(C, A), g.sub(N, O)) and g.close(g.angle(A, N, B), 2 * g.angle(A, B, C))
        return g.dist(N, O) if p['ask'] == 'NO' else g.dist_line(N, A, B)

    def condition(self, p):
        a = ('а) Докажите, что прямая $AC$ параллельна биссектрисе угла $ANB$.' if p['ask'] == 'NO'
             else 'а) Докажите, что $\\angle ANB=2\\angle ABC$.')
        b = 'длину отрезка $NO$' if p['ask'] == 'NO' else 'расстояние от точки $N$ до прямой $AB$'
        return ('Окружность с центром $O$ касается сторон угла с вершиной $N$ в точках $A$ и $B$. Отрезок $BC$ — диаметр этой окружности.\n\n'
                f'{a}\n\nб) Найдите {b}, если $AC={p["ac"]}$ и $AB={p["ab"]}$.')

    def solution(self, p):
        ac, ab = sp.Integer(p['ac']), sp.Integer(p['ab'])
        bc2 = ab ** 2 + ac ** 2
        if p['ask'] == 'NO':
            a = ('а) $\\angle BAC=90^\\circ$ (опирается на диаметр), то есть $AC\\perp AB$. Касательные $NA=NB$, а $OA=OB$, поэтому $NO$ — '
                 'серединный перпендикуляр к $AB$ и биссектриса угла $ANB$: $NO\\perp AB$. Значит, $AC\\parallel NO$.\n\n')
        else:
            a = ('а) Треугольник $AOB$ равнобедренный: $\\angle AOB=180^\\circ-2\\angle ABO=180^\\circ-2\\angle ABC$. В четырёхугольнике '
                 '$NAOB$ углы $A$ и $B$ прямые (радиусы к касательным), поэтому $\\angle ANB=180^\\circ-\\angle AOB=2\\angle ABC$.\n\n')
        b = (f'б) $BC=\\sqrt{{AB^2+AC^2}}=\\sqrt{{{tx(bc2)}}}$, $OB=\\frac{{BC}}{{2}}$. Пусть $K$ — середина $AB$; $NO$ проходит через $K$, '
             f'$NO\\perp AB$, и $OK$ — средняя линия треугольника $ABC$: $OK=\\frac{{AC}}{{2}}={tx(ac / 2)}$, $BK={tx(ab / 2)}$. В прямоугольном '
             'треугольнике $NBO$ ($\\angle NBO=90^\\circ$) $BK$ — высота: ')
        if p['ask'] == 'NO':
            return a + b + f'$OB^2=OK\\cdot ON$, $$NO=\\frac{{OB^2}}{{OK}}=\\frac{{{tx(bc2 / 4)}}}{{{tx(ac / 2)}}}={self.answer(p).display.strip("$")}.$$'
        return a + b + (f'$BK^2=OK\\cdot KN$. Расстояние от $N$ до $AB$ — это $NK$: '
                        f'$$NK=\\frac{{BK^2}}{{OK}}=\\frac{{{tx((ab / 2) ** 2)}}}{{{tx(ac / 2)}}}={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        ac, ab = float(p['ac']), float(p['ab'])
        rr = math.hypot(ac, ab) / 2
        half = math.asin((ab / 2) / rr)
        A, B = g.polar(rr, 90 + math.degrees(half)), g.polar(rr, 90 - math.degrees(half))
        C = (-B[0], -B[1])
        N = g.intersect(A, g.add(A, (A[1], -A[0])), B, g.add(B, (B[1], -B[0])))
        return g.draw({'A': A, 'B': B, 'C': C, 'O': (0.0, 0.0), 'N': N}, segments=[('N', 'A'), ('N', 'B'), ('B', 'C'), ('A', 'C'), ('A', 'B')],
                      dashed=[('N', 'O')], circles=[((0.0, 0.0), rr)], dots=['O'])

    def sample(self, rng):
        ac, ab = rng.choice([(10, 24), (14, 48), (6, 8), (12, 16), (10, 24), (16, 30), (18, 24), (7, 24), (12, 35)])
        return dict(ac=ac, ab=ab, ask=rng.choice(['NO', 'dist']))


class IsoTrapezoidHeight(Solved):
    """Равнобедренная трапеция, AD = k·BC: высота делит AD в отношении; расстояние от C до середины отрезка"""
    number, topic = 17, QUAD
    fipi = {'060A0A': dict(k=3, ad=15, ac='2*sqrt(61)', ask='BD'), '832C34': dict(k=2, bc=16, ab=10, ask='OD')}

    def _pts_exact(self, p):
        k = p['k']
        if p['ask'] == 'BD':
            ad = sp.Integer(p['ad'])
            bc = ad / k
            hd = (ad - bc) / 2
            ah = ad - hd
            h = S(sp.sympify(p['ac']) ** 2 - ah ** 2)
        else:
            bc = sp.Integer(p['bc'])
            ad = k * bc
            hd = (ad - bc) / 2
            h = S(sp.Integer(p['ab']) ** 2 - hd ** 2)
        A, D = sp.Matrix([0, 0]), sp.Matrix([ad, 0])
        B, C = sp.Matrix([hd, h]), sp.Matrix([ad - hd, h])
        return ad, bc, hd, h, A, B, C, D

    def answer(self, p):
        ad, bc, hd, h, A, B, C, D = self._pts_exact(p)
        if p['ask'] == 'BD':
            X = (B + D) / 2
        else:
            O = A + (C - A) * ad / (ad + bc)
            X = (O + D) / 2
        return Answer.num(simp(S((X - C).dot(X - C))))

    def check(self, p):
        ad, bc, hd, h, A, B, C, D = self._pts_exact(p)
        P = {k: (float(v[0]), float(v[1])) for k, v in dict(A=A, B=B, C=C, D=D).items()}
        H = g.foot(P['C'], P['A'], P['D'])
        q = g.dist(P['A'], H) / g.dist(H, P['D'])
        assert g.close(q, (p['k'] + 1) / (p['k'] - 1))
        if p['ask'] == 'BD':
            return g.dist(P['C'], g.mid(P['B'], P['D']))
        O = g.intersect(P['A'], P['C'], P['B'], P['D'])
        return g.dist(P['C'], g.mid(O, P['D']))

    def condition(self, p):
        k = p['k']
        word = {2: 'в два раза', 3: 'в три раза', 4: 'в четыре раза', 5: 'в пять раз'}[k]
        ratio = sp.Rational(k + 1, k - 1)
        rel = {2: 'вдвое', 3: 'втрое', 4: 'вчетверо', 5: 'впятеро'}.get(int(ratio), f'в ${tx(ratio)}$ раза') if ratio.q == 1 else f'в ${tx(ratio)}$ раза'
        if p['ask'] == 'BD':
            return (f'В равнобедренной трапеции $ABCD$ основание $AD$ {word} больше основания $BC$.\n\n'
                    f'а) Докажите, что высота $CH$ трапеции разбивает основание $AD$ на отрезки, один из которых {rel} больше другого.\n\n'
                    f'б) Найдите расстояние от вершины $C$ до середины диагонали $BD$, если $AD={p["ad"]}$ и $AC={tx(sp.sympify(p["ac"]))}$.')
        return (f'В равнобедренной трапеции $ABCD$ основание $AD$ {word} больше основания $BC$.\n\n'
                f'а) Докажите, что высота $CH$ трапеции разбивает основание $AD$ на отрезки, один из которых {rel} больше другого.\n\n'
                f'б) Пусть $O$ — точка пересечения диагоналей. Найдите расстояние от вершины $C$ до середины отрезка $OD$, если $BC={p["bc"]}$ и $AB={p["ab"]}$.')

    def solution(self, p):
        ad, bc, hd, h, A, B, C, D = self._pts_exact(p)
        k = p['k']
        ans = self.answer(p).display.strip('$')
        t = ('а) В равнобедренной трапеции $HD=\\frac{AD-BC}{2}$, $AH=AD-HD=\\frac{AD+BC}{2}$. При $AD=' + f'{k}BC$: '
             f'$HD=\\frac{{{k - 1}}}{{2}}BC$, $AH=\\frac{{{k + 1}}}{{2}}BC$, $AH:HD={k + 1}:{k - 1}$' + (
                 f'$={tx(sp.Rational(k + 1, k - 1))}:1$' if (k + 1) % (k - 1) == 0 else '') + '.\n\n')
        if p['ask'] == 'BD':
            ah = ad - hd
            return t + (f'б) $BC={tx(bc)}$, $HD={tx(hd)}$, $AH={tx(ah)}$, $CH=\\sqrt{{AC^2-AH^2}}={tx(h)}$. Введём координаты: $A(0;0)$, '
                        f'$D({tx(ad)};0)$, $B({tx(hd)};{tx(h)})$, $C({tx(ad - hd)};{tx(h)})$. Середина $BD$: '
                        f'$\\left({tx((hd + ad) / 2)};{tx(h / 2)}\\right)$, расстояние до $C$:\n\n$$d={ans}.$$')
        O = A + (C - A) * ad / (ad + bc)
        X = (O + D) / 2
        return t + (f'б) $AD={tx(ad)}$, $HD={tx(hd)}$, $CH=\\sqrt{{CD^2-HD^2}}={tx(h)}$. Диагонали делятся точкой $O$ в отношении '
                    f'$AO:OC=AD:BC={k}:1$. Координаты: $A(0;0)$, $D({tx(ad)};0)$, $C({tx(ad - hd)};{tx(h)})$, '
                    f'$O\\left({tx(O[0])};{tx(O[1])}\\right)$, середина $OD$: $\\left({tx(X[0])};{tx(X[1])}\\right)$.\n\n$$d={ans}.$$')

    def figure(self, p):
        ad, bc, hd, h, A, B, C, D = self._pts_exact(p)
        P = {k: (float(v[0]), float(v[1])) for k, v in dict(A=A, B=B, C=C, D=D).items()}
        P['H'] = g.foot(P['C'], P['A'], P['D'])
        segs = [('C', 'H'), ('B', 'D')]
        if p['ask'] == 'OD':
            P['O'] = g.intersect(P['A'], P['C'], P['B'], P['D'])
            P['X'] = g.mid(P['O'], P['D'])
            segs.append(('A', 'C'))
        else:
            P['X'] = g.mid(P['B'], P['D'])
        return g.draw(P, polygons=[['A', 'B', 'C', 'D']], segments=segs, dashed=[('C', 'X')], dots=['H', 'X'] + (['O'] if 'O' in P else []))

    def sample(self, rng):
        k = rng.choice([2, 3, 4])
        if rng.random() < 0.5:
            bc = rng.randint(2, 10)
            ad = k * bc
            ah = sp.Rational((k + 1) * bc, 2)
            h = rng.randint(2, 12)
            return dict(k=k, ad=ad, ac=str(S(ah ** 2 + h ** 2)), ask='BD')
        bc = 2 * rng.randint(1, 8)
        hd = sp.Rational((k - 1) * bc, 2)
        for ab in range(int(hd) + 1, int(hd) + 20):
            if S(ab ** 2 - hd ** 2).is_Rational:
                return dict(k=k, bc=bc, ab=ab, ask='OD')
        return None


class RightTrapezoidCircle(Solved):
    """Прямоугольная трапеция, окружность на AD как на диаметре пересекает BC в C и M: ∠BAM = ∠CAD; площадь AOB"""
    number, topic = 17, CIRC
    fipi = {'B3890A': dict(b='sqrt(10)', k=2)}

    def _v(self, p):
        b, k = sp.sympify(p['b']), p['k']
        m = simp(b / S(k))
        ad, bc = (k + 1) * m, k * m
        return b, k, m, ad, bc, simp(sp.Rational(k + 1, 2 * k + 1) * b * bc / 2)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        b, k, m, ad, bc, s = (float(x) if not isinstance(x, int) else x for x in self._v(p))
        A, B = (0.0, 0.0), (0.0, b)
        D, C, M = (ad, 0.0), (bc, b), (m, b)
        O = (ad / 2, 0.0)
        assert g.close(g.dist(O, C), ad / 2) and g.close(g.dist(O, M), ad / 2)
        assert g.close(g.angle(B, A, M), g.angle(C, A, D))
        Ov = g.intersect(A, C, B, D)
        return g.area(A, Ov, B)

    def condition(self, p):
        return ('В трапеции $ABCD$ угол $BAD$ прямой. Окружность, построенная на большем основании $AD$ как на диаметре, пересекает меньшее '
                'основание $BC$ в точках $C$ и $M$.\n\nа) Докажите, что $\\angle BAM=\\angle CAD$.\n\n'
                f'б) Диагонали трапеции пересекаются в точке $O$. Найдите площадь треугольника $AOB$, если $AB={tx(sp.sympify(p["b"]))}$, '
                f'а $BC={p["k"]}BM$.')

    def solution(self, p):
        b, k, m, ad, bc, s = self._v(p)
        return (
            'а) Хорда $MC$ параллельна диаметру $AD$, поэтому $AMCD$ — вписанная (равнобедренная) трапеция: $\\angle MAD=\\angle CDA$. '
            '$\\angle ACD=90^\\circ$ (опирается на диаметр), так что $\\angle CAD=90^\\circ-\\angle CDA$; а $\\angle BAM=90^\\circ-\\angle MAD$. '
            'Значит, $\\angle BAM=\\angle CAD$.\n\n'
            f'б) Введём координаты: $A(0;0)$, $B(0;b)$, $b={tx(b)}$, $AD$ по оси $Ox$. Пусть $BM=m$, тогда $BC={k}m$; точки $M(m;b)$ и '
            f'$C({k}m;b)$ симметричны относительно серединного перпендикуляра к $AD$, поэтому центр окружности $\\left(\\frac{{{k + 1}m}}{{2}};0\\right)$, '
            f'$AD={k + 1}m$. Точка $C$ на окружности: $\\left({k}m-\\frac{{{k + 1}m}}{{2}}\\right)^2+b^2=\\left(\\frac{{{k + 1}m}}{{2}}\\right)^2$, '
            f'откуда ${k}m^2=b^2$, $m={tx(m)}$, $BC={tx(bc)}$, $AD={tx(ad)}$.\n\n'
            f'Диагонали делятся в отношении $AO:OC=AD:BC={k + 1}:{k}$, поэтому '
            f'$$S_{{AOB}}=\\frac{{{k + 1}}}{{{2 * k + 1}}}S_{{ABC}}=\\frac{{{k + 1}}}{{{2 * k + 1}}}\\cdot\\frac12\\cdot {tx(b)}\\cdot {tx(bc)}={tx(s)}.$$')

    def figure(self, p):
        b, k, m, ad, bc, s = (float(x) for x in self._v(p))
        A, B, D, C, M = (0.0, 0.0), (0.0, b), (ad, 0.0), (bc, b), (m, b)
        Ov = g.intersect(A, C, B, D)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'M': M, 'O': Ov}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('A', 'C'), ('B', 'D'), ('A', 'M')], circles=[((ad / 2, 0.0), ad / 2)], dots=['M', 'O'])

    def sample(self, rng):
        k = rng.choice([2, 3, 4])
        return dict(b=rng.choice(['sqrt(10)', '2', '3', 'sqrt(6)', '2*sqrt(3)', '4', 'sqrt(2)']), k=k)


class TriangleMedianBisector(Solved):
    """∠C = 30°, AM — медиана и биссектриса угла CAH ⇒ треугольник прямоугольный; площадь CMF"""
    number, topic = 17, TRI
    fipi = {'e6Ac01': dict(c=8)}

    def answer(self, p):
        c = sp.Integer(p['c'])
        return Answer.num(S(3) * c ** 2 / 4)

    def check(self, p):
        c = float(p['c'])
        B, C = (0.0, 0.0), (2 * c, 0.0)
        A = g.polar(c, 60)
        H, M = g.foot(A, B, C), g.mid(B, C)
        assert g.close(g.angle(H, A, M), g.angle(M, A, C)) and g.close(g.angle(B, A, C), 90)
        Q = g.foot(M, A, C)
        F = g.intersect(A, H, M, Q)
        return g.area(C, M, F)

    def condition(self, p):
        return ('В треугольнике $ABC$ угол $ACB$ равен $30^\\circ$, отрезки $AH$ и $AM$ — высота и медиана, причём точка $H$ лежит на отрезке $BM$. '
                'Отрезок $MQ$ — высота треугольника $AMC$, прямые $AH$ и $MQ$ пересекаются в точке $F$. Луч $AM$ — биссектриса угла $CAH$.\n\n'
                f'а) Докажите, что треугольник $ABC$ прямоугольный.\n\nб) Найдите площадь треугольника $CMF$, если $AB={p["c"]}$.')

    def solution(self, p):
        c = sp.Integer(p['c'])
        return (
            'а) В прямоугольном треугольнике $AHC$: $\\angle HAC=90^\\circ-30^\\circ=60^\\circ$, биссектриса $AM$ делит его пополам: '
            '$\\angle MAC=30^\\circ=\\angle C$. Значит, $MA=MC=MB$, и точка $A$ лежит на окружности с диаметром $BC$: $\\angle BAC=90^\\circ$.\n\n'
            f'б) $\\angle B=60^\\circ$, $BC=2AB={2 * c}$, $MA=MC={c}$. Треугольник $AMC$ равнобедренный, его высота $MQ$ — медиана: $Q$ — середина $AC$. '
            f'Введём координаты: $B(0;0)$, $C({2 * c};0)$, $A\\left({tx(c / 2)};{tx(c * S(3) / 2)}\\right)$, $H\\left({tx(c / 2)};0\\right)$, '
            f'$M({c};0)$, $Q\\left({tx(5 * c / 4)};{tx(c * S(3) / 4)}\\right)$. Прямая $MQ$ пересекает прямую $x={tx(c / 2)}$ в точке '
            f'$F\\left({tx(c / 2)};{tx(-c * S(3) / 2)}\\right)$.\n\n'
            f'$$S_{{CMF}}=\\frac12\\cdot CM\\cdot|y_F|=\\frac12\\cdot {c}\\cdot {tx(c * S(3) / 2)}={tx(S(3) * c ** 2 / 4)}.$$')

    def figure(self, p):
        c = 1.0
        B, C = (0.0, 0.0), (2.0, 0.0)
        A = g.polar(c, 60)
        H, M = g.foot(A, B, C), g.mid(B, C)
        Q = g.foot(M, A, C)
        F = g.intersect(A, H, M, Q)
        return g.draw({'A': A, 'B': B, 'C': C, 'H': H, 'M': M, 'Q': Q, 'F': F}, polygons=[['A', 'B', 'C']],
                      segments=[('A', 'H'), ('A', 'M'), ('M', 'Q'), ('H', 'F'), ('M', 'F'), ('C', 'F')], dots=['H', 'M', 'Q', 'F'])

    def sample(self, rng):
        return dict(c=rng.choice([2, 4, 6, 10, 12, 4 * rng.randint(1, 5)]))


class EqualChordsTrapezoid(Solved):
    """Окружность высекает на сторонах трапеции равные хорды: биссектрисы пересекаются в O; высота по отрезкам на боковой стороне"""
    number, topic = 17, CIRC
    fipi = {'D9D771': dict(ak=15, kl=6, lb=5)}

    def answer(self, p):
        at = sp.Integer(p['ak']) + sp.Rational(p['kl'], 2)
        bt = sp.Integer(p['lb']) + sp.Rational(p['kl'], 2)
        return Answer.num(simp(2 * S(at * bt)))

    def check(self, p):
        at = p['ak'] + p['kl'] / 2
        bt = p['lb'] + p['kl'] / 2
        rho = math.sqrt(at * bt)
        # боковая сторона касается вписанной окружности (O, ρ) в T; A и B на касательной, ∠AOB = 90°
        O = (0.0, 0.0)
        T = (rho, 0.0)
        A, B = (rho, -at), (rho, bt)
        assert g.close(g.angle(A, O, B), 90)
        return 2 * rho

    def condition(self, p):
        return ('Окружность с центром $O$ высекает на всех сторонах трапеции $ABCD$ равные хорды.\n\n'
                'а) Докажите, что биссектрисы всех углов трапеции пересекаются в одной точке.\n\n'
                f'б) Найдите высоту трапеции, если окружность пересекает боковую сторону $AB$ в точках $K$ и $L$ так, что $AK={p["ak"]}$, '
                f'$KL={p["kl"]}$, $LB={p["lb"]}$.')

    def solution(self, p):
        at = sp.Integer(p['ak']) + sp.Rational(p['kl'], 2)
        bt = sp.Integer(p['lb']) + sp.Rational(p['kl'], 2)
        return (
            'а) Равные хорды окружности равноудалены от центра, поэтому $O$ находится на одном расстоянии $\\rho$ от всех четырёх сторон. '
            'Точка, равноудалённая от сторон угла и лежащая внутри него, лежит на его биссектрисе, значит, $O$ лежит на биссектрисах всех углов '
            'трапеции (и это центр вписанной в трапецию окружности радиуса $\\rho$).\n\n'
            f'б) Основание $T$ перпендикуляра из $O$ на $AB$ — середина хорды $KL$ и точка касания вписанной окружности: '
            f'$AT={p["ak"]}+{tx(sp.Rational(p["kl"], 2))}={tx(at)}$, $BT={tx(bt)}$. Углы $A$ и $B$ трапеции в сумме дают $180^\\circ$, их '
            'биссектрисы пересекаются под прямым углом: $\\angle AOB=90^\\circ$, и $OT$ — высота прямоугольного треугольника $AOB$: '
            f'$\\rho^2=AT\\cdot BT={tx(at * bt)}$.\n\n$$h=2\\rho={tx(simp(2 * S(at * bt)))}.$$')

    def figure(self, p):
        at, bt = p['ak'] + p['kl'] / 2, p['lb'] + p['kl'] / 2
        rho = math.sqrt(at * bt)
        # описанная трапеция: AD — касательная y = −ρ, BC — касательная y = ρ; ∠AOT: tg = AT/ρ
        phi = math.degrees(math.atan2(at, rho))           # ∠AOT = ∠AOA', A' — точка касания на AD
        T = g.polar(rho, -90 - 2 * phi)                     # точка касания на AB (левая сторона)
        tang = g.add(T, (-T[1], T[0]))
        A = g.intersect(T, tang, (0.0, -rho), (1.0, -rho))
        B = g.intersect(T, tang, (0.0, rho), (1.0, rho))
        T2 = g.polar(rho, -90 + 2 * math.degrees(math.atan2(rho * 1.3, rho)))   # правая боковая сторона — произвольная касательная
        tang2 = g.add(T2, (-T2[1], T2[0]))
        D = g.intersect(T2, tang2, (0.0, -rho), (1.0, -rho))
        C = g.intersect(T2, tang2, (0.0, rho), (1.0, rho))
        K, L = g.lerp(A, B, p['ak'] / (p['ak'] + p['kl'] + p['lb'])), g.lerp(A, B, (p['ak'] + p['kl']) / (p['ak'] + p['kl'] + p['lb']))
        R = g.dist((0.0, 0.0), K)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'O': (0.0, 0.0), 'K': K, 'L': L}, polygons=[['A', 'B', 'C', 'D']],
                      circles=[((0.0, 0.0), R)], dots=['O', 'K', 'L'])

    def sample(self, rng):
        for _ in range(60):
            kl = 2 * rng.randint(1, 4)
            ak, lb = rng.randint(1, 20), rng.randint(1, 20)
            v = (ak + kl // 2) * (lb + kl // 2)
            if int(math.isqrt(v)) ** 2 == v:
                return dict(ak=ak, kl=kl, lb=lb)
        return None


class AltitudeBisectorCircle(Solved):
    """Продолжения высоты CC₁ и биссектрисы BB₁ пересекают описанную окружность в N и M: BM = CN; площадь BDN"""
    number, topic = 17, CIRC
    fipi = {'54E571': dict(bh=6)}

    def answer(self, p):
        return Answer.num(sp.Integer(p['bh']) ** 2)

    def check(self, p):
        # дуги: A — 0°, N — 70°, B — 170°, C — 280°, M — 320° (∠B = 40°, ∠C = 85°)
        A, N, B, C, M = (g.polar(1.0, t) for t in (0, 70, 170, 280, 320))
        assert g.close(g.angle(A, B, C), 40) and g.close(g.angle(A, C, B), 85)
        assert g.perpendicular(g.sub(N, C), g.sub(B, A)) and g.close(g.angle(A, B, M), g.angle(M, B, C))
        assert g.close(g.dist(B, M), g.dist(C, N))
        D = g.intersect(B, C, M, N)
        k = p['bh'] / g.dist_line(B, D, N)
        return g.area(B, D, N) * k * k

    def condition(self, p):
        return ('В треугольнике $ABC$ продолжения высоты $CC_1$ и биссектрисы $BB_1$ пересекают описанную окружность в точках $N$ и $M$ '
                'соответственно, $\\angle ABC=40^\\circ$, $\\angle ACB=85^\\circ$.\n\nа) Докажите, что $BM=CN$.\n\n'
                f'б) Прямые $BC$ и $MN$ пересекаются в точке $D$. Найдите площадь треугольника $BDN$, если его высота $BH$ равна ${p["bh"]}$.')

    def solution(self, p):
        bh = sp.Integer(p['bh'])
        return (
            'а) $\\angle A=180^\\circ-40^\\circ-85^\\circ=55^\\circ$. Найдём дуги описанной окружности (вписанный угол равен половине дуги): '
            '$\\smile BC=110^\\circ$, $\\smile CA=80^\\circ$, $\\smile AB=170^\\circ$ (дуги, не содержащие третьей вершины). $M$ — середина дуги $AC$ '
            '(биссектриса угла $B$): $\\smile AM=\\smile MC=40^\\circ$. Прямая $CN\\perp AB$, поэтому $\\angle ACN=90^\\circ-\\angle A=35^\\circ$ '
            'и $\\smile AN=70^\\circ$ ($N$ на дуге $AB$, не содержащей $C$), $\\smile NB=100^\\circ$.\n\n'
            'Хорда $BM$ стягивает дугу $\\smile BC+\\smile CM=150^\\circ$, хорда $CN$ — дугу $\\smile CA+\\smile AN=150^\\circ$. Равные дуги — '
            'равные хорды: $BM=CN$.\n\n'
            'б) $\\angle NBD=\\angle NBC$ опирается на дугу $NAC$ в $150^\\circ$: $\\angle NBC=75^\\circ$; $\\angle BNM$ опирается на дугу $BCM$ '
            'в $150^\\circ$: $75^\\circ$. Угол между секущими $DB$ и $DN$ равен полуразности дуг: $\\angle D=\\frac{100^\\circ-40^\\circ}{2}=30^\\circ$. '
            'Итак, в треугольнике $BDN$ углы при $B$ и $N$ равны $75^\\circ$, $DB=DN$, а $BH=BD\\sin30^\\circ$: '
            f'$DN=BD=2BH={2 * bh}$.\n\n$$S_{{BDN}}=\\frac12\\cdot DN\\cdot BH=\\frac12\\cdot {2 * bh}\\cdot {bh}={bh ** 2}.$$')

    def figure(self, p):
        A, N, B, C, M = (g.polar(1.0, t) for t in (0, 70, 170, 280, 320))
        D = g.intersect(B, C, M, N)
        C1, B1 = g.foot(C, A, B), g.intersect(B, M, A, C)
        return g.draw({'A': A, 'B': B, 'C': C, 'N': N, 'M': M, 'D': D, 'C1': C1, 'B1': B1}, polygons=[['A', 'B', 'C']],
                      segments=[('C', 'N'), ('B', 'M'), ('C', 'D'), ('M', 'D')], circles=[((0.0, 0.0), 1.0)], dots=['N', 'M', 'D', 'C1', 'B1'])

    def sample(self, rng):
        return dict(bh=rng.choice([2, 3, 4, 5, 7, 8, 10]))


class EquilateralFold(Solved):
    """Серединный перпендикуляр к BM в правильном треугольнике: AEM ~ CMK; отношения площадей и отрезков"""
    number, topic = 17, TRI
    fipi = {'B5D2B2': dict(ask='AM:MC', s1=4, s2=9), 'F2A2EB': dict(ask='S', p=1, q=4)}

    def _pq(self, p):
        if p['ask'] == 'S':
            return sp.Integer(p['p']), sp.Integer(p['q'])
        k = S(sp.Rational(p['s1'], p['s2']))
        # (2p + q) / (p + 2q) = k  ⇒  p(2 − k) = q(2k − 1)
        pp, q = 2 * k - 1, 2 - k
        x = sp.nsimplify(pp / q)
        return x.p, x.q

    def answer(self, p):
        pp, q = self._pq(p)
        if p['ask'] == 'AM:MC':
            return Answer.ratio(pp, q)
        k = sp.Rational(2 * pp + q, pp + 2 * q)
        return Answer.ratio(k ** 2, 1)

    def check(self, p):
        pp, q = (int(x) for x in self._pq(p))
        A, B, C = (0.0, 0.0), g.polar(1.0, 60), (1.0, 0.0)
        M = g.ratio(A, C, pp, q)
        mid = g.mid(B, M)
        d = g.sub(M, B)
        perp = g.add(mid, (-d[1], d[0]))
        E, K = g.intersect(mid, perp, A, B), g.intersect(mid, perp, B, C)
        assert g.close(g.angle(A, E, M), g.angle(C, M, K))
        s1, s2 = g.area(A, E, M), g.area(C, M, K)
        if p['ask'] == 'AM:MC':
            assert g.close(s1 / s2, p['s1'] / p['s2'])
            return g.dist(A, M) / g.dist(M, C)
        return s1 / s2

    def condition(self, p):
        if p['ask'] == 'AM:MC':
            return ('На стороне $AC$ правильного треугольника $ABC$ отмечена точка $M$. Серединный перпендикуляр к отрезку $BM$ пересекает '
                    'стороны $AB$ и $BC$ в точках $E$ и $K$.\n\nа) Докажите, что треугольники $AEM$ и $CMK$ подобны.\n\n'
                    f'б) Найдите отношение $AM:MC$, если площади треугольников $AEM$ и $CMK$ равны ${p["s1"]}$ и ${p["s2"]}$.')
        return ('На стороне $AC$ правильного треугольника $ABC$ отмечена точка $M$. Серединный перпендикуляр к отрезку $BM$ пересекает '
                'стороны $AB$ и $BC$ в точках $E$ и $K$.\n\nа) Докажите, что $\\angle AEM=\\angle CMK$.\n\n'
                f'б) Найдите отношение площадей треугольников $AEM$ и $CMK$, если $AM:MC={p["p"]}:{p["q"]}$.')

    def solution(self, p):
        pp, q = self._pq(p)
        t = ('а) $E$ и $K$ лежат на серединном перпендикуляре к $BM$, поэтому $EM=EB$, $KM=KB$, и треугольники $EMK$ и $EBK$ равны: '
             '$\\angle EMK=\\angle EBK=60^\\circ$. Тогда $\\angle AME+\\angle CMK=180^\\circ-60^\\circ=120^\\circ$, а в треугольнике $AEM$ '
             '$\\angle AME+\\angle AEM=180^\\circ-60^\\circ=120^\\circ$. Значит, $\\angle AEM=\\angle CMK$, и (так как $\\angle A=\\angle C=60^\\circ$) '
             'треугольники $AEM$ и $CMK$ подобны.\n\n'
             'б) Пусть сторона треугольника $a$. Периметр треугольника $AEM$: $AE+EM+AM=AE+EB+AM=a+AM$; периметр $CMK$: $CM+MK+KC=CM+KB+KC=a+CM$. '
             'Отношение периметров подобных треугольников равно коэффициенту подобия $k$: $k=\\frac{a+AM}{a+CM}$.\n\n')
        if p['ask'] == 'AM:MC':
            k = S(sp.Rational(p['s1'], p['s2']))
            return t + (f'$k^2=\\frac{{{p["s1"]}}}{{{p["s2"]}}}$, $k={tx(k)}$. Пусть $AM=x$, $CM=a-x$: '
                        f'$\\frac{{a+x}}{{2a-x}}={tx(k)}$, откуда $x={tx(sp.nsimplify((2 * k - 1) / (1 + k)))}a$. '
                        f'$AM:MC={self.answer(p).display.strip("$")}$.')
        k = sp.Rational(2 * pp + q, pp + 2 * q)
        return t + (f'$AM=\\frac{{{pp}}}{{{pp + q}}}a$, $CM=\\frac{{{q}}}{{{pp + q}}}a$, $k=\\frac{{{pp + q}+{pp}}}{{{pp + q}+{q}}}={tx(k)}$. '
                    f'Отношение площадей $k^2={tx(k ** 2)}$, то есть {self.answer(p).display}.')

    def figure(self, p):
        pp, q = (int(x) for x in self._pq(p))
        A, B, C = (0.0, 0.0), g.polar(1.0, 60), (1.0, 0.0)
        M = g.ratio(A, C, pp, q)
        mid = g.mid(B, M)
        d = g.sub(M, B)
        perp = g.add(mid, (-d[1], d[0]))
        E, K = g.intersect(mid, perp, A, B), g.intersect(mid, perp, B, C)
        return g.draw({'A': A, 'B': B, 'C': C, 'M': M, 'E': E, 'K': K}, polygons=[['A', 'B', 'C']],
                      segments=[('E', 'K'), ('E', 'M'), ('K', 'M')], dashed=[('B', 'M')], dots=['M', 'E', 'K'])

    def sample(self, rng):
        pp, q = rng.choice([(1, 4), (1, 2), (2, 1), (1, 3), (3, 1), (2, 3), (1, 1)])
        if rng.random() < 0.5:
            return dict(ask='S', p=pp, q=q)
        k = sp.Rational(2 * pp + q, pp + 2 * q)
        return dict(ask='AM:MC', s1=int((k ** 2).p), s2=int((k ** 2).q))


class PentagonParallelogram(Solved):
    """Вписанный пятиугольник, BCDM — параллелограмм: BC = DE; найти AB по отрезкам хорд"""
    number, topic = 17, CIRC
    fipi = {'AC39B7': dict(de=4, ad=7, be=8)}

    def _v(self, p):
        de, ad, be = (sp.Integer(p[k]) for k in ('de', 'ad', 'be'))
        am = ad - de
        x = sp.symbols('x')
        roots = sorted(sp.solve(x * (be - x) - am * de, x))
        return am, roots, max(rt for rt in roots if rt > de)

    def answer(self, p):
        return Answer.num(self._v(p)[2])

    def check(self, p):
        am, roots, ab = self._v(p)
        de, be = float(p['de']), float(p['be'])
        a = float(am)
        found = None
        for bm in (float(x) for x in roots):
            me = be - bm
            M = (0.0, 0.0)
            A, D = (-a, 0.0), (de, 0.0)

            def gap(th):
                u = g.polar(1.0, th)
                B, E = g.mul(u, -bm), g.mul(u, me)
                C = g.add(B, g.sub(D, M))
                O = g.circumcenter(A, B, D)
                return g.dist(O, C) - g.dist(O, A), B, C, E
            lo, hi = 1.0, 179.0
            ok = False
            for i in range(200):
                mid = (lo + hi) / 2
                if gap(lo)[0] * gap(mid)[0] <= 0:
                    hi, ok = mid, True
                else:
                    lo = mid
            if not ok or abs(gap(lo)[0]) > 1e-6:
                continue
            _, B, C, E = gap(lo)
            if g.close(g.dist(B, C), de) and g.dist(A, B) > g.dist(B, C):
                found = g.dist(A, B)
        assert found is not None
        return found

    def condition(self, p):
        return ('Пятиугольник $ABCDE$ вписан в окружность. Диагонали $AD$ и $BE$ пересекаются в точке $M$. Известно, что $BCDM$ — параллелограмм.\n\n'
                'а) Докажите, что $BC=DE$.\n\n'
                f'б) Найдите длину стороны $AB$, если $DE={p["de"]}$, $AD={p["ad"]}$, $BE={p["be"]}$ и $AB>BC$.')

    def solution(self, p):
        am, roots, ab = self._v(p)
        de, ad, be = p['de'], p['ad'], p['be']
        return (
            'а) $BC\\parallel MD$, то есть $BC\\parallel AD$: вписанная трапеция $ABCD$ равнобедренная, $AB=CD$. $CD\\parallel BM$, то есть '
            '$CD\\parallel BE$: вписанная трапеция $BCDE$ равнобедренная, $BC=DE$.\n\n'
            f'б) В параллелограмме $MD=BC=DE={de}$, $BM=CD=AB$. $AM=AD-MD={tx(am)}$. Пусть $BM=x$, $ME={be}-x$. По свойству пересекающихся '
            f'хорд $AM\\cdot MD=BM\\cdot ME$: ${tx(am)}\\cdot {de}=x({be}-x)$, корни $x={tx(roots[0])}$ и $x={tx(roots[1])}$. '
            f'$AB=BM$, и по условию $AB>BC={de}$, поэтому $$AB={tx(ab)}.$$')

    def figure(self, p):
        return None

    def sample(self, rng):
        for _ in range(80):
            de = rng.randint(2, 8)
            am = rng.randint(1, 8)
            x = rng.randint(de + 1, de + 8)
            y = sp.Rational(am * de, x)
            if y.q != 1 or y == x:
                continue
            return dict(de=de, ad=am + de, be=int(x + y))
        return None


class TrapezoidDiagonals(Solved):
    """Сумма оснований и диагонали образуют пифагорову тройку: диагонали перпендикулярны; высота"""
    number, topic = 17, QUAD
    fipi = {'34E1B6': dict(s=13, d1=5, d2=12), '5259A1': dict(s=10, d1=6, d2=8)}

    def answer(self, p):
        return Answer.num(sp.Rational(p['d1'] * p['d2'], p['s']))

    def check(self, p):
        s, d1, d2 = (float(p[k]) for k in ('s', 'd1', 'd2'))
        h = d1 * d2 / s
        # A(0,0), C на высоте h с AC = d1; D на оси, BD = d2
        cx = math.sqrt(d1 * d1 - h * h)
        A, C = (0.0, 0.0), (cx, h)
        bc = 0.3 * s
        B = (cx - bc, h)
        D = (s - bc, 0.0)
        assert g.close(g.dist(B, D), d2) and g.perpendicular(g.sub(C, A), g.sub(D, B))
        return g.dist_line(B, A, D)

    def condition(self, p):
        return (f'Сумма оснований трапеции равна ${p["s"]}$, а её диагонали равны ${p["d1"]}$ и ${p["d2"]}$.\n\n'
                'а) Докажите, что диагонали трапеции перпендикулярны.\n\nб) Найдите высоту трапеции.')

    def solution(self, p):
        s, d1, d2 = p['s'], p['d1'], p['d2']
        return (
            'а) Пусть $ABCD$ — трапеция с основаниями $AD$ и $BC$. Проведём через $C$ прямую, параллельную $BD$, до пересечения с прямой $AD$ '
            'в точке $E$. $BCED$ — параллелограмм: $CE=BD$, $DE=BC$, поэтому $AE=AD+BC$' + f'$={s}$. В треугольнике $ACE$ стороны ${d1}$, '
            f'${d2}$, ${s}$, и ${d1}^2+{d2}^2={s}^2$, значит, $\\angle ACE=90^\\circ$, то есть $AC\\perp CE\\parallel BD$.\n\n'
            f'б) Высота трапеции равна высоте прямоугольного треугольника $ACE$, проведённой к гипотенузе: '
            f'$$h=\\frac{{AC\\cdot CE}}{{AE}}=\\frac{{{d1}\\cdot {d2}}}{{{s}}}={tx(sp.Rational(d1 * d2, s))}.$$')

    def figure(self, p):
        s, d1, d2 = (float(p[k]) for k in ('s', 'd1', 'd2'))
        h = d1 * d2 / s
        cx = math.sqrt(d1 * d1 - h * h)
        bc = 0.3 * s
        A, C, B, D = (0.0, 0.0), (cx, h), (cx - bc, h), (s - bc, 0.0)
        E = (s, 0.0)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'E': E}, polygons=[['A', 'B', 'C', 'D']], segments=[('A', 'C'), ('B', 'D')],
                      dashed=[('C', 'E'), ('D', 'E')])

    def sample(self, rng):
        a, b, c = rng.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15), (7, 24, 25), (12, 16, 20)])
        return dict(s=c, d1=a, d2=b)


class OrthicB1C1(Solved):
    """Высоты BB₁, CC₁: ∠BB₁C₁ = ∠BAH; расстояние от центра описанной окружности до BC по B₁C₁ и углу A"""
    number, topic = 17, TRI
    fipi = {'10D010': dict(m=18, A=30)}

    def answer(self, p):
        return Answer.num(simp(sp.Integer(p['m']) / (2 * sin(p['A']))))

    def check(self, p):
        A_ = p['A']
        Av, Bv, Cv = g.triangle_angles(70, 180 - 70 - A_, 1.0)
        B1, C1 = g.foot(Bv, Av, Cv), g.foot(Cv, Av, Bv)
        k = p['m'] / g.dist(B1, C1)
        H = g.orthocenter(Av, Bv, Cv)
        assert g.close(g.angle(Bv, B1, C1), g.angle(Bv, Av, H))
        O = g.circumcenter(Av, Bv, Cv)
        return g.dist_line(O, Bv, Cv) * k

    def condition(self, p):
        return ('Высоты $BB_1$ и $CC_1$ остроугольного треугольника $ABC$ пересекаются в точке $H$.\n\n'
                'а) Докажите, что $\\angle BB_1C_1=\\angle BAH$.\n\n'
                f'б) Найдите расстояние от центра окружности, описанной около треугольника $ABC$, до стороны $BC$, если $B_1C_1={p["m"]}$ и '
                f'$\\angle BAC={p["A"]}^\\circ$.')

    def solution(self, p):
        m, A = sp.Integer(p['m']), p['A']
        return (
            'а) $\\angle AB_1H=\\angle AC_1H=90^\\circ$, поэтому точки $A$, $C_1$, $H$, $B_1$ лежат на окружности с диаметром $AH$, и вписанные углы '
            '$HB_1C_1$ и $HAC_1$ равны: $\\angle BB_1C_1=\\angle BAH$.\n\n'
            'б) Треугольник $AB_1C_1$ подобен треугольнику $ABC$ с коэффициентом $\\cos A$ ($AB_1=AB\\cos A$, $AC_1=AC\\cos A$, угол общий), '
            f'поэтому $BC=\\frac{{B_1C_1}}{{\\cos A}}$. Радиус описанной окружности $R=\\frac{{BC}}{{2\\sin A}}$, а расстояние от центра до $BC$ '
            '(угол $A$ острый) $d=R\\cos A$:\n\n'
            f'$$d=\\frac{{BC\\cos A}}{{2\\sin A}}=\\frac{{B_1C_1}}{{2\\sin A}}=\\frac{{{m}}}{{2\\sin{A}^\\circ}}={tx(simp(m / (2 * sin(A))))}.$$')

    def figure(self, p):
        A_ = p['A']
        Av, Bv, Cv = g.triangle_angles(70, 180 - 70 - A_, 4.0)
        B1, C1 = g.foot(Bv, Av, Cv), g.foot(Cv, Av, Bv)
        H, O = g.orthocenter(Av, Bv, Cv), g.circumcenter(Av, Bv, Cv)
        return g.draw({'A': Av, 'B': Bv, 'C': Cv, 'B1': B1, 'C1': C1, 'H': H, 'O': O}, polygons=[['A', 'B', 'C']],
                      segments=[('B', 'B1'), ('C', 'C1'), ('B1', 'C1'), ('A', 'H')], dashed=[('O', 'B'), ('O', 'C')], dots=['B1', 'C1', 'H', 'O'])

    def sample(self, rng):
        return dict(m=rng.randint(2, 24), A=rng.choice([30, 45, 60]))


class IncircleTouchesMN(Solved):
    """MN ∥ AC касается вписанной окружности: AB + BC = k·AC; радиус по отрезкам ML и LN"""
    number, topic = 17, CIRC
    fipi = {'7C842B': dict(p=2, q=3, ml='9/5', ln='3')}

    def _v(self, p):
        pp, q = sp.Integer(p['p']), sp.Integer(p['q'])
        ml, ln = sp.Rational(p['ml']), sp.Rational(p['ln'])
        mn = ml + ln
        ac = mn * (pp + q) / q
        s_ = (pp + q) * (mn + ac) / pp          # AB + BC
        d_ = (pp + q) * (ln - ml) / q           # AB − BC
        ab, bc = (s_ + d_) / 2, (s_ - d_) / 2
        per = (ab + bc + ac) / 2
        area = simp(S(per * (per - ab) * (per - bc) * (per - ac)))
        return mn, ac, s_, d_, ab, bc, per, area, simp(area / per)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        mn, ac, s_, d_, ab, bc, per, area, rr = (float(x) for x in self._v(p))
        A, B, C = g.triangle(bc, ac, ab)
        pp, q = p['p'], p['q']
        M, N = g.ratio(A, B, pp, q), g.ratio(C, B, pp, q)
        I = g.incenter(A, B, C)
        rin = g.inradius(A, B, C)
        assert g.close(g.dist_line(I, M, N), rin)
        L = g.foot(I, M, N)
        assert g.close(g.dist(M, L), float(sp.Rational(p['ml']))) and g.close(g.dist(L, N), float(sp.Rational(p['ln'])))
        return rin

    def condition(self, p):
        pp, q = p['p'], p['q']
        k = sp.Rational(pp + 2 * q, pp)
        return (f'В треугольнике $ABC$ точки $M$ и $N$ лежат на сторонах $AB$ и $BC$ так, что $AM:MB=CN:NB={pp}:{q}$. Окружность, вписанная в '
                f'треугольник $ABC$, касается отрезка $MN$ в точке $L$.\n\nа) Докажите, что $AB+BC={tx(k)}AC$.\n\n'
                f'б) Найдите радиус окружности, вписанной в треугольник $ABC$, если $ML={tx(sp.Rational(p["ml"]))}$, $LN={tx(sp.Rational(p["ln"]))}$.')

    def solution(self, p):
        mn, ac, s_, d_, ab, bc, per, area, rr = self._v(p)
        pp, q = p['p'], p['q']
        k = sp.Rational(pp + 2 * q, pp)
        return (
            f'а) $\\frac{{BM}}{{BA}}=\\frac{{BN}}{{BC}}=\\frac{{{q}}}{{{pp + q}}}$, поэтому $MN\\parallel AC$ и $MN=\\frac{{{q}}}{{{pp + q}}}AC$. '
            'Окружность касается всех сторон четырёхугольника $AMNC$, значит, $AM+NC=MN+AC$:\n\n'
            f'$$\\frac{{{pp}}}{{{pp + q}}}(AB+BC)=\\frac{{{q}}}{{{pp + q}}}AC+AC\\ \\Rightarrow\\ AB+BC={tx(k)}AC.$$\n\n'
            f'б) $MN=ML+LN={tx(mn)}$, $AC={tx(ac)}$, $AB+BC={tx(s_)}$. Касательные из $M$ и $N$: $ML$ и $LN$ равны отрезкам от $M$ и $N$ до точек '
            'касания со сторонами $AB$ и $BC$; касательные из $B$ равны: $BM+ML=BN+NL$, то есть '
            f'$\\frac{{{q}}}{{{pp + q}}}(AB-BC)=LN-ML$, $AB-BC={tx(d_)}$. Значит, $AB={tx(ab)}$, $BC={tx(bc)}$.\n\n'
            f'Полупериметр $p={tx(per)}$, по формуле Герона $S={tx(area)}$, $$r=\\frac{{S}}{{p}}={tx(rr)}.$$')

    def figure(self, p):
        mn, ac, s_, d_, ab, bc, per, area, rr = (float(x) for x in self._v(p))
        A, B, C = g.triangle(bc, ac, ab)
        M, N = g.ratio(A, B, p['p'], p['q']), g.ratio(C, B, p['p'], p['q'])
        I = g.incenter(A, B, C)
        L = g.foot(I, M, N)
        return g.draw({'A': A, 'B': B, 'C': C, 'M': M, 'N': N, 'L': L}, polygons=[['A', 'B', 'C']], segments=[('M', 'N')],
                      circles=[(I, rr)], dots=['M', 'N', 'L'])

    def sample(self, rng):
        # касание MN равносильно p(AB + BC) = (p + 2q)·AC; разность AB − BC задаём сами
        pp, q = rng.choice([(2, 3), (1, 2), (1, 3), (2, 5), (3, 4), (1, 1)])
        ac = rng.randint(2, 12) * pp
        s_ = sp.Rational(ac * (pp + 2 * q), pp)
        d_ = rng.randint(0, ac - 1) * rng.choice([1, -1])
        mn = sp.Rational(q * ac, pp + q)
        diff = sp.Rational(q * d_, pp + q)               # LN − ML
        ml, ln = (mn - diff) / 2, (mn + diff) / 2
        if ml <= 0 or ln <= 0 or abs(d_) >= ac:
            return None
        return dict(p=pp, q=q, ml=str(ml), ln=str(ln))


class ParallelogramBisectorL(Solved):
    """∠BAC = 2∠CAD, AL — биссектриса: AL·BC = AB·AC; найти EL, где AE = CE"""
    number, topic = 17, QUAD
    fipi = {'FC6FD7': dict(ac=8, t='1/2')}

    def answer(self, p):
        a, t = sp.Integer(p['ac']), sp.Rational(p['t'])
        return Answer.num(a / 2 * (t + 2 * t / (1 - t ** 2)))

    def check(self, p):
        a, t = float(p['ac']), float(sp.Rational(p['t']))
        phi = math.degrees(math.atan(t))
        A, C = (0.0, 0.0), (a, 0.0)
        B = g.intersect(A, g.polar(1.0, 2 * phi), C, g.add(C, g.polar(1.0, 180 - phi)))
        D = g.add(A, g.sub(C, B))
        L = g.intersect(A, g.polar(1.0, phi), B, C)
        assert g.close(g.dist(A, L) * g.dist(B, C), g.dist(A, B) * g.dist(A, C))
        E = g.intersect(C, D, (a / 2, 0.0), (a / 2, 1.0))
        assert g.dist(C, E) > g.dist(C, D)
        return g.dist(E, L)

    def condition(self, p):
        return ('В параллелограмме $ABCD$ угол $BAC$ вдвое больше угла $CAD$. Биссектриса угла $BAC$ пересекает отрезок $BC$ в точке $L$. '
                'На продолжении стороны $CD$ за точку $D$ выбрана такая точка $E$, что $AE=CE$.\n\n'
                'а) Докажите, что $AL\\cdot BC=AB\\cdot AC$.\n\n'
                f'б) Найдите $EL$, если $AC={p["ac"]}$, $\\operatorname{{tg}}\\angle BCA={tx(sp.Rational(p["t"]))}$.')

    def solution(self, p):
        a, t = sp.Integer(p['ac']), sp.Rational(p['t'])
        t2 = 2 * t / (1 - t ** 2)
        return (
            'а) Пусть $\\varphi=\\angle CAD=\\angle BCA$ (накрест лежащие). Тогда $\\angle BAL=\\angle LAC=\\varphi=\\angle BCA$. Треугольники '
            '$ABL$ и $CBA$ подобны (общий угол $B$, $\\angle BAL=\\angle BCA$): $\\frac{AL}{CA}=\\frac{AB}{CB}$, то есть $AL\\cdot BC=AB\\cdot AC$.\n\n'
            'б) В треугольнике $ALC$ $\\angle LAC=\\angle LCA=\\varphi$, поэтому $LA=LC$ и $L$ лежит на серединном перпендикуляре к $AC$. '
            'Точка $E$ ($AE=CE$) тоже на нём, так что $EL\\perp AC$ и проходит через середину $P$ отрезка $AC$ (точки $L$ и $E$ — по разные '
            f'стороны от $AC$). $LP=PC\\operatorname{{tg}}\\varphi={tx(a / 2)}\\cdot {tx(t)}={tx(a / 2 * t)}$. Угол $PCE$ — это $\\angle ACD=\\angle BAC=2\\varphi$ '
            f'(накрест лежащие при $AB\\parallel CD$), $\\operatorname{{tg}}2\\varphi=\\frac{{2\\operatorname{{tg}}\\varphi}}{{1-\\operatorname{{tg}}^2\\varphi}}={tx(t2)}$, '
            f'$PE=PC\\operatorname{{tg}}2\\varphi={tx(a / 2 * t2)}$.\n\n$$EL=LP+PE={tx(a / 2 * (t + t2))}.$$')

    def figure(self, p):
        a, t = 4.0, float(sp.Rational(p['t']))
        phi = math.degrees(math.atan(t))
        A, C = (0.0, 0.0), (a, 0.0)
        B = g.intersect(A, g.polar(1.0, 2 * phi), C, g.add(C, g.polar(1.0, 180 - phi)))
        D = g.add(A, g.sub(C, B))
        L = g.intersect(A, g.polar(1.0, phi), B, C)
        E = g.intersect(C, D, (a / 2, 0.0), (a / 2, 1.0))
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'L': L, 'E': E}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('A', 'C'), ('A', 'L'), ('D', 'E'), ('A', 'E')], dashed=[('E', 'L')], dots=['L', 'E'])

    def sample(self, rng):
        t = rng.choice(['1/2', '1/3', '1/4', '2/3', '1/5'])
        return dict(ac=rng.choice([4, 6, 8, 10, 12, 15, 16]), t=t)


class DoubleAngle(Solved):
    """∠A = 2∠B, окружность AOC пересекает BC в P: AP = BP, PAC ~ ABC, a² = b(b + c)"""
    number, topic = 17, CIRC
    fipi = {'0e9DD3': dict(ask='BC', c=7, b=4), '16DDDD': dict(ask='AB', b=2, a='sqrt(10)')}

    def answer(self, p):
        b = sp.Integer(p['b'])
        if p['ask'] == 'BC':
            return Answer.num(simp(S(b * (b + p['c']))))
        a = sp.sympify(p['a'])
        return Answer.num(simp(a ** 2 / b - b))

    def check(self, p):
        b = float(p['b'])
        if p['ask'] == 'BC':
            c = float(p['c'])
            a = float(self.answer(p).value)
        else:
            a = f(p['a'])
            c = float(self.answer(p).value)
        A, B, C = g.triangle(a, b, c)
        assert g.close(g.angle(B, A, C), 2 * g.angle(A, B, C)) and max(g.angle(B, A, C), g.angle(A, B, C), g.angle(A, C, B)) < 90
        O = g.circumcenter(A, B, C)
        O2 = g.circumcenter(A, O, C)
        P = g.second(B, C, O2, g.dist(O2, A), C)
        assert g.close(g.dist(A, P), g.dist(B, P))
        return a if p['ask'] == 'BC' else c

    def condition(self, p):
        if p['ask'] == 'BC':
            return ('В остроугольном треугольнике $ABC$ угол $BAC$ в два раза больше угла $ABC$. Точка $O$ — центр окружности, описанной около '
                    'треугольника $ABC$. Окружность, описанная около треугольника $AOC$, пересекает отрезок $BC$ в точках $C$ и $P$.\n\n'
                    f'а) Докажите, что $AP=BP$.\n\nб) Найдите длину стороны $BC$, если $AB={p["c"]}$, $AC={p["b"]}$.')
        return ('В остроугольном треугольнике $ABC$ угол $BAC$ в два раза больше угла $ABC$. Точка $O$ — центр окружности, описанной около '
                'треугольника $ABC$. Окружность, описанная около треугольника $AOC$, пересекает отрезок $BC$ в точках $C$ и $P$.\n\n'
                f'а) Докажите, что треугольники $PAC$ и $ABC$ подобны.\n\nб) Найдите длину стороны $AB$, если $AC={p["b"]}$, '
                f'$BC={tx(sp.sympify(p["a"]))}$.')

    def solution(self, p):
        t = ('а) Центральный угол $AOC=2\\angle ABC$. Точки $A$, $O$, $P$, $C$ лежат на одной окружности, $P$ и $O$ — по одну сторону от $AC$, '
             'поэтому $\\angle APC=\\angle AOC=2\\angle B$. $\\angle APC$ — внешний угол треугольника $ABP$: $\\angle APC=\\angle B+\\angle BAP$, '
             'откуда $\\angle BAP=\\angle B$ и $AP=BP$. Кроме того, $\\angle PAC=\\angle A-\\angle BAP=2\\angle B-\\angle B=\\angle B$, и треугольники '
             '$CAP$ и $CBA$ подобны (общий угол $C$, $\\angle CAP=\\angle CBA$).\n\n'
             'б) Обозначим $a=BC$, $b=AC$, $c=AB$. Из подобия $\\frac{CP}{CA}=\\frac{CA}{CB}$: $CP=\\frac{b^2}{a}$, и $\\frac{AP}{BA}=\\frac{CA}{CB}$: '
             '$AP=\\frac{bc}{a}$. Но $AP=BP=a-\\frac{b^2}{a}$, поэтому $a^2-b^2=bc$, то есть $a^2=b(b+c)$.\n\n')
        b = sp.Integer(p['b'])
        if p['ask'] == 'BC':
            return t + f'$$BC=\\sqrt{{{b}\\cdot({b}+{p["c"]})}}={self.answer(p).display.strip("$")}.$$'
        a = sp.sympify(p['a'])
        return t + f'${tx(a ** 2)}={b}({b}+c)$, $$AB=c={self.answer(p).display.strip("$")}.$$'

    def figure(self, p):
        b = float(p['b'])
        a, c = (float(self.answer(p).value), float(p['c'])) if p['ask'] == 'BC' else (f(p['a']), float(self.answer(p).value))
        A, B, C = g.triangle(a, b, c)
        O = g.circumcenter(A, B, C)
        O2 = g.circumcenter(A, O, C)
        P = g.second(B, C, O2, g.dist(O2, A), C)
        return g.draw({'A': A, 'B': B, 'C': C, 'O': O, 'P': P}, polygons=[['A', 'B', 'C']], segments=[('A', 'P'), ('A', 'O'), ('O', 'C')],
                      circles=[(O2, g.dist(O2, A))], dots=['O', 'P'])

    def sample(self, rng):
        for _ in range(60):
            b, c = rng.randint(2, 12), rng.randint(2, 15)
            a2 = b * (b + c)
            if c * c < a2 + b * b and a2 < b * b + c * c and b < c:
                if rng.random() < 0.5:
                    return dict(ask='BC', c=c, b=b)
                return dict(ask='AB', b=b, a=str(simp(S(a2))))
        return None


class RightTriangleRotation(Solved):
    """CM = BC, CN = AC: треугольник NCM — поворот ACB на 90°; медианы перпендикулярны; найти KL"""
    number, topic = 17, TRI
    fipi = {'EF3DDA': dict(a=1, b=5)}

    def _v(self, p):
        a, b = sp.Integer(p['a']), sp.Integer(p['b'])
        x = sp.symbols('x')
        # C(0;0), B(a;0), A(0;b), M(0;a), N(−b;0)
        # K = MN ∩ AB: MN: y = a + a·x/b ; AB: y = b − b·x/a
        kx = sp.solve(sp.Eq(a + a * x / b, b - b * x / a), x)[0]
        K = (kx, a + a * kx / b)
        # L = BM ∩ AN: BM: x/a + y/a = 1 ; AN: y = b + x
        lx = sp.solve(sp.Eq(a - x, b + x), x)[0]
        L = (lx, a - lx)
        kl = simp(S((K[0] - L[0]) ** 2 + (K[1] - L[1]) ** 2))
        return a, b, K, L, kl

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        a, b = float(p['a']), float(p['b'])
        C, B, A = (0.0, 0.0), (a, 0.0), (0.0, b)
        M, N = (0.0, a), (-b, 0.0)
        P, Q = g.mid(A, B), g.mid(N, M)
        assert g.perpendicular(P, Q)
        K = g.intersect(M, N, A, B)
        L = g.intersect(B, M, A, N)
        return g.dist(K, L)

    def condition(self, p):
        return ('В прямоугольном треугольнике $ABC$ точка $M$ лежит на катете $AC$, а точка $N$ — на продолжении катета $BC$ за точку $C$, '
                'причём $CM=BC$ и $CN=AC$.\n\nа) Отрезки $CP$ и $CQ$ — медианы треугольников $ABC$ и $NCM$. Докажите, что прямые $CP$ и $CQ$ '
                'перпендикулярны.\n\nб) Прямые $MN$ и $AB$ пересекаются в точке $K$, а прямые $BM$ и $AN$ — в точке $L$. Найдите $KL$, если '
                f'$BC={p["a"]}$, а $AC={p["b"]}$.')

    def solution(self, p):
        a, b, K, L, kl = self._v(p)
        return (
            'а) Поворот вокруг $C$ на $90^\\circ$, переводящий луч $CA$ в луч $CN$, переводит луч $CB$ в луч $CM$ (они перпендикулярны и '
            'расположены так же), а с учётом $CN=CA$, $CM=CB$ — точку $A$ в $N$ и $B$ в $M$. Значит, отрезок $AB$ переходит в $NM$, его '
            'середина $P$ — в середину $Q$, и $CQ$ получается из $CP$ поворотом на $90^\\circ$: $CP\\perp CQ$.\n\n'
            f'б) Введём координаты: $C(0;0)$, $B({a};0)$, $A(0;{b})$, $M(0;{a})$, $N(-{b};0)$. Прямая $MN$: $y={a}+\\frac{{{a}}}{{{b}}}x$, прямая '
            f'$AB$: $y={b}-\\frac{{{b}}}{{{a}}}x$; $K\\left({tx(K[0])};{tx(K[1])}\\right)$. Прямая $BM$: $x+y={a}$, прямая $AN$: $y=x+{b}$; '
            f'$L\\left({tx(L[0])};{tx(L[1])}\\right)$.\n\n$$KL=\\sqrt{{\\left({tx(K[0] - L[0])}\\right)^2+\\left({tx(K[1] - L[1])}\\right)^2}}={tx(kl)}.$$')

    def figure(self, p):
        a, b = float(p['a']), float(p['b'])
        C, B, A, M, N = (0.0, 0.0), (a, 0.0), (0.0, b), (0.0, a), (-b, 0.0)
        K, L = g.intersect(M, N, A, B), g.intersect(B, M, A, N)
        return g.draw({'A': A, 'B': B, 'C': C, 'M': M, 'N': N, 'K': K, 'L': L}, polygons=[['A', 'B', 'C'], ['N', 'C', 'M']],
                      segments=[('M', 'K'), ('B', 'L'), ('A', 'N')], dots=['M', 'N', 'K', 'L'])

    def sample(self, rng):
        a = rng.randint(1, 5)
        return dict(a=a, b=rng.randint(a + 1, a + 6))


class PentagonEqualSides(Solved):
    """Вписанный пятиугольник: AB = CD, BC = DE ⇒ AC = CE; BE по теореме Птолемея"""
    number, topic = 17, CIRC
    fipi = {'D8C152': dict(p=3, q=4, d=6)}

    def answer(self, p):
        pp, q, d = (sp.Integer(p[k]) for k in ('p', 'q', 'd'))
        return Answer.num((pp ** 2 + q * d - q ** 2) / pp)

    def check(self, p):
        pp, q, d = (float(p[k]) for k in ('p', 'q', 'd'))

        def arcs(R):
            a = 2 * math.asin(min(1.0, pp / (2 * R)))
            b = 2 * math.asin(min(1.0, q / (2 * R)))
            return a, b
        lo, hi = max(pp, q) / 2 + 1e-9, 1e4
        for _ in range(300):            # радиус, при котором хорда AD (дуга 2α + β) равна d
            mid = (lo + hi) / 2
            a, b = arcs(mid)
            ad = 2 * mid * math.sin((2 * a + b) / 2)
            lo, hi = (mid, hi) if ad < d else (lo, mid)   # AD растёт вместе с R
        R = lo
        a, b = arcs(R)
        assert 2 * a + 2 * b < 2 * math.pi
        pts = [g.polar(R, math.degrees(t)) for t in (0, a, a + b, 2 * a + b, 2 * a + 2 * b)]
        A, B, C, D, E = pts
        assert g.close(g.dist(A, D), d) and g.close(g.dist(A, C), g.dist(C, E))
        return g.dist(B, E)

    def condition(self, p):
        return (f'Пятиугольник $ABCDE$ вписан в окружность. Известно, что $AB=CD={p["p"]}$, $BC=DE={p["q"]}$.\n\n'
                f'а) Докажите, что $AC=CE$.\n\nб) Найдите длину диагонали $BE$, если $AD={p["d"]}$.')

    def solution(self, p):
        pp, q, d = p['p'], p['q'], p['d']
        return (
            'а) Равные хорды стягивают равные дуги: $\\smile AB=\\smile CD$, $\\smile BC=\\smile DE$. Тогда дуги $ABC$ и $CDE$ равны, и '
            'хорды $AC=CE$.\n\n'
            'б) По теореме Птолемея для вписанного четырёхугольника $ABCD$: $AB\\cdot CD+BC\\cdot AD=AC\\cdot BD$, то есть '
            f'$AC\\cdot BD={pp}\\cdot {pp}+{q}\\cdot {d}={pp * pp + q * d}$. Для четырёхугольника $BCDE$: $BC\\cdot DE+CD\\cdot BE=BD\\cdot CE=BD\\cdot AC$:\n\n'
            f'$${q}\\cdot {q}+{pp}\\cdot BE={pp * pp + q * d},\\qquad BE={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        return None

    def sample(self, rng):
        pp, q = rng.randint(2, 6), rng.randint(2, 7)
        d = rng.randint(max(pp, q) + 1, pp + q + pp)
        return dict(p=pp, q=q, d=d)


class IsoscelesCircleCH(Solved):
    """Окружность касается боковых сторон равнобедренного треугольника и высоты CH: ∠AOC = 90°, ∠OAC = 45°"""
    number, topic = 17, CIRC
    fipi = {'D6A053': dict(bo=7, ac=16, ask='area'), '0e3ce7': dict(bo=1, ac=6, ask='BC')}

    def answer(self, p):
        bo, ac = sp.Integer(p['bo']), sp.Integer(p['ac'])
        bd = bo + ac / 2
        if p['ask'] == 'area':
            return Answer.num(ac * bd / 2)
        return Answer.num(simp(S(bd ** 2 + ac ** 2 / 4)))

    def check(self, p):
        bo, ac = float(p['bo']), float(p['ac'])
        bd = bo + ac / 2
        A, C, B = (-ac / 2, 0.0), (ac / 2, 0.0), (0.0, bd)
        H = g.foot(C, A, B)
        O = g.incenter(B, H, C)
        assert g.close(g.dist(O, B), bo) and g.close(g.angle(A, O, C), 90)
        assert g.close(g.dist_line(O, A, B), g.dist_line(O, C, H))
        return g.area(A, B, C) if p['ask'] == 'area' else g.dist(B, C)

    def condition(self, p):
        a = 'а) Докажите, что $\\angle AOC=90^\\circ$.' if p['ask'] == 'area' else 'а) Докажите, что $\\angle OAC=45^\\circ$.'
        b = 'площадь треугольника $ABC$' if p['ask'] == 'area' else 'длину отрезка $BC$'
        return ('Окружность с центром $O$ касается боковых сторон $AB$ и $BC$ равнобедренного остроугольного треугольника $ABC$ и его высоты '
                f'$CH$.\n\n{a}\n\nб) Найдите {b}, если $BO={p["bo"]}$ и $AC={p["ac"]}$.')

    def solution(self, p):
        bo, ac = sp.Integer(p['bo']), sp.Integer(p['ac'])
        bd = bo + ac / 2
        t = ('а) Окружность касается сторон $BH$, $BC$ и $CH$ треугольника $BHC$ и лежит внутри него, то есть это его вписанная окружность: '
             '$O$ лежит на биссектрисах углов $B$ и $C$ треугольника $BHC$. Пусть $\\angle A=\\angle C=\\alpha$. В прямоугольном треугольнике $AHC$ '
             '$\\angle HCA=90^\\circ-\\alpha$, поэтому $\\angle BCH=\\alpha-(90^\\circ-\\alpha)=2\\alpha-90^\\circ$ и '
             '$\\angle OCA=\\frac12\\angle BCH+\\angle HCA=\\alpha-45^\\circ+90^\\circ-\\alpha=45^\\circ$. $O$ лежит на оси симметрии $BD$ '
             'треугольника, поэтому и $\\angle OAC=45^\\circ$, а $\\angle AOC=180^\\circ-90^\\circ=90^\\circ$.\n\n'
             f'б) $D$ — середина $AC$, треугольник $AOD$ прямоугольный равнобедренный: $OD=AD={tx(ac / 2)}$, $BD=BO+OD={tx(bd)}$.\n\n')
        if p['ask'] == 'area':
            return t + f'$$S_{{ABC}}=\\frac12\\cdot AC\\cdot BD=\\frac12\\cdot {ac}\\cdot {tx(bd)}={tx(ac * bd / 2)}.$$'
        return t + f'$$BC=\\sqrt{{BD^2+DC^2}}=\\sqrt{{{tx(bd ** 2)}+{tx(ac ** 2 / 4)}}}={self.answer(p).display.strip("$")}.$$'

    def figure(self, p):
        bo, ac = float(p['bo']), float(p['ac'])
        bd = bo + ac / 2
        A, C, B = (-ac / 2, 0.0), (ac / 2, 0.0), (0.0, bd)
        H = g.foot(C, A, B)
        O = g.incenter(B, H, C)
        return g.draw({'A': A, 'B': B, 'C': C, 'H': H, 'O': O}, polygons=[['A', 'B', 'C']], segments=[('C', 'H'), ('A', 'O'), ('O', 'C')],
                      circles=[(O, g.inradius(B, H, C))], dots=['H', 'O'])

    def sample(self, rng):
        return dict(bo=rng.randint(1, 10), ac=2 * rng.randint(1, 10), ask=rng.choice(['area', 'BC']))


class TangentCirclesTriangle(Solved):
    """Окружности касаются в C, равнобедренный прямоугольный треугольник ABC: AD ∥ BE; найти катет"""
    number, topic = 17, CIRC
    fipi = {'A7A4AB': dict(kind='internal', r1='3', r2='4', ask='AC'), '7E3432': dict(kind='external', r1='sqrt(15)', r2='15', ask='BC')}

    def answer(self, p):
        r1, r2 = sp.sympify(p['r1']), sp.sympify(p['r2'])
        return Answer.num(simp(2 * r1 * r2 / S(r1 ** 2 + r2 ** 2)))

    def _pts(self, p):
        r1, r2 = f(p['r1']), f(p['r2'])
        th = math.atan2(r2, r1)
        C = (0.0, 0.0)
        o1 = (0.0, r1)
        o2 = (0.0, r2) if p['kind'] == 'internal' else (0.0, -r2)
        x = 2 * r1 * math.sin(th)
        A = g.polar(x, math.degrees(th))
        phi = math.degrees(th) + 90 if p['kind'] == 'internal' else math.degrees(th) - 90
        B = g.polar(x, phi)
        return C, o1, o2, r1, r2, A, B

    def check(self, p):
        C, o1, o2, r1, r2, A, B = self._pts(p)
        assert g.close(g.dist(A, o1), r1) and g.close(g.dist(B, o2), r2) and g.close(g.angle(A, C, B), 90)
        E = g.second(A, C, o2, r2, C)
        D = g.second(B, C, o1, r1, C)
        assert g.parallel(g.sub(D, A), g.sub(E, B))
        return g.dist(A, C)

    def condition(self, p):
        kind = 'внутренним' if p['kind'] == 'internal' else 'внешним'
        return (f'Две окружности касаются {kind} образом в точке $C$. Вершины $A$ и $B$ равнобедренного прямоугольного треугольника $ABC$ с прямым '
                'углом $C$ лежат на меньшей и большей окружностях соответственно. Прямая $AC$ вторично пересекает большую окружность в точке $E$, '
                'а прямая $BC$ вторично пересекает меньшую окружность в точке $D$.\n\nа) Докажите, что прямые $AD$ и $BE$ параллельны.\n\n'
                f'б) Найдите ${p["ask"]}$, если радиусы окружностей равны ${tx(sp.sympify(p["r1"]))}$ и ${tx(sp.sympify(p["r2"]))}$.')

    def solution(self, p):
        r1, r2 = sp.sympify(p['r1']), sp.sympify(p['r2'])
        sign = '' if p['kind'] == 'internal' else '-'
        return (
            f'а) Гомотетия с центром $C$ и коэффициентом ${sign}\\frac{{R}}{{r}}$ ($r<R$ — радиусы) переводит меньшую окружность в большую '
            '(точка касания — центр гомотетии). Она переводит точку $D$ меньшей окружности, лежащую на прямой $CB$, в точку большей окружности '
            'на той же прямой, то есть в $B$, а точку $A$ — в $E$. Гомотетия переводит прямую $AD$ в параллельную ей прямую $EB$.\n\n'
            'б) $\\angle ACD=90^\\circ$ (прямые $CA$ и $CB$ перпендикулярны), поэтому $AD$ — диаметр меньшей окружности: $AD=2r$. '
            f'Пусть $CA=CB=x$; из гомотетии $CD=\\frac{{r}}{{R}}x$. По теореме Пифагора в треугольнике $ACD$: $x^2+\\frac{{r^2}}{{R^2}}x^2=4r^2$, '
            f'$$x=\\frac{{2rR}}{{\\sqrt{{R^2+r^2}}}}=\\frac{{2\\cdot {tx(r1)}\\cdot {tx(r2)}}}{{\\sqrt{{{tx(r2 ** 2)}+{tx(r1 ** 2)}}}}}={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        C, o1, o2, r1, r2, A, B = self._pts(p)
        E = g.second(A, C, o2, r2, C)
        D = g.second(B, C, o1, r1, C)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'E': E}, polygons=[['A', 'B', 'C']], segments=[('A', 'D'), ('B', 'E'), ('C', 'E'), ('C', 'D')],
                      circles=[(o1, r1), (o2, r2)], dots=['C', 'D', 'E'])

    def sample(self, rng):
        r1, r2 = rng.choice([('3', '4'), ('6', '8'), ('5', '12'), ('1', '2'), ('2', '3'), ('sqrt(15)', '15'), ('sqrt(3)', '3'), ('1', '3')])
        return dict(kind=rng.choice(['internal', 'external']), r1=r1, r2=r2, ask=rng.choice(['AC', 'BC']))


class RhombusPerpBC(Solved):
    """Прямая ⊥ BC пересекает диагонали ромба: AM:MC = 1:2, BN:ND = 1:3 ⇒ cos∠BAD = 1/5; MN делит BC как 1:4"""
    number, topic = 17, QUAD
    fipi = {'78A6C2': dict(mn='5', ask='area'), 'E80769': dict(mn='sqrt(6)', ask='side')}

    def _v(self, p):
        mn = sp.sympify(p['mn'])
        p2 = 18 * mn ** 2 / 5
        q2 = 2 * p2 / 3
        return mn, p2, q2

    def answer(self, p):
        mn, p2, q2 = self._v(p)
        if p['ask'] == 'area':
            return Answer.num(simp(2 * S(p2 * q2)))
        return Answer.num(simp(S(p2 + q2)))

    def check(self, p):
        mn, p2, q2 = (float(x) for x in self._v(p))
        pp, q = math.sqrt(p2), math.sqrt(q2)
        A, C, B, D = (-pp, 0.0), (pp, 0.0), (0.0, -q), (0.0, q)
        M, N = g.ratio(A, C, 1, 2), g.ratio(B, D, 1, 3)
        assert g.perpendicular(g.sub(N, M), g.sub(C, B)) and g.close(g.dist(M, N), mn)
        X = g.intersect(M, N, B, C)
        assert g.close(g.dist(B, X) / g.dist(X, C), 0.25)
        cosA = g.dot(g.sub(B, A), g.sub(D, A)) / g.dist(A, B) / g.dist(A, D)
        assert g.close(cosA, 0.2)
        return g.area(A, B, C, D) if p['ask'] == 'area' else g.dist(A, B)

    def condition(self, p):
        a = 'а) Докажите, что $\\cos\\angle BAD=\\frac15$.' if p['ask'] == 'area' else 'а) Докажите, что прямая $MN$ делит сторону $BC$ в отношении $1:4$.'
        b = 'площадь ромба' if p['ask'] == 'area' else 'сторону ромба'
        return ('Прямая, перпендикулярная стороне $BC$ ромба $ABCD$, пересекает его диагональ $AC$ в точке $M$, а диагональ $BD$ — в точке $N$, '
                f'причём $AM:MC=1:2$, $BN:ND=1:3$.\n\n{a}\n\nб) Найдите {b}, если $MN={tx(sp.sympify(p["mn"]))}$.')

    def solution(self, p):
        mn, p2, q2 = self._v(p)
        t = ('Введём координаты с началом в центре ромба $O$: $A(-p;0)$, $C(p;0)$, $B(0;-q)$, $D(0;q)$. Тогда $M\\left(-\\frac p3;0\\right)$, '
             '$N\\left(0;-\\frac q2\\right)$, $\\overrightarrow{MN}=\\left(\\frac p3;-\\frac q2\\right)$, $\\overrightarrow{BC}=(p;q)$. Условие '
             '$MN\\perp BC$: $\\frac{p^2}{3}-\\frac{q^2}{2}=0$, $q^2=\\frac23p^2$.\n\n')
        if p['ask'] == 'area':
            t = 'а) ' + t + ('$\\cos\\angle BAD=\\frac{\\overrightarrow{AB}\\cdot\\overrightarrow{AD}}{AB^2}=\\frac{p^2-q^2}{p^2+q^2}='
                             '\\frac{1/3}{5/3}=\\frac15$.\n\n')
        else:
            t = 'а) ' + t + ('Точка $M+s\\overrightarrow{MN}$ лежит на $BC$ (точки $B+u\\overrightarrow{BC}$): $-\\frac p3+\\frac{sp}{3}=up$, '
                             '$-\\frac{sq}{2}=-q+uq$; отсюда $s=\\frac85$, $u=\\frac15$: $MN$ делит $BC$ в отношении $1:4$.\n\n')
        t += (f'б) $MN^2=\\frac{{p^2}}{{9}}+\\frac{{q^2}}{{4}}=\\frac{{p^2}}{{9}}+\\frac{{p^2}}{{6}}=\\frac{{5p^2}}{{18}}={tx(mn ** 2)}$, '
              f'$p^2={tx(p2)}$, $q^2={tx(q2)}$.\n\n')
        if p['ask'] == 'area':
            return t + f'$$S=\\frac12\\cdot 2p\\cdot 2q=2pq=2\\sqrt{{{tx(p2)}\\cdot {tx(q2)}}}={self.answer(p).display.strip("$")}.$$'
        return t + f'$$AB=\\sqrt{{p^2+q^2}}=\\sqrt{{{tx(p2 + q2)}}}={self.answer(p).display.strip("$")}.$$'

    def figure(self, p):
        pp, q = 3.0, 3.0 * math.sqrt(2 / 3)
        A, C, B, D = (-pp, 0.0), (pp, 0.0), (0.0, -q), (0.0, q)
        M, N = g.ratio(A, C, 1, 2), g.ratio(B, D, 1, 3)
        X = g.intersect(M, N, B, C)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'M': M, 'N': N, 'X': X}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('A', 'C'), ('B', 'D'), ('M', 'X')], dots=['M', 'N', 'X'], right=[('X', 'C', 'M')])

    def sample(self, rng):
        return dict(mn=rng.choice(['5', 'sqrt(5)', 'sqrt(10)', '10', 'sqrt(6)', '2*sqrt(6)', '3*sqrt(6)', 'sqrt(30)']),
                    ask=rng.choice(['area', 'side']))


class RightTriangleKM(Solved):
    """M, N — середины AB и BC, CK:KB = 1:3: AN = 2KM; отрезок прямой BP внутри треугольника"""
    number, topic = 17, TRI
    fipi = {'A003cB': dict(a=8, b=6)}

    def answer(self, p):
        a, b = sp.Integer(p['a']), sp.Integer(p['b'])
        return Answer.num(simp(S(a ** 2 + 4 * b ** 2 / 25)))

    def check(self, p):
        a, b = float(p['a']), float(p['b'])
        C, B, A = (0.0, 0.0), (a, 0.0), (0.0, b)
        M, N, K = g.mid(A, B), g.mid(B, C), (a / 4, 0.0)
        assert g.close(g.dist(A, N), 2 * g.dist(K, M))
        P = g.intersect(A, N, K, M)
        Z = g.intersect(B, P, A, C)
        assert 0 <= Z[1] <= b
        return g.dist(B, Z)

    def condition(self, p):
        return ('В прямоугольном треугольнике $ABC$ точки $M$ и $N$ — середины гипотенузы $AB$ и катета $BC$, точка $K$ отмечена на катете $BC$ '
                'так, что $CK:KB=1:3$.\n\nа) Докажите, что $AN=2KM$.\n\nб) Пусть $P$ — точка пересечения отрезков $AN$ и $KM$. Найдите длину '
                f'отрезка прямой $BP$, заключённого внутри треугольника $ABC$, если $AC={p["b"]}$, $BC={p["a"]}$.')

    def solution(self, p):
        a, b = sp.Integer(p['a']), sp.Integer(p['b'])
        return (
            'а) Введём координаты: $C(0;0)$, $B(a;0)$, $A(0;b)$, $a=BC$, $b=AC$. Тогда $N\\left(\\frac a2;0\\right)$, $K\\left(\\frac a4;0\\right)$, '
            '$M\\left(\\frac a2;\\frac b2\\right)$. $AN=\\sqrt{\\frac{a^2}{4}+b^2}$, $KM=\\sqrt{\\frac{a^2}{16}+\\frac{b^2}{4}}=\\frac12\\sqrt{\\frac{a^2}{4}+b^2}$, '
            'то есть $AN=2KM$.\n\n'
            'б) Точка $P$: $A+t\\overrightarrow{AN}=K+s\\overrightarrow{KM}$, $\\frac{ta}{2}=\\frac a4(1+s)$, $b(1-t)=\\frac{sb}{2}$, откуда $t=\\frac34$, '
            '$P\\left(\\frac{3a}{8};\\frac b4\\right)$. Прямая $BP$ пересекает катет $AC$ ($x=0$) в точке $Z\\left(0;\\frac{2b}{5}\\right)$, которая лежит '
            'на отрезке $AC$. Искомый отрезок — $BZ$:\n\n'
            f'$$BZ=\\sqrt{{a^2+\\frac{{4b^2}}{{25}}}}=\\sqrt{{{a ** 2}+{tx(4 * b ** 2 / 25)}}}={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        a, b = float(p['a']), float(p['b'])
        C, B, A = (0.0, 0.0), (a, 0.0), (0.0, b)
        M, N, K = g.mid(A, B), g.mid(B, C), (a / 4, 0.0)
        P = g.intersect(A, N, K, M)
        Z = g.intersect(B, P, A, C)
        return g.draw({'A': A, 'B': B, 'C': C, 'M': M, 'N': N, 'K': K, 'P': P, 'Z': Z}, polygons=[['A', 'B', 'C']],
                      segments=[('A', 'N'), ('K', 'M'), ('B', 'Z')], dots=['M', 'N', 'K', 'P', 'Z'])

    def sample(self, rng):
        a, b = rng.choice([(8, 6), (4, 3), (12, 5), (5, 10), (10, 5), (4, 10), (8, 10), (6, 5)])
        return dict(a=a, b=b)


class IncircleEH(Solved):
    """Вписанная окружность прямоугольного треугольника, EH ⊥ MK: CH ∥ EK; отношение CH:EK"""
    number, topic = 17, CIRC
    fipi = {'9c96c5': dict(b=12, a=5)}

    def _v(self, p):
        a, b = sp.Integer(p['a']), sp.Integer(p['b'])
        c = S(a ** 2 + b ** 2)
        rr = (a + b - c) / 2
        # C(0;0), B(a;0), A(0;b); M(0;r), E(r;0); K на AB: AK = s − a
        s = (a + b + c) / 2
        K = (0 + (s - a) * a / c, b - (s - a) * b / c)
        # X = MK ∩ BC (y = 0): M + t(K − M), r + t(K_y − r) = 0
        t = -rr / (K[1] - rr)
        X = sp.nsimplify(t * K[0])
        xc, xe = sp.Abs(X), sp.Abs(X - rr)
        return a, b, c, rr, K, X, simp(xc / xe)

    def answer(self, p):
        q = self._v(p)[-1]
        return Answer.ratio(q, 1)

    def check(self, p):
        a, b = float(p['a']), float(p['b'])
        C, B, A = (0.0, 0.0), (a, 0.0), (0.0, b)
        I, rr = g.incenter(A, B, C), g.inradius(A, B, C)
        M, E, K = g.foot(I, A, C), g.foot(I, B, C), g.foot(I, A, B)
        H = g.foot(E, M, K)
        assert g.parallel(g.sub(H, C), g.sub(K, E))
        return g.dist(C, H) / g.dist(E, K)

    def condition(self, p):
        return ('Окружность с центром $O$ касается катетов $AC$ и $BC$ прямоугольного треугольника $ABC$ в точках $M$ и $E$, а гипотенузы — '
                'в точке $K$. Отрезок $EH$ — перпендикуляр к прямой $MK$.\n\nа) Докажите, что прямые $CH$ и $EK$ параллельны.\n\n'
                f'б) Найдите отношение $CH:EK$, если $AC={p["b"]}$ и $BC={p["a"]}$.')

    def solution(self, p):
        a, b, c, rr, K, X, q = self._v(p)
        return (
            'а) $CMOE$ — квадрат ($\\angle C=90^\\circ$, $OM=OE$, радиусы перпендикулярны касательным). Точки $C$ и $H$ видят отрезок $ME$ под '
            'прямым углом, поэтому лежат на окружности с диаметром $ME$, и $\\angle MHC=\\angle MEC=45^\\circ$ (угол между стороной и диагональю '
            'квадрата). Вписанный угол $MKE$ окружности с центром $O$ опирается на дугу $ME$ в $90^\\circ$: $\\angle MKE=45^\\circ$. Углы $MHC$ и '
            '$MKE$ — соответственные при прямых $CH$, $EK$ и секущей $MK$, значит, $CH\\parallel EK$.\n\n'
            f'б) $AB={tx(c)}$, $r=\\frac{{AC+BC-AB}}{{2}}={tx(rr)}$. Введём координаты: $C(0;0)$, $B({a};0)$, $A(0;{b})$, $M(0;{tx(rr)})$, '
            f'$E({tx(rr)};0)$; $AK=p-BC={tx((a + b + c) / 2 - a)}$, $K\\left({tx(K[0])};{tx(K[1])}\\right)$. Прямая $MK$ пересекает прямую $BC$ в '
            f'точке $X({tx(X)};0)$. Так как $CH\\parallel EK$, треугольники $XCH$ и $XEK$ подобны:\n\n'
            f'$$\\frac{{CH}}{{EK}}=\\frac{{XC}}{{XE}}=\\frac{{{tx(sp.Abs(X))}}}{{{tx(sp.Abs(X - rr))}}}={tx(q)}.$$')

    def figure(self, p):
        a, b = float(p['a']), float(p['b'])
        C, B, A = (0.0, 0.0), (a, 0.0), (0.0, b)
        I, rr = g.incenter(A, B, C), g.inradius(A, B, C)
        M, E, K = g.foot(I, A, C), g.foot(I, B, C), g.foot(I, A, B)
        H = g.foot(E, M, K)
        return g.draw({'A': A, 'B': B, 'C': C, 'M': M, 'E': E, 'K': K, 'H': H, 'O': I}, polygons=[['A', 'B', 'C']],
                      segments=[('M', 'K'), ('E', 'K'), ('E', 'H'), ('C', 'H')], circles=[(I, rr)], dots=['M', 'E', 'K', 'H', 'O'])

    def sample(self, rng):
        a, b = rng.choice([(3, 4), (4, 3), (5, 12), (12, 5), (8, 15), (15, 8), (6, 8), (7, 24), (20, 21)])
        return dict(a=a, b=b)


class MidlineTangentIncircle(Solved):
    """Средняя линия EF касается вписанной окружности: AC = P/4; площадь при прямом угле C"""
    number, topic = 17, CIRC
    fipi = {'92699C': dict(per=36)}

    def answer(self, p):
        P = sp.Integer(p['per'])
        return Answer.num(P ** 2 / 24)

    def check(self, p):
        P = float(p['per'])
        k = P / 12
        A, C, B = (0.0, 3 * k), (0.0, 0.0), (4 * k, 0.0)
        E, F = g.mid(A, B), g.mid(B, C)
        I, rr = g.incenter(A, B, C), g.inradius(A, B, C)
        assert g.close(g.dist_line(I, E, F), rr) and g.close(g.dist(A, C), P / 4)
        return g.area(A, B, C)

    def condition(self, p):
        return (f'Периметр треугольника $ABC$ равен ${p["per"]}$. Точки $E$ и $F$ — середины сторон $AB$ и $BC$. Отрезок $EF$ касается окружности, '
                f'вписанной в треугольник $ABC$.\n\nа) Докажите, что $AC={tx(sp.Rational(p["per"], 4))}$.\n\n'
                'б) Найдите площадь треугольника $ABC$, если $\\angle ACB=90^\\circ$.')

    def solution(self, p):
        P = sp.Integer(p['per'])
        ac = P / 4
        return (
            'а) Вписанная окружность касается всех сторон четырёхугольника $AEFC$, поэтому $AE+FC=EF+AC$. $AE=\\frac{AB}{2}$, $FC=\\frac{BC}{2}$, '
            '$EF=\\frac{AC}{2}$ (средняя линия): $\\frac{AB+BC}{2}=\\frac32AC$, $AB+BC=3AC$, и периметр $4AC=' + f'{P}$, $AC={tx(ac)}$.\n\n'
            f'б) $AB+BC={tx(3 * ac)}$, $AB^2-BC^2=AC^2={tx(ac ** 2)}$, поэтому $AB-BC=\\frac{{{tx(ac ** 2)}}}{{{tx(3 * ac)}}}={tx(ac / 3)}$; '
            f'$AB={tx(5 * ac / 3)}$, $BC={tx(4 * ac / 3)}$.\n\n$$S=\\frac12\\cdot AC\\cdot BC=\\frac12\\cdot {tx(ac)}\\cdot {tx(4 * ac / 3)}={tx(P ** 2 / 24)}.$$')

    def figure(self, p):
        A, C, B = (0.0, 3.0), (0.0, 0.0), (4.0, 0.0)
        E, F = g.mid(A, B), g.mid(B, C)
        I, rr = g.incenter(A, B, C), g.inradius(A, B, C)
        return g.draw({'A': A, 'B': B, 'C': C, 'E': E, 'F': F}, polygons=[['A', 'B', 'C']], segments=[('E', 'F')], circles=[(I, rr)],
                      dots=['E', 'F'], right=[('C', 'A', 'B')])

    def sample(self, rng):
        return dict(per=12 * rng.randint(1, 6))


class SquareMidpointsK(Solved):
    """Квадрат, M, N — середины AB и BC, K = CM ∩ DN: ∠BKM = 45°; радиус окружности ABK"""
    number, topic = 17, CIRC
    fipi = {'86B99A': dict(a='2*sqrt(10)')}

    def answer(self, p):
        a = sp.sympify(p['a'])
        return Answer.num(simp(a * S(10) / 6))

    def check(self, p):
        a = f(p['a'])
        A, B, C, D = (0.0, 0.0), (a, 0.0), (a, a), (0.0, a)
        M, N = g.mid(A, B), g.mid(B, C)
        K = g.intersect(C, M, D, N)
        assert g.close(g.angle(B, K, M), 45)
        return g.circumradius(A, B, K)

    def condition(self, p):
        return ('В квадрате $ABCD$ точки $M$ и $N$ — середины сторон $AB$ и $BC$. Отрезки $CM$ и $DN$ пересекаются в точке $K$.\n\n'
                'а) Докажите, что $\\angle BKM=45^\\circ$.\n\n'
                f'б) Найдите радиус окружности, описанной около треугольника $ABK$, если $AB={tx(sp.sympify(p["a"]))}$.')

    def solution(self, p):
        a = sp.sympify(p['a'])
        return (
            'а) Прямоугольные треугольники $BCM$ и $CDN$ равны (катеты $a$ и $\\frac a2$), поэтому $\\angle BCM=\\angle CDN$ и '
            '$\\angle KCN+\\angle KNC=\\angle CDN+\\angle CND=90^\\circ$: $CM\\perp DN$. Тогда $\\angle MKN=\\angle MBN=90^\\circ$, точки $B$, $M$, $K$, $N$ '
            'лежат на окружности с диаметром $MN$, и $\\angle BKM=\\angle BNM=45^\\circ$ (треугольник $MBN$ прямоугольный равнобедренный).\n\n'
            'б) Введём координаты: $A(0;0)$, $B(a;0)$, $C(a;a)$, $D(0;a)$. Решая систему уравнений прямых $CM$ и $DN$, получаем '
            '$K\\left(\\frac{4a}{5};\\frac{3a}{5}\\right)$. $\\overrightarrow{KA}=\\left(-\\frac{4a}{5};-\\frac{3a}{5}\\right)$, '
            '$\\overrightarrow{KB}=\\left(\\frac a5;-\\frac{3a}{5}\\right)$, $\\cos\\angle AKB=\\frac{a^2/5}{a\\cdot\\frac{a\\sqrt{10}}{5}}=\\frac{1}{\\sqrt{10}}$, '
            '$\\sin\\angle AKB=\\frac{3}{\\sqrt{10}}$.\n\n'
            f'$$R=\\frac{{AB}}{{2\\sin\\angle AKB}}=\\frac{{a\\sqrt{{10}}}}{{6}}={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        a = 1.0
        A, B, C, D = (0.0, 0.0), (a, 0.0), (a, a), (0.0, a)
        M, N = g.mid(A, B), g.mid(B, C)
        K = g.intersect(C, M, D, N)
        O = g.circumcenter(A, B, K)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'M': M, 'N': N, 'K': K}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('C', 'M'), ('D', 'N'), ('B', 'K'), ('A', 'K')], circles=[(O, g.dist(O, A))], dots=['M', 'N', 'K'])

    def sample(self, rng):
        return dict(a=rng.choice(['sqrt(10)', '3*sqrt(10)', '6', '12', '3', '4*sqrt(10)']))


class OrthicSimilarC1HK(Solved):
    """C₁K ∥ BB₁: треугольник C₁HK подобен ABC; отношение площадей"""
    number, topic = 17, TRI
    fipi = {'0063ED': dict(ab=6, bc=4, ac=5)}

    def answer(self, p):
        c, a, b = (sp.Integer(p[k]) for k in ('ab', 'bc', 'ac'))
        cosA = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
        cosB = (a ** 2 + c ** 2 - b ** 2) / (2 * a * c)
        cosC = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
        k2 = (cosA * cosB) ** 2 / (1 - cosC ** 2)
        return Answer.num(k2)

    def check(self, p):
        A, B, C = g.triangle(float(p['bc']), float(p['ac']), float(p['ab']))
        A1, B1, C1 = g.foot(A, B, C), g.foot(B, A, C), g.foot(C, A, B)
        H = g.orthocenter(A, B, C)
        K = g.intersect(C1, g.add(C1, g.sub(B1, B)), A, A1)
        assert g.close(g.dist(A, B) * g.dist(K, H), g.dist(B, C) * g.dist(C1, H))
        return g.area(C1, H, K) / g.area(A, B, C)

    def condition(self, p):
        return ('В остроугольном треугольнике $ABC$ высоты $AA_1$, $BB_1$ и $CC_1$ пересекаются в точке $H$. Через точку $C_1$ параллельно высоте '
                '$BB_1$ проведена прямая, пересекающая высоту $AA_1$ в точке $K$.\n\nа) Докажите, что $AB\\cdot KH=BC\\cdot C_1H$.\n\n'
                f'б) Найдите отношение площадей треугольников $C_1HK$ и $ABC$, если $AB={p["ab"]}$, $BC={p["bc"]}$, $AC={p["ac"]}$.')

    def solution(self, p):
        c, a, b = (sp.Integer(p[k]) for k in ('ab', 'bc', 'ac'))
        cosA = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
        cosB = (a ** 2 + c ** 2 - b ** 2) / (2 * a * c)
        cosC = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
        sinC = S(1 - cosC ** 2)
        k = simp(cosA * cosB / sinC)
        return (
            'а) $C_1K\\parallel BB_1\\perp AC$, $C_1H\\perp AB$, поэтому угол между $C_1K$ и $C_1H$ равен углу между $AC$ и $AB$: $\\angle HC_1K=\\angle A$. '
            'Угол между высотами $CC_1$ и $AA_1$ равен $\\angle B$ ($\\angle C_1HA=90^\\circ-\\angle C_1AH=\\angle B$), то есть $\\angle C_1HK=\\angle B$. '
            'Значит, треугольник $C_1HK$ подобен треугольнику $ABC$ ($C_1\\to A$, $H\\to B$, $K\\to C$), и $\\frac{KH}{BC}=\\frac{C_1H}{AB}$, '
            'что и требовалось.\n\n'
            'б) Коэффициент подобия $k=\\frac{C_1H}{AB}$. В прямоугольном треугольнике $BC_1H$: $C_1H=BC_1\\operatorname{ctg}A$, $BC_1=BC\\cos B$, '
            'поэтому $k=\\frac{BC\\cos B\\cos A}{AB\\sin A}=\\frac{\\cos A\\cos B}{\\sin C}$ (по теореме синусов $\\frac{BC}{\\sin A}=\\frac{AB}{\\sin C}$).\n\n'
            f'По теореме косинусов $\\cos A={tx(cosA)}$, $\\cos B={tx(cosB)}$, $\\cos C={tx(cosC)}$, $\\sin C={tx(sinC)}$, $k={tx(k)}$.\n\n'
            f'$$\\frac{{S_{{C_1HK}}}}{{S_{{ABC}}}}=k^2={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        A, B, C = g.triangle(float(p['bc']), float(p['ac']), float(p['ab']))
        A1, B1, C1 = g.foot(A, B, C), g.foot(B, A, C), g.foot(C, A, B)
        H = g.orthocenter(A, B, C)
        K = g.intersect(C1, g.add(C1, g.sub(B1, B)), A, A1)
        return g.draw({'A': A, 'B': B, 'C': C, 'A1': A1, 'B1': B1, 'C1': C1, 'H': H, 'K': K}, polygons=[['A', 'B', 'C'], ['C1', 'H', 'K']],
                      segments=[('A', 'A1'), ('B', 'B1'), ('C', 'C1')], dots=['A1', 'B1', 'C1', 'H', 'K'])

    def nice(self, answer) -> bool:
        return len(answer['display']) <= 40 and all(int(x) <= 2000 for x in re.findall(r'\d+', answer['display']))

    def sample(self, rng):
        for _ in range(60):
            a, b, c = sorted(rng.sample(range(3, 13), 3))
            if a + b > c and a * a + b * b > c * c:
                sides = [a, b, c]
                rng.shuffle(sides)
                return dict(ab=sides[0], bc=sides[1], ac=sides[2])
        return None


class InternalTangentChord(Solved):
    """Меньшая окружность проходит через центр большей и касается её в A; хорда BC касается меньшей в P: KM ∥ BC; найти AL"""
    number, topic = 17, CIRC
    fipi = {'BE8FE4': dict(R=34, bc=32)}

    def _v(self, p):
        R, bc = sp.Integer(p['R']), sp.Integer(p['bc'])
        d = S(R ** 2 - (bc / 2) ** 2)
        return R, bc, d, simp(S(R * (R - d)) / 2)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        R, bc, d, al = (float(x) for x in self._v(p))
        O = (0.0, 0.0)
        y1 = -d + R / 2
        x1 = math.sqrt((R / 2) ** 2 - y1 ** 2)
        O1 = (x1, y1)
        A = g.mul(O1, 2)
        B, C = (-bc / 2, -d), (bc / 2, -d)
        P = (x1, -d)
        assert g.close(g.dist(A, O), R) and g.close(g.dist_line(O1, B, C), R / 2)
        K = g.second(A, B, O1, R / 2, A)
        M = g.second(A, C, O1, R / 2, A)
        assert g.parallel(g.sub(M, K), g.sub(C, B))
        L = g.intersect(K, M, A, P)
        return g.dist(A, L)

    def condition(self, p):
        return ('Две окружности касаются внутренним образом в точке $A$, причём меньшая проходит через центр большей. Хорда $BC$ большей '
                'окружности касается меньшей в точке $P$. Хорды $AB$ и $AC$ пересекают меньшую окружность в точках $K$ и $M$.\n\n'
                'а) Докажите, что прямые $KM$ и $BC$ параллельны.\n\n'
                f'б) Пусть $L$ — точка пересечения отрезков $KM$ и $AP$. Найдите $AL$, если радиус большей окружности равен ${p["R"]}$, а $BC={p["bc"]}$.')

    def solution(self, p):
        R, bc, d, al = self._v(p)
        return (
            'а) Меньшая окружность проходит через центр $O$ большей и касается её в $A$, значит, $AO$ — её диаметр, и её радиус $r=\\frac R2$. '
            'Гомотетия с центром $A$ и коэффициентом $\\frac12$ переводит большую окружность в меньшую, точку $B$ — в $K$, точку $C$ — в $M$ '
            '($K$, $M$ — середины $AB$ и $AC$). Значит, $KM\\parallel BC$.\n\n'
            'б) $KM$ — средняя линия треугольника $ABC$, она делит $AP$ пополам: $AL=\\frac12AP$. Введём координаты: $O(0;0)$, хорда $BC$ на прямой '
            f'$y=-d$, $d=\\sqrt{{R^2-\\left(\\frac{{BC}}{{2}}\\right)^2}}={tx(d)}$. Центр меньшей окружности $O_1(x;y)$: $|OO_1|=\\frac R2$ и расстояние '
            'от $O_1$ до $BC$ равно $\\frac R2$, поэтому $y=-d+\\frac R2$, $x^2=\\frac{R^2}{4}-y^2=dR-d^2$; $A=2O_1$, $P(x;-d)$.\n\n'
            '$AP^2=x^2+(R-d)^2=dR-d^2+(R-d)^2=R(R-d)$, '
            f'$$AL=\\frac12\\sqrt{{R(R-d)}}=\\frac12\\sqrt{{{R}\\cdot {tx(R - d)}}}={tx(al)}.$$')

    def figure(self, p):
        R, bc, d, al = (float(x) for x in self._v(p))
        y1 = -d + R / 2
        x1 = math.sqrt((R / 2) ** 2 - y1 ** 2)
        O1 = (x1, y1)
        A = g.mul(O1, 2)
        B, C, P = (-bc / 2, -d), (bc / 2, -d), (x1, -d)
        K, M = g.second(A, B, O1, R / 2, A), g.second(A, C, O1, R / 2, A)
        return g.draw({'A': A, 'B': B, 'C': C, 'P': P, 'K': K, 'M': M, 'O': (0.0, 0.0)}, polygons=[['A', 'B', 'C']],
                      segments=[('K', 'M'), ('A', 'P')], circles=[((0.0, 0.0), R), (O1, R / 2)], dots=['P', 'K', 'M', 'O'])

    def sample(self, rng):
        R, half = rng.choice([(5, 4), (10, 8), (13, 12), (13, 5), (17, 15), (25, 24), (25, 7), (34, 16), (10, 6), (26, 10)])
        return dict(R=R, bc=2 * half)


class BisectorADK(Solved):
    """AB = BD, BF — биссектриса, CK ⊥ AD: AB:BC = AE:EK; отношение площадей ABE и CDEF"""
    number, topic = 17, TRI
    fipi = {'003F6E': dict(p=5, q=2)}

    def _v(self, p):
        pp, q = sp.Integer(p['p']), sp.Integer(p['q'])
        s_abe = pp / (2 * (pp + q))
        s_bfc = (pp + q) / (2 * pp + q)
        s_bed = pp / (2 * (pp + q))
        return s_abe, s_bfc, s_bed, s_bfc - s_bed

    def answer(self, p):
        s_abe, s_bfc, s_bed, s_cdef = self._v(p)
        return Answer.ratio(s_abe, s_cdef)

    def check(self, p):
        pp, q = p['p'], p['q']
        B, C = (0.0, 0.0), (float(pp + q), 0.0)
        A = g.polar(float(pp), 70)
        D = (float(pp), 0.0)
        F = g.ratio(A, C, pp, pp + q)       # AF : FC = AB : BC
        E = g.intersect(B, F, A, D)
        K = g.foot(C, A, D)
        assert g.close(g.dist(A, B) / g.dist(B, C), g.dist(A, E) / g.dist(E, K))
        return g.area(A, B, E) / g.area(C, D, E, F)

    def condition(self, p):
        return ('На стороне $BC$ треугольника $ABC$ отмечена точка $D$ так, что $AB=BD$. Биссектриса $BF$ треугольника $ABC$ пересекает прямую $AD$ '
                'в точке $E$. Из точки $C$ на прямую $AD$ опущен перпендикуляр $CK$.\n\nа) Докажите, что $AB:BC=AE:EK$.\n\n'
                f'б) Найдите отношение площади треугольника $ABE$ к площади четырёхугольника $CDEF$, если $BD:DC={p["p"]}:{p["q"]}$.')

    def solution(self, p):
        s_abe, s_bfc, s_bed, s_cdef = self._v(p)
        pp, q = p['p'], p['q']
        return (
            'а) Треугольник $ABD$ равнобедренный, его биссектриса $BE$ — медиана и высота: $AE=ED$, $BE\\perp AD$. $CK\\perp AD$, поэтому '
            '$BE\\parallel CK$, и по теореме о пропорциональных отрезках (угол с вершиной $D$) $\\frac{DE}{DK}=\\frac{DB}{DC}$. Тогда '
            '$\\frac{AE}{EK}=\\frac{ED}{ED+DK}=\\frac{DB}{DB+DC}=\\frac{BD}{BC}=\\frac{AB}{BC}$.\n\n'
            f'б) Пусть $S=S_{{ABC}}$. $AB=BD$, $BD:BC={pp}:{pp + q}$, $S_{{ABD}}=\\frac{{{pp}}}{{{pp + q}}}S$, $S_{{ABE}}=S_{{BED}}=\\frac12 S_{{ABD}}={tx(s_abe)}S$. '
            f'По свойству биссектрисы $\\frac{{AF}}{{FC}}=\\frac{{AB}}{{BC}}=\\frac{{{pp}}}{{{pp + q}}}$, $S_{{BFC}}=\\frac{{FC}}{{AC}}S={tx(s_bfc)}S$. '
            f'$S_{{CDEF}}=S_{{BFC}}-S_{{BED}}={tx(s_cdef)}S$.\n\n'
            f'$$S_{{ABE}}:S_{{CDEF}}={tx(s_abe)}:{tx(s_cdef)}={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        pp, q = p['p'], p['q']
        B, C = (0.0, 0.0), (float(pp + q), 0.0)
        A = g.polar(float(pp), 70)
        D = (float(pp), 0.0)
        F = g.ratio(A, C, pp, pp + q)
        E = g.intersect(B, F, A, D)
        K = g.foot(C, A, D)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'K': K}, polygons=[['A', 'B', 'C']],
                      segments=[('B', 'F'), ('A', 'K'), ('C', 'K')], dots=['D', 'E', 'F', 'K'])

    def sample(self, rng):
        pp, q = rng.choice([(5, 2), (3, 1), (2, 1), (3, 2), (4, 3), (1, 1), (2, 3)])
        return dict(p=pp, q=q)


class ParallelogramHeightsPQ(Solved):
    """Высоты BP и BQ параллелограмма, AM = BP, AB = BQ: BM = PQ; площадь APQ"""
    number, topic = 17, QUAD
    fipi = {'36ce6e': dict(h=8, c=10)}

    def _v(self, p):
        h, c = sp.Integer(p['h']), sp.Integer(p['c'])
        sinA = h / c
        cosA = S(1 - sinA ** 2)
        ad = c / sinA                          # BC = AB / sin A (из BQ = AB)
        A = sp.Matrix([0, 0])
        B = sp.Matrix([c * cosA, h])
        D = sp.Matrix([ad, 0])
        C = B + D
        u = (C - D) / c
        Q = D + u * (B - D).dot(u)
        ap = c * cosA
        return sinA, cosA, ad, B, C, D, Q, ap, simp(ap * Q[1] / 2)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        h, c = float(p['h']), float(p['c'])
        sinA = h / c
        cosA = math.sqrt(1 - sinA ** 2)
        A, B = (0.0, 0.0), (c * cosA, h)
        D = (c / sinA, 0.0)
        C = g.add(B, D)
        P, Q = g.foot(B, A, D), g.foot(B, C, D)
        assert g.close(g.dist(B, Q), c)
        M = (h, 0.0)
        assert g.close(g.dist(B, M), g.dist(P, Q))
        return g.area(A, P, Q)

    def condition(self, p):
        return ('В параллелограмме $ABCD$ с острым углом $BAD$ из вершины $B$ проведены высоты $BP$ и $BQ$, причём $P$ лежит на стороне $AD$, '
                'а $Q$ — на стороне $CD$. На стороне $AD$ отмечена точка $M$. Известно, что $AM=BP$, $AB=BQ$.\n\nа) Докажите, что $BM=PQ$.\n\n'
                f'б) Найдите площадь треугольника $APQ$, если $AM=BP={p["h"]}$, $AB=BQ={p["c"]}$.')

    def solution(self, p):
        sinA, cosA, ad, B, C, D, Q, ap, s = self._v(p)
        h, c = p['h'], p['c']
        return (
            'а) $\\angle PBQ=180^\\circ-\\angle PDQ=180^\\circ-\\angle ADC=\\angle BAD$ (в четырёхугольнике $BPDQ$ два прямых угла). Треугольники '
            '$BAM$ и $QBP$ равны по двум сторонам и углу между ними: $AB=BQ$, $AM=BP$, $\\angle BAM=\\angle QBP$. Значит, $BM=PQ$.\n\n'
            f'б) $\\sin A=\\frac{{BP}}{{AB}}={tx(sinA)}$, $\\cos A={tx(cosA)}$, $AP=AB\\cos A={tx(ap)}$. Из $BQ=BC\\sin\\angle C=BC\\sin A=AB$: '
            f'$AD=BC={tx(ad)}$. Введём координаты: $A(0;0)$, $D({tx(ad)};0)$, $B({tx(B[0])};{h})$, $C({tx(C[0])};{h})$. $Q$ — проекция $B$ на $CD$: '
            f'$Q\\left({tx(Q[0])};{tx(Q[1])}\\right)$.\n\n$$S_{{APQ}}=\\frac12\\cdot AP\\cdot y_Q=\\frac12\\cdot {tx(ap)}\\cdot {tx(Q[1])}={tx(s)}.$$')

    def figure(self, p):
        h, c = float(p['h']), float(p['c'])
        sinA = h / c
        cosA = math.sqrt(1 - sinA ** 2)
        A, B = (0.0, 0.0), (c * cosA, h)
        D = (c / sinA, 0.0)
        C = g.add(B, D)
        P, Q = g.foot(B, A, D), g.foot(B, C, D)
        M = (h, 0.0)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'P': P, 'Q': Q, 'M': M}, polygons=[['A', 'B', 'C', 'D'], ['A', 'P', 'Q']],
                      segments=[('B', 'P'), ('B', 'Q'), ('B', 'M')], dots=['P', 'Q', 'M'])

    def sample(self, rng):
        h, c = rng.choice([(8, 10), (4, 5), (12, 13), (3, 5), (12, 15), (6, 10), (15, 17), (5, 13)])
        return dict(h=h, c=c)


class TrapezoidTwoCircles(Solved):
    """Окружности касаются оснований и боковой стороны трапеции: O₁O₂ ∥ основаниям; найти O₁O₂"""
    number, topic = 17, CIRC
    fipi = {'7EEB3E': dict(ab=10, bc=9, cd=30, ad=39)}

    def _v(self, p):
        ab, bc, cd, ad = (sp.Integer(p[k]) for k in ('ab', 'bc', 'cd', 'ad'))
        s = ad - bc
        d = (cd ** 2 - ab ** 2) / s
        x1, x2 = (s - d) / 2, (s + d) / 2
        h = S(ab ** 2 - x1 ** 2)
        rr = h / 2
        cA, cD = x1 / ab, x2 / cd
        ctA = S((1 + cA) / (1 - cA))
        ctD = S((1 + cD) / (1 - cD))
        return x1, x2, h, rr, cA, cD, simp(rr * ctA), simp(rr * ctD), simp(ad - rr * ctA - rr * ctD)

    def answer(self, p):
        return Answer.num(self._v(p)[-1])

    def check(self, p):
        x1, x2, h, rr, *_ = (float(x) for x in self._v(p))
        ad, bc = float(p['ad']), float(p['bc'])
        A, D, B, C = (0.0, 0.0), (ad, 0.0), (x1, h), (x1 + bc, h)
        assert g.close(g.dist(C, D), p['cd'])

        def center(V, U, W):       # центр окружности радиуса r, касающейся сторон угла V (лучи VU, VW), на высоте r
            bis = g.add(g.mul(g.sub(U, V), 1 / g.dist(U, V)), g.mul(g.sub(W, V), 1 / g.dist(W, V)))
            return g.intersect(V, g.add(V, bis), (0.0, rr), (1.0, rr))
        O1, O2 = center(A, B, D), center(D, C, A)
        assert g.close(g.dist_line(O1, A, B), rr) and g.close(g.dist_line(O2, C, D), rr)
        return g.dist(O1, O2)

    def condition(self, p):
        return ('Окружность с центром $O_1$ касается оснований $BC$ и $AD$ и боковой стороны $AB$ трапеции $ABCD$. Окружность с центром $O_2$ '
                f'касается сторон $BC$, $CD$ и $AD$. Известно, что $AB={p["ab"]}$, $BC={p["bc"]}$, $CD={p["cd"]}$, $AD={p["ad"]}$.\n\n'
                'а) Докажите, что прямая $O_1O_2$ параллельна основаниям трапеции.\n\nб) Найдите $O_1O_2$.')

    def solution(self, p):
        x1, x2, h, rr, cA, cD, a1, a2, ans = self._v(p)
        return (
            'а) Обе окружности касаются обеих параллельных прямых $BC$ и $AD$, поэтому их радиусы равны половине высоты $h$ трапеции, а центры '
            'находятся на расстоянии $\\frac h2$ от $AD$, то есть на средней линии. Значит, $O_1O_2\\parallel AD\\parallel BC$.\n\n'
            f'б) Проекции боковых сторон на основание: $x_1+x_2=AD-BC={p["ad"] - p["bc"]}$, $x_2^2-x_1^2=CD^2-AB^2$, откуда $x_1={tx(x1)}$, '
            f'$x_2={tx(x2)}$; $h=\\sqrt{{AB^2-x_1^2}}={tx(h)}$, $r=\\frac h2={tx(rr)}$. $\\cos A=\\frac{{x_1}}{{AB}}={tx(cA)}$, '
            f'$\\cos D=\\frac{{x_2}}{{CD}}={tx(cD)}$.\n\n'
            'Центр $O_1$ лежит на биссектрисе угла $A$, его проекция на $AD$ удалена от $A$ на $r\\operatorname{ctg}\\frac A2$, где '
            '$\\operatorname{ctg}\\frac A2=\\sqrt{\\frac{1+\\cos A}{1-\\cos A}}$; аналогично для $O_2$ и угла $D$: '
            f'$r\\operatorname{{ctg}}\\frac A2={tx(a1)}$, $r\\operatorname{{ctg}}\\frac D2={tx(a2)}$.\n\n'
            f'$$O_1O_2=AD-{tx(a1)}-{tx(a2)}={tx(ans)}.$$')

    def figure(self, p):
        x1, x2, h, rr, *_ = (float(x) for x in self._v(p))
        ad, bc = float(p['ad']), float(p['bc'])
        A, D, B, C = (0.0, 0.0), (ad, 0.0), (x1, h), (x1 + bc, h)

        def center(V, U, W):
            bis = g.add(g.mul(g.sub(U, V), 1 / g.dist(U, V)), g.mul(g.sub(W, V), 1 / g.dist(W, V)))
            return g.intersect(V, g.add(V, bis), (0.0, rr), (1.0, rr))
        O1, O2 = center(A, B, D), center(D, C, A)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'O1': O1, 'O2': O2}, polygons=[['A', 'B', 'C', 'D']], segments=[('O1', 'O2')],
                      circles=[(O1, rr), (O2, rr)], dots=['O1', 'O2'])


class TrapezoidMidpointE(Solved):
    """E — середина CD, CK ∥ AE: CO = KO; отношение оснований по доле площади треугольника BCK"""
    number, topic = 17, QUAD
    fipi = {'15EF35': dict(f='9/100')}

    def answer(self, p):
        k = S(sp.Rational(p['f']))
        return Answer.ratio(k, 1 - k)

    def check(self, p):
        k = math.sqrt(float(sp.Rational(p['f'])))
        bc, ad = k, 1 - k
        A, D, B, C = (0.0, 0.0), (ad, 0.0), (0.15, 0.6), (0.15 + bc, 0.6)
        E = g.mid(C, D)
        K = g.intersect(C, g.add(C, g.sub(E, A)), A, B)
        O = g.intersect(C, K, B, E)
        assert g.close(g.dist(C, O), g.dist(K, O))
        assert g.close(g.area(B, C, K) / g.area(A, B, C, D), float(sp.Rational(p['f'])))
        return bc / ad

    def condition(self, p):
        return ('Точка $E$ — середина боковой стороны $CD$ трапеции $ABCD$. На стороне $AB$ взята точка $K$ так, что прямые $CK$ и $AE$ параллельны. '
                'Отрезки $CK$ и $BE$ пересекаются в точке $O$.\n\nа) Докажите, что $CO=KO$.\n\n'
                f'б) Найдите отношение оснований $BC$ и $AD$, если площадь треугольника $BCK$ составляет ${tx(sp.Rational(p["f"]))}$ площади трапеции.')

    def solution(self, p):
        fr = sp.Rational(p['f'])
        k = S(fr)
        return (
            'а) Пусть прямая $AE$ пересекает прямую $BC$ в точке $X$. Треугольники $ECX$ и $EDA$ равны ($CE=ED$, вертикальные углы, накрест лежащие '
            'углы при $BX\\parallel AD$), поэтому $CX=AD$ и $AE=EX$: $BE$ — медиана треугольника $ABX$. Медиана делит пополам любой отрезок с концами '
            'на сторонах $BA$ и $BX$, параллельный $AX$, — в том числе $CK$. Значит, $CO=KO$.\n\n'
            'б) Площадь треугольника $ABX$ равна площади трапеции (треугольник $ECX$ заменяет равный ему $EDA$). $CK\\parallel AX$, треугольник $BCK$ '
            'подобен $BXA$ с коэффициентом $\\frac{BC}{BX}=\\frac{BC}{BC+AD}$:\n\n'
            f'$$\\left(\\frac{{BC}}{{BC+AD}}\\right)^2={tx(fr)},\\quad \\frac{{BC}}{{BC+AD}}={tx(k)},\\quad BC:AD={self.answer(p).display.strip("$")}.$$')

    def figure(self, p):
        k = math.sqrt(float(sp.Rational(p['f'])))
        bc, ad = k * 3, (1 - k) * 3
        A, D, B, C = (0.0, 0.0), (ad, 0.0), (0.5, 1.6), (0.5 + bc, 1.6)
        E = g.mid(C, D)
        K = g.intersect(C, g.add(C, g.sub(E, A)), A, B)
        O = g.intersect(C, K, B, E)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'K': K, 'O': O}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('A', 'E'), ('C', 'K'), ('B', 'E')], dots=['E', 'K', 'O'])

    def sample(self, rng):
        a, b = rng.choice([(1, 3), (1, 2), (2, 3), (3, 7), (1, 4), (2, 5), (3, 5)])
        return dict(f=str(sp.Rational(a, a + b) ** 2))


class TrapezoidIncircleRay(Solved):
    """Вписанная в равнобедренную трапецию окружность, луч AM: AN = k, MN = 3k ⇒ AD = AM; найти основания"""
    number, topic = 17, CIRC
    fipi = {'8C8D87': dict(k=4)}

    def answer(self, p):
        k = sp.Integer(p['k'])
        return Answer(f'${tx(4 * k)}$ и ${tx(12 * k / 5)}$', 4 * k + 12 * k / 5)

    def check(self, p):
        k = float(p['k'])
        t = 2 * k
        b = 3 * t / 5
        ad, bc = 2 * t, 2 * b
        rr = math.sqrt(t * b)            # радиус: r² = (касательная из A)·(касательная из B)
        A, D = (-t, 0.0), (t, 0.0)
        B, C = (-b, 2 * rr), (b, 2 * rr)
        O = (0.0, rr)
        M = g.foot(O, C, D)
        N = g.second(A, M, O, rr, M)
        assert g.close(g.dist(A, N), k) and g.close(g.dist(M, N), 3 * k)
        K = g.intersect(A, M, B, C)
        assert g.close(g.angle(A, M, D), g.angle(M, C, K))
        return ad + bc

    def condition(self, p):
        k = p['k']
        return ('Окружность, вписанная в равнобедренную трапецию $ABCD$, касается её боковой стороны $CD$ в точке $M$. Луч $AM$ вторично '
                f'пересекает окружность в точке $N$, а прямую $BC$ — в точке $K$, причём $AN={k}$, $MN={3 * k}$.\n\n'
                'а) Докажите, что $\\angle AMD=\\angle MCK$.\n\nб) Найдите основания трапеции.')

    def solution(self, p):
        k = sp.Integer(p['k'])
        t = 2 * k
        return (
            f'а) Касательная из $A$: $t^2=AN\\cdot AM={k}\\cdot {4 * k}$, $t={tx(t)}$. В равнобедренной трапеции касательные из $A$ и $D$ равны, '
            f'поэтому $AD=2t={tx(2 * t)}$ и $DM=t={tx(t)}$. Тогда $AM=AN+NM={4 * k}=AD$, треугольник $ADM$ равнобедренный: '
            '$\\angle AMD=\\angle ADM$. А $\\angle ADM=\\angle MCK$ как накрест лежащие при $AD\\parallel CK$ и секущей $CD$.\n\n'
            f'б) В треугольнике $ADM$: $AD=AM={tx(2 * t)}$, $DM={tx(t)}$, $\\cos D=\\frac{{DM/2}}{{AD}}=\\frac14$. Пусть $b$ — касательная из $C$ '
            f'(и из $B$), $BC=2b$, боковая сторона $t+b$. Проекция боковой стороны на $AD$: $\\frac{{AD-BC}}{{2}}=(t+b)\\cos D$, '
            f'${tx(t)}-b=\\frac{{{tx(t)}+b}}{{4}}$, $b={tx(3 * t / 5)}$.\n\nОснования трапеции: $AD={tx(4 * k)}$, $BC={tx(12 * k / 5)}$.')

    def figure(self, p):
        k = 1.0
        t = 2 * k
        b = 3 * t / 5
        rr = math.sqrt(t * b)
        A, D, B, C = (-t, 0.0), (t, 0.0), (-b, 2 * rr), (b, 2 * rr)
        O = (0.0, rr)
        M = g.foot(O, C, D)
        N = g.second(A, M, O, rr, M)
        K = g.intersect(A, M, B, C)
        return g.draw({'A': A, 'B': B, 'C': C, 'D': D, 'M': M, 'N': N, 'K': K}, polygons=[['A', 'B', 'C', 'D']],
                      segments=[('A', 'K'), ('C', 'K')], circles=[(O, rr)], dots=['M', 'N', 'K'])

    def sample(self, rng):
        return dict(k=rng.choice([1, 2, 3, 5, 6, 10]))


TEMPLATES = [c() for c in Solved.__subclasses__() if c.__module__ == __name__]
EXTRA = []
