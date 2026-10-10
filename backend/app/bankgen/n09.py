"""№ 9. Задачи с прикладным содержанием: вычисления по физическим формулам"""
import math
import random
import re
from fractions import Fraction

from app.bankgen.core import Rendered, Template, dec, frac, isqrt_exact, nice_number, par, tex_frac, tex_num

N = r'(\d[\d ]*(?:[,.]\d+)?)'   # число в тексте: «20 880», «12,5»
TN = r'(-?\d+(?:\{,\}\d+)?)'     # число в формуле: 5{,}8


def _n(s: str) -> Fraction:
    return Fraction(s.replace(' ', '').replace('\u00a0', '').replace('{,}', '.').replace(',', '.'))


def _sp(x) -> str:
    """Число с пробелом-разделителем тысяч: 20880 → «20 880»"""
    s = dec(x)
    whole, _, rest = s.partition(',')
    if len(whole.lstrip('-')) > 4:
        whole = f'{int(whole):,}'.replace(',', ' ')
    return whole + (',' + rest if rest else '')


def _log2_exact(x: Fraction) -> int:
    """log₂ x для степени двойки (в том числе дробной 1/2^k)"""
    if x <= 0:
        raise ValueError('не степень двойки')
    k = 0
    while x > 1 and x.denominator == 1 and x.numerator % 2 == 0:
        x /= 2
        k += 1
    while x < 1 and x.numerator == 1 and x.denominator % 2 == 0:
        x *= 2
        k -= 1
    if x != 1:
        raise ValueError('не степень двойки')
    return k


class Applied(Template):
    number = 9
    topic = 'Прикладные задачи'

    def render(self, p):
        cond, sol = self.build(p)
        return Rendered(cond, sol + f'\n\n**Ответ:** {dec(self.solve(p))}.')

    def nice(self, x):
        return nice_number(x, max_decimals=2) and x > 0


class CarAcceleration(Applied):
    code = '9.car'
    patterns = [r'постоянным ускорением \$a=(\d+)\\text\{км\}/\\text\{ч\}\^2\$.*?v=\\sqrt\{2la\}.*?Найдите, сколько километров проедет автомобиль к моменту, когда он разгонится до скорости (\d+) км/ч',
                r'v=\\sqrt\{2la\}.*?Найдите ускорение, с которым должен двигаться автомобиль, чтобы, проехав ' + N + r' км, (?:приобрести|развить) скорость (\d+) км/ч']

    def parse(self, m, task):
        if 'ускорение, с которым' in m.group(0):
            return {'ask': 'a', 'l': _n(m.group(1)), 'v': _n(m.group(2))}
        return {'ask': 'l', 'a': _n(m.group(1)), 'v': _n(m.group(2))}

    def solve(self, p):
        return p['v'] ** 2 / (2 * p['a']) if p['ask'] == 'l' else p['v'] ** 2 / (2 * p['l'])

    def build(self, p):
        head = ('Автомобиль разгоняется на прямолинейном участке шоссе с постоянным ускорением $a$ (в км/ч²). Скорость $v$ (в км/ч) '
                'вычисляется по формуле $v=\\sqrt{2la}$, где $l$ — пройденный автомобилем путь (в км). ')
        v = p['v']
        if p['ask'] == 'l':
            cond = head.replace('ускорением $a$ (в км/ч²)', f'ускорением $a={p["a"]}$ км/ч²') + \
                f'Найдите, сколько километров проедет автомобиль к моменту, когда он разгонится до скорости {v} км/ч.'
            sol = (f'Из $v=\\sqrt{{2la}}$ получаем $v^2=2la$, откуда $$l=\\frac{{v^2}}{{2a}}=\\frac{{{v}^2}}{{2\\cdot {p["a"]}}}'
                   f'=\\frac{{{v * v}}}{{{2 * p["a"]}}}={tex_num(self.solve(p))}.$$')
        else:
            cond = head + (f'Найдите ускорение, с которым должен двигаться автомобиль, чтобы, проехав {dec(p["l"])} км, приобрести скорость '
                           f'{v} км/ч. Ответ дайте в км/ч².')
            sol = (f'Из $v^2=2la$: $$a=\\frac{{v^2}}{{2l}}=\\frac{{{v}^2}}{{2\\cdot {tex_num(p["l"])}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        v = Fraction(rng.choice([40, 50, 60, 70, 80, 90, 100, 110, 120]))
        if rng.random() < 0.5:
            return {'ask': 'l', 'a': Fraction(rng.choice([2000, 2500, 3000, 4000, 4500, 5000, 6000, 8000])), 'v': v}
        return {'ask': 'a', 'l': Fraction(rng.choice([1, 2, Fraction(1, 2), Fraction(4, 5)])), 'v': v}


class DivingBell(Applied):
    """A = αυT·log₂(V₁/V₂) или log₂(p₂/p₁)"""
    code = '9.bell'
    patterns = [r'содержащий \$\\text\{υ\}=(\d+)\$ моль воздуха (объёмом \$V_1|при давлении \$p_1)=' + TN + r'.*?где \$(?:\\alpha|\\text\{α\})=' + TN
                + r'.*?\$T=(\d+)\\text\{[КK]\}\$.*?совершена работа (?:в )?' + N + r' Дж']

    def parse(self, m, task):
        return {'kind': 'V' if 'объёмом' in m.group(2) else 'p', 'nu': _n(m.group(1)), 'x1': _n(m.group(3)), 'alpha': _n(m.group(4)),
                'T': _n(m.group(5)), 'A': _n(m.group(6))}

    def _k(self, p):
        q = p['A'] / (p['alpha'] * p['nu'] * p['T'])
        if q.denominator != 1:
            raise ValueError('показатель дробный')
        return int(q)

    def solve(self, p):
        k = self._k(p)
        return p['x1'] / Fraction(2) ** k if p['kind'] == 'V' else p['x1'] * Fraction(2) ** k

    def build(self, p):
        nu, x1, alpha, T, A = p['nu'], p['x1'], p['alpha'], p['T'], p['A']
        k = self._k(p)
        if p['kind'] == 'V':
            cond = (f'Водолазный колокол, содержащий $\\nu={nu}$ моль воздуха объёмом $V_1={x1}$ л, медленно опускают на дно водоёма. '
                    f'При этом происходит изотермическое сжатие воздуха до конечного объёма $V_2$ (в л). Работа, совершаемая водой при сжатии '
                    f'воздуха, вычисляется по формуле $A=\\alpha\\nu T\\log_2\\frac{{V_1}}{{V_2}}$, где $\\alpha={tex_num(alpha)}\\,\\frac{{\\text{{Дж}}}}'
                    f'{{\\text{{моль}}\\cdot\\text{{К}}}}$ — постоянная, $T={T}$ К — температура воздуха. Найдите, какой объём $V_2$ будет '
                    f'занимать воздух в колоколе, если при сжатии воздуха была совершена работа в {_sp(A)} Дж. Ответ дайте в литрах.')
            sol = (f'$\\alpha\\nu T={tex_num(alpha)}\\cdot {nu}\\cdot {T}={tex_num(alpha * nu * T)}$, поэтому '
                   f'$$\\log_2\\frac{{V_1}}{{V_2}}=\\frac{{{tex_num(A)}}}{{{tex_num(alpha * nu * T)}}}={k},\\qquad \\frac{{{x1}}}{{V_2}}=2^{{{k}}}={2 ** k},'
                   f'\\qquad V_2=\\frac{{{x1}}}{{{2 ** k}}}={tex_num(self.solve(p))}.$$')
        else:
            cond = (f'Водолазный колокол, содержащий $\\nu={nu}$ моль воздуха при давлении $p_1={x1}$ атмосфер, медленно опускают на дно '
                    f'водоёма. При этом происходит изотермическое сжатие воздуха до конечного давления $p_2$ (в атмосферах). Работа, совершаемая '
                    f'водой при сжатии воздуха, вычисляется по формуле $A=\\alpha\\nu T\\log_2\\frac{{p_2}}{{p_1}}$, где $\\alpha={tex_num(alpha)}\\,'
                    f'\\frac{{\\text{{Дж}}}}{{\\text{{моль}}\\cdot\\text{{К}}}}$ — постоянная, $T={T}$ К — температура воздуха. Найдите давление $p_2$ '
                    f'воздуха в колоколе, если при сжатии воздуха была совершена работа в {_sp(A)} Дж. Ответ дайте в атмосферах.')
            sol = (f'$\\alpha\\nu T={tex_num(alpha * nu * T)}$, $$\\log_2\\frac{{p_2}}{{p_1}}=\\frac{{{tex_num(A)}}}{{{tex_num(alpha * nu * T)}}}={k},'
                   f'\\qquad p_2={x1}\\cdot 2^{{{k}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        nu = Fraction(rng.randint(2, 9))
        alpha, T = Fraction(29, 5), Fraction(300)
        k = rng.randint(1, 4)
        kind = rng.choice(['V', 'p'])
        x1 = Fraction(rng.choice([16, 20, 24, 32, 40, 48, 64, 80, 96, 120, 160])) if kind == 'V' else Fraction(rng.randint(1, 12))
        return {'kind': kind, 'nu': nu, 'x1': x1, 'alpha': alpha, 'T': T, 'A': alpha * nu * T * k}


class Motorcyclist(Applied):
    """S = v₀t + at²/2 → t (в минутах)"""
    code = '9.motorcycle'
    patterns = [r'со скоростью \$v_0=(\d+)\\text\{км/ч\}(?:\\text)?\$.*?ускорением \$a=(\d+)\{?\\text\{км/ч\}\}?\^2\$.*?удалился от города на (\d+) км']

    def parse(self, m, task):
        return {'v0': _n(m.group(1)), 'a': _n(m.group(2)), 'S': _n(m.group(3))}

    def _t(self, p):
        # a/2 t² + v0 t − S = 0
        A, B, C = p['a'] / 2, p['v0'], -p['S']
        D = B * B - 4 * A * C
        num, den = D.numerator, D.denominator
        r = Fraction(isqrt_exact(num) or -1, isqrt_exact(den) or 1)
        if r * r != D:
            raise ValueError('дискриминант не квадрат')
        return (-B + r) / (2 * A), D, r

    def solve(self, p):
        return self._t(p)[0] * 60

    def build(self, p):
        v0, a, S = p['v0'], p['a'], p['S']
        t, D, r = self._t(p)
        cond = (f'Мотоциклист, движущийся по городу со скоростью $v_0={v0}$ км/ч, выезжает из него и сразу после выезда начинает разгоняться '
                f'с постоянным ускорением $a={a}$ км/ч². Расстояние (в км) от мотоциклиста до города вычисляется по формуле '
                f'$S=v_0t+\\frac{{at^2}}{{2}}$, где $t$ — время в часах, прошедшее после выезда из города. Определите время, прошедшее после '
                f'выезда мотоциклиста из города, если известно, что за это время он удалился от города на {S} км. Ответ дайте в минутах.')
        sol = (f'Подставим: $${v0}t+\\frac{{{a}t^2}}{{2}}={S},\\qquad {tex_num(a / 2)}t^2+{v0}t-{S}=0.$$ '
               f'$D={v0}^2+4\\cdot {tex_num(a / 2)}\\cdot {S}={tex_num(D)}$, положительный корень $$t=\\frac{{-{v0}+{tex_num(r)}}}{{{tex_num(a)}}}'
               f'={tex_num(t)}\\text{{ ч}}={tex_num(t * 60)}\\text{{ мин}}.$$')
        return cond, sol

    def sample(self, rng):
        v0 = Fraction(rng.choice([40, 50, 60, 70, 80, 90]))
        a = Fraction(rng.choice([12, 18, 24, 30, 36, 48, 60, 72, 90, 120]))
        t = Fraction(rng.choice([10, 12, 15, 20, 30, 40, 45]), 60)
        S = v0 * t + a * t * t / 2
        if S.denominator != 1:
            return None
        return {'v0': v0, 'a': a, 'S': S}

    def nice(self, x):
        return frac(x).denominator == 1 and x > 0


class Isotope(Applied):
    """m = m₀·2^{−τ/T} → τ"""
    code = '9.isotope'
    patterns = [r'В начальный момент времени масса изотопа (?:равна )?' + N + r' мг\. Период его полураспада составляет (\d+) мин\w*\. Найдите, через сколько минут масса изотопа будет равна ' + N + ' мг']

    def parse(self, m, task):
        return {'m0': _n(m.group(1)), 'T': _n(m.group(2)), 'm': _n(m.group(3))}

    def solve(self, p):
        return p['T'] * _log2_exact(p['m0'] / p['m'])

    def build(self, p):
        m0, T, m = p['m0'], p['T'], p['m']
        k = _log2_exact(m0 / m)
        cond = (f'В ходе распада радиоактивного изотопа его масса $m$ (в мг) уменьшается по закону $m=m_0\\cdot 2^{{-\\frac{{t}}{{T}}}}$, где $m_0$ '
                f'— начальная масса изотопа (в мг), $t$ — время, прошедшее от начального момента, в минутах, $T$ — период полураспада в минутах. '
                f'В начальный момент времени масса изотопа {dec(m0)} мг. Период его полураспада составляет {T} мин. Найдите, через сколько минут '
                f'масса изотопа будет равна {dec(m)} мг.')
        sol = (f'$${tex_num(m)}={tex_num(m0)}\\cdot 2^{{-\\frac{{t}}{{{T}}}}},\\qquad 2^{{-\\frac{{t}}{{{T}}}}}=\\frac{{{tex_num(m)}}}{{{tex_num(m0)}}}'
               f'=\\frac{{1}}{{{2 ** k}}}=2^{{-{k}}}.$$ Значит, $\\frac{{t}}{{{T}}}={k}$ и $t={self.solve(p)}$ мин.')
        return cond, sol

    def sample(self, rng):
        k = rng.randint(1, 5)
        m = Fraction(rng.choice([5, 6, 7, 9, 10, 12, 15, 20, 25, 30, 40, 50]), rng.choice([1, 1, 2]))
        return {'m0': m * 2 ** k, 'T': Fraction(rng.choice([2, 3, 4, 5, 6, 7, 8, 10, 12, 15])), 'm': m}


class DopplerApproach(Applied):
    """f = f₀(c+u)/(c−v) → c"""
    code = '9.doppler'
    patterns = [r'f=f_0·\\frac\{c\+u\}\{c-v\}\$, где \$f_0=(\d+)\\text\{Гц\}\$.*?\$u=(\d+)\\text\{м\}/\\text\{с\}\$ и \$v=(\d+)\\text\{м\}/\\text\{с\}\$ — скорости (источника и приёмника|приёмника и источника).*?будет равна (\d+) Гц']

    def parse(self, m, task):
        u, v = _n(m.group(2)), _n(m.group(3))
        if m.group(4) == 'приёмника и источника':
            pass  # в формуле u — источник, v — приёмник, обозначения в тексте не меняют формулы
        return {'f0': _n(m.group(1)), 'u': u, 'v': v, 'f': _n(m.group(5))}

    def solve(self, p):
        # f(c − v) = f₀(c + u) → c(f − f₀) = f₀u + fv
        return (p['f0'] * p['u'] + p['f'] * p['v']) / (p['f'] - p['f0'])

    def build(self, p):
        f0, u, v, f = p['f0'], p['u'], p['v'], p['f']
        cond = (f'При сближении источника и приёмника звуковых сигналов, движущихся в некоторой среде по прямой навстречу друг другу со скоростями '
                f'$u$ и $v$ (в м/с) соответственно, частота звукового сигнала $f$ (в Гц), регистрируемого приёмником, вычисляется по формуле '
                f'$f=f_0\\cdot\\frac{{c+u}}{{c-v}}$, где $f_0={f0}$ Гц — частота исходного сигнала, $c$ — скорость распространения сигнала в среде '
                f'(в м/с), а $u={u}$ м/с и $v={v}$ м/с — скорости источника и приёмника относительно среды. При какой скорости распространения '
                f'сигнала в среде частота сигнала в приёмнике будет равна {f} Гц? Ответ дайте в м/с.')
        c = self.solve(p)
        sol = (f'$${f}={f0}\\cdot\\frac{{c+{u}}}{{c-{v}}},\\qquad {f}(c-{v})={f0}(c+{u}),\\qquad {f - f0}c={f0 * u}+{f * v}={f0 * u + f * v},$$ '
               f'откуда $c={tex_num(c)}$ м/с.')
        return cond, sol

    def sample(self, rng):
        f0 = Fraction(rng.choice([120, 140, 150, 160, 170, 180, 200]))
        u, v = Fraction(rng.randint(5, 15)), Fraction(rng.randint(5, 15))
        c = Fraction(rng.choice([290, 300, 310, 320, 330, 340, 350, 360, 380, 400]))
        f = f0 * (c + u) / (c - v)
        if f.denominator != 1:
            return None
        return {'f0': f0, 'u': u, 'v': v, 'f': f}


class Lens(Applied):
    """1/d₁ + 1/d₂ = 1/f: наименьшее d₁ при наибольшем d₂"""
    code = '9.lens'
    patterns = [r'фокусным расстоянием[^$]*\$f=(\d+)\$ см\. Расстояние \$d_1\$ от линзы до лампочки может изменяться в пределах от (\d+) см до (\d+) см, а расстояние \$d_2\$ от линзы до экрана — в пределах от (\d+) см до (\d+) см']

    def parse(self, m, task):
        return {'f': _n(m.group(1)), 'd1': (_n(m.group(2)), _n(m.group(3))), 'd2': (_n(m.group(4)), _n(m.group(5)))}

    def solve(self, p):
        d1 = 1 / (1 / p['f'] - 1 / p['d2'][1])
        if not (p['d1'][0] <= d1 <= p['d1'][1]):
            raise ValueError('вне диапазона')
        return d1

    def build(self, p):
        f, (a, b), (c, e) = p['f'], p['d1'], p['d2']
        d1 = self.solve(p)
        cond = (f'Для получения на экране увеличенного изображения лампочки в лаборатории используется собирающая линза с фокусным расстоянием '
                f'$f={f}$ см. Расстояние $d_1$ от линзы до лампочки может изменяться в пределах от {a} см до {b} см, а расстояние $d_2$ от линзы '
                f'до экрана — в пределах от {c} см до {e} см. Изображение на экране будет чётким, если выполнено соотношение '
                f'$\\frac{{1}}{{d_1}}+\\frac{{1}}{{d_2}}=\\frac{{1}}{{f}}$. На каком наименьшем расстоянии от линзы нужно поместить лампочку, '
                f'чтобы её изображение на экране было чётким? Ответ дайте в сантиметрах.')
        sol = (f'$\\frac{{1}}{{d_1}}=\\frac{{1}}{{f}}-\\frac{{1}}{{d_2}}$: чем больше $d_2$, тем больше $\\frac{{1}}{{d_1}}$ — и тем меньше $d_1$. '
               f'Берём наибольшее $d_2={e}$: $$\\frac{{1}}{{d_1}}=\\frac{{1}}{{{f}}}-\\frac{{1}}{{{e}}}=\\frac{{{e - f}}}{{{f * e}}},\\qquad '
               f'd_1={tex_num(d1)}.$$ Это значение лежит в допустимых пределах от {a} до {b} см.')
        return cond, sol

    def sample(self, rng):
        f = Fraction(rng.choice([20, 24, 25, 30, 35, 36, 40, 45, 50]))
        d1 = Fraction(rng.randint(int(f) + 2, int(f) * 2))
        d2 = 1 / (1 / f - 1 / d1)
        if d2.denominator != 1:
            return None
        return {'f': f, 'd1': (d1 - rng.randint(2, 8), d1 + rng.randint(5, 15)), 'd2': (d2 - rng.randint(10, 30), d2)}


class StefanBoltzmann(Applied):
    """P = σST⁴ → T"""
    code = '9.stefan'
    patterns = [r'σ\}=5\{,\}7·10\^\{-8\}.*?площадь поверхности некоторой звезды равна \$\\frac\{1\}\{(\d+)\}·10\^\{(\d+)\}\\text\{м\}\^2\$, а мощность её излучения равна \$' + TN + r'·10\^\{(\d+)\}']

    def parse(self, m, task):
        return {'den': int(m.group(1)), 'es': int(m.group(2)), 'P': _n(m.group(3)), 'ep': int(m.group(4))}

    def solve(self, p):
        sigma = Fraction(57, 10) * Fraction(10) ** -8
        S = Fraction(10) ** p['es'] / p['den']
        P = p['P'] * Fraction(10) ** p['ep']
        t4 = P / (sigma * S)
        r = round(float(t4) ** 0.25)
        if Fraction(r) ** 4 != t4:
            raise ValueError('не точная четвёртая степень')
        return Fraction(r)

    def build(self, p):
        T = self.solve(p)
        cond = (f'Для определения эффективной температуры звёзд используют закон Стефана — Больцмана, согласно которому $P=\\sigma ST^4$, где $P$ — '
                f'мощность излучения звезды (в Вт), $\\sigma=5{{,}}7\\cdot 10^{{-8}}\\,\\frac{{\\text{{Вт}}}}{{\\text{{м}}^2\\cdot\\text{{К}}^4}}$ — '
                f'постоянная, $S$ — площадь поверхности звезды (в м²), а $T$ — температура (в К). Известно, что площадь поверхности некоторой '
                f'звезды равна $\\frac{{1}}{{{p["den"]}}}\\cdot 10^{{{p["es"]}}}$ м², а мощность её излучения равна ${tex_num(p["P"])}\\cdot 10^{{{p["ep"]}}}$ Вт. '
                f'Найдите температуру этой звезды. Ответ дайте в кельвинах.')
        sol = (f'$$T^4=\\frac{{P}}{{\\sigma S}}=\\frac{{{tex_num(p["P"])}\\cdot 10^{{{p["ep"]}}}\\cdot {p["den"]}}}{{5{{,}}7\\cdot 10^{{-8}}\\cdot 10^{{{p["es"]}}}}}'
               f'={tex_num(T ** 4)},\\qquad T=\\sqrt[4]{{{tex_num(T ** 4)}}}={tex_num(T)}.$$')
        return cond, sol

    def sample(self, rng):
        T = rng.choice([2000, 3000, 4000, 5000, 6000, 7000])
        root = rng.choice([2, 3, 4, 5, 6, 7])
        den = root ** 4
        es = rng.choice([20, 21, 22])
        # P = σ S T⁴ = 5,7·10⁻⁸ · 10^es/den · T⁴
        P = Fraction(57, 10) * Fraction(10) ** (es - 8) * Fraction(T) ** 4 / den
        ep = len(str(int(P))) - 1  # мантисса от 1 до 10
        mant = P / Fraction(10) ** ep
        if not (1 <= mant < 100) or not nice_number(mant, 3):
            return None
        return {'den': den, 'es': es, 'P': mant, 'ep': ep}

    def nice(self, x):
        return frac(x).denominator == 1


class TrainWhistle(Applied):
    """f = f₀/(1 − v/c) ≥ f₀ + Δ → минимальная скорость v"""
    code = '9.whistle'
    patterns = [r'гудок с частотой \$f_0=(\d+)\\text\{Гц\}\$.*?отличаются не менее чем на (\d+) Гц.*?\$c=(\d+)\\text\{м/с\}']

    def parse(self, m, task):
        return {'f0': _n(m.group(1)), 'df': _n(m.group(2)), 'c': _n(m.group(3))}

    def solve(self, p):
        return p['c'] * (1 - p['f0'] / (p['f0'] + p['df']))

    def build(self, p):
        f0, df, c = p['f0'], p['df'], p['c']
        cond = (f'Перед отправкой тепловоз издал гудок с частотой $f_0={f0}$ Гц. Чуть позже гудок издал подъезжающий к платформе тепловоз. Из-за '
                f'эффекта Доплера частота второго гудка $f$ (в Гц) больше первого: она зависит от скорости тепловоза $v$ (в м/с) по закону '
                f'$f(v)=\\frac{{f_0}}{{1-\\frac{{v}}{{c}}}}$ (Гц), где $c$ — скорость звука (в м/с). Человек, стоящий на платформе, различает '
                f'сигналы по тону, если они отличаются не менее чем на {df} Гц. Определите, с какой минимальной скоростью приближался к платформе '
                f'тепловоз, если человек смог различить сигналы, а $c={c}$ м/с. Ответ дайте в м/с.')
        sol = (f'Нужно $f-f_0\\ge {df}$, то есть $f\\ge {f0 + df}$. Функция $f(v)$ возрастает, наименьшая скорость — при равенстве: '
               f'$$\\frac{{{f0}}}{{1-\\frac{{v}}{{{c}}}}}={f0 + df},\\qquad 1-\\frac{{v}}{{{c}}}=\\frac{{{f0}}}{{{f0 + df}}},\\qquad '
               f'v={c}\\cdot\\frac{{{df}}}{{{f0 + df}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        c = Fraction(rng.choice([300, 320, 330, 340]))
        f0 = Fraction(rng.randint(140, 600))
        df = Fraction(rng.randint(3, 12))
        return {'f0': f0, 'df': df, 'c': c}


class ParallelResistors(Applied):
    """R = R₁R₂/(R₁+R₂) ≥ R₀ → наименьшее R₂"""
    code = '9.parallel'
    patterns = [r'сопротивление которой составляет [^$]*\$R_1=(\d+)\$ Ом.*?общее сопротивление в ней должно быть не меньше (\d+) Ом']

    def parse(self, m, task):
        return {'R1': _n(m.group(1)), 'R0': _n(m.group(2))}

    def solve(self, p):
        if p['R1'] <= p['R0']:
            raise ValueError('R1 ≤ R0')
        return p['R1'] * p['R0'] / (p['R1'] - p['R0'])

    def build(self, p):
        R1, R0 = p['R1'], p['R0']
        cond = (f'В розетку электросети подключена электрическая духовка, сопротивление которой составляет $R_1={R1}$ Ом. Параллельно с ней в '
                f'розетку предполагается подключить электрообогреватель, сопротивление которого $R_2$ (в Ом). При параллельном соединении двух '
                f'электроприборов с сопротивлениями $R_1$ и $R_2$ их общее сопротивление $R$ вычисляется по формуле $R=\\frac{{R_1R_2}}{{R_1+R_2}}$. '
                f'Для нормального функционирования электросети общее сопротивление в ней должно быть не меньше {R0} Ом. Определите наименьшее '
                f'возможное сопротивление электрообогревателя. Ответ дайте в омах.')
        sol = (f'Общее сопротивление растёт вместе с $R_2$, поэтому наименьшее $R_2$ даёт равенство: $$\\frac{{{R1}R_2}}{{{R1}+R_2}}={R0},\\qquad '
               f'{R1}R_2={R0}\\cdot {R1}+{R0}R_2,\\qquad {R1 - R0}R_2={R0 * R1},\\qquad R_2={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        R1 = Fraction(rng.choice([20, 24, 30, 36, 40, 45, 50, 60, 72, 90]))
        R0 = Fraction(rng.randint(8, int(R1) - 4))
        return {'R1': R1, 'R0': R0}


class Collision(Applied):
    """Q = mv²sin²α → угол 2α"""
    code = '9.collision'
    patterns = [r'Два тела, массой \$m=(\d+)\\text\{кг\}\$ каждое, движутся с одинаковой скоростью \$v=(\d+)\\text\{м\}/\\text\{[cс]\}\$.*?выделилась энергия, равная (\d+) Дж']

    ANGLES = {Fraction(1, 4): 30, Fraction(1, 2): 45, Fraction(3, 4): 60, Fraction(1): 90}

    def parse(self, m, task):
        return {'m': _n(m.group(1)), 'v': _n(m.group(2)), 'Q': _n(m.group(3))}

    def solve(self, p):
        s2 = p['Q'] / (p['m'] * p['v'] ** 2)
        return 2 * self.ANGLES[s2]

    def build(self, p):
        m, v, Q = p['m'], p['v'], p['Q']
        s2 = Q / (m * v * v)
        a = self.ANGLES[s2]
        s = {30: '\\frac{1}{2}', 45: '\\frac{\\sqrt{2}}{2}', 60: '\\frac{\\sqrt{3}}{2}', 90: '1'}[a]
        cond = (f'Два тела, массой $m={m}$ кг каждое, движутся с одинаковой скоростью $v={v}$ м/с под углом $2\\alpha$ друг к другу. Энергия '
                f'(в Дж), выделяющаяся при их абсолютно неупругом соударении, вычисляется по формуле $Q=mv^2\\sin^2\\alpha$. Найдите, под каким '
                f'углом $2\\alpha$ должны двигаться тела, чтобы в результате соударения выделилась энергия, равная {Q} Дж. Ответ дайте в градусах.')
        sol = (f'$$\\sin^2\\alpha=\\frac{{Q}}{{mv^2}}=\\frac{{{Q}}}{{{m}\\cdot {v}^2}}={tex_frac(s2)},\\qquad \\sin\\alpha={s}.$$ '
               f'Острый угол $\\alpha={a}^\\circ$, значит $2\\alpha={2 * a}^\\circ$.')
        return cond, sol

    def sample(self, rng):
        s2 = rng.choice([Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)])
        m, v = Fraction(rng.randint(2, 10)), Fraction(rng.randint(2, 12))
        Q = m * v * v * s2
        return {'m': m, 'v': v, 'Q': Q} if Q.denominator == 1 else None


class QuadraticTime(Applied):
    """
    Квадратичный закон движения/нагрева: h(t) = h₀ + bt − 5t² (сколько секунд не ниже H),
    T(t) = T₀ + bt + at² (через какое наибольшее время отключить), φ = ωt + βt²/2 (время), H(t) = at² + bt + H₀ (сколько минут вытекает)
    """
    code = '9.quadratic'
    patterns = [r'(?P<ball>h\(t\)=' + TN + r'\+' + TN + r't-5t\^2\$.*?на высоте не менее (\d+) метр)',
                r'(?P<heat>T_0=(\d+)\\text\{К\}\$, \$a=(-\d+)\\text\{К\}/\{\\text\{мин\}\}\^2\$, \$b=(\d+)\\text\{К\}/\\text\{мин\}\$\. Известно, что при температуре нагревательного элемента свыше (\d+) К)',
                r'(?P<winch>\\text\{ω\}=(\d+)\\text\{град\}\./\\text\{мин\}\$.*?\\text\{β\}=(\d+)\\text\{град\}\./\{\\text\{мин\}\}\^2\$.*?достиг \$(\d+)\^\\circ\$)',
                r'(?P<tank>H_0=(\d+)\\text\{м\}\$ — начальный уровень воды, \$a=\\frac\{1\}\{(\d+)\}\\text\{м\}/\{\\text\{мин\}\}\^2\$ и \$b=-\\frac\{(\d+)\}\{(\d+)\}\\text\{м\}/\\text\{мин\}\$)']

    def parse(self, m, task):
        g = m.groups()
        if m.groupdict().get('ball'):
            return {'kind': 'ball', 'h0': _n(g[1]), 'b': _n(g[2]), 'H': _n(g[3])}
        if m.groupdict().get('heat'):
            gs = re.search(r'T_0=(\d+).*?a=(-\d+).*?b=(\d+).*?свыше (\d+) К', m.group(0))
            return {'kind': 'heat', 'T0': _n(gs.group(1)), 'a': _n(gs.group(2)), 'b': _n(gs.group(3)), 'Tmax': _n(gs.group(4))}
        if m.groupdict().get('winch'):
            gs = re.search(r'ω\}=(\d+).*?β\}=(\d+).*?достиг \$(\d+)', m.group(0))
            return {'kind': 'winch', 'w': _n(gs.group(1)), 'beta': _n(gs.group(2)), 'phi': _n(gs.group(3))}
        gs = re.search(r'H_0=(\d+).*?\\frac\{1\}\{(\d+)\}.*?b=-\\frac\{(\d+)\}\{(\d+)\}', m.group(0))
        return {'kind': 'tank', 'H0': _n(gs.group(1)), 'a': Fraction(1) / _n(gs.group(2)), 'b': -_n(gs.group(3)) / _n(gs.group(4))}

    @staticmethod
    def _roots(A, B, C):
        D = B * B - 4 * A * C
        r = Fraction(isqrt_exact(D.numerator) or -1, isqrt_exact(D.denominator) or 1)
        if D < 0 or r * r != D:
            raise ValueError('корни иррациональные')
        return sorted([(-B - r) / (2 * A), (-B + r) / (2 * A)]), D, r

    def solve(self, p):
        k = p['kind']
        if k == 'ball':
            (t1, t2), _, _ = self._roots(Fraction(-5), p['b'], p['h0'] - p['H'])
            return t2 - t1
        if k == 'heat':
            (t1, t2), _, _ = self._roots(p['a'], p['b'], p['T0'] - p['Tmax'])
            return min(t for t in (t1, t2) if t > 0)
        if k == 'winch':
            (t1, t2), _, _ = self._roots(p['beta'] / 2, p['w'], -p['phi'])
            return t2
        D = p['b'] ** 2 - 4 * p['a'] * p['H0']
        if D != 0:
            raise ValueError('ожидали двойной корень')
        return -p['b'] / (2 * p['a'])

    def build(self, p):
        k = p['kind']
        ans = self.solve(p)
        if k == 'ball':
            h0, b, H = p['h0'], p['b'], p['H']
            (t1, t2), D, r = self._roots(Fraction(-5), b, h0 - H)
            cond = (f'Высота над землёй подброшенного вверх мяча меняется по закону $h(t)={tex_num(h0)}+{tex_num(b)}t-5t^2$, где $h$ — высота в метрах, '
                    f'$t$ — время в секундах, прошедшее с момента броска. Сколько секунд мяч будет находиться на высоте не менее {H} метров?')
            sol = (f'Решим неравенство $${tex_num(h0)}+{tex_num(b)}t-5t^2\\ge {H},\\qquad 5t^2-{tex_num(b)}t+{tex_num(H - h0)}\\le 0.$$ '
                   f'Корни: $t_1={tex_num(t1)}$, $t_2={tex_num(t2)}$. Мяч находится на этой высоте при $t\\in[{tex_num(t1)};{tex_num(t2)}]$ — '
                   f'это ${tex_num(t2)}-{tex_num(t1)}={tex_num(ans)}$ с.').replace('+-', '-')
        elif k == 'heat':
            T0, a, b, Tm = p['T0'], p['a'], p['b'], p['Tmax']
            (t1, t2), _, _ = self._roots(a, b, T0 - Tm)
            cond = (f'Для нагревательного элемента некоторого прибора экспериментально была получена зависимость температуры (в К) от времени работы: '
                    f'$T(t)=T_0+bt+at^2$, где $t$ — время (в мин.), $T_0={T0}$ К, $a={a}$ К/мин², $b={b}$ К/мин. Известно, что при температуре '
                    f'нагревательного элемента свыше {Tm} К прибор может испортиться, поэтому его нужно отключить. Найдите, через какое наибольшее '
                    f'время после начала работы нужно отключить прибор. Ответ дайте в минутах.')
            sol = (f'Найдём, когда температура впервые достигнет {Tm} К: $${T0}+{b}t{a:+}t^2={Tm},\\qquad {-a}t^2-{b}t+{Tm - T0}=0.$$ '
                   f'Корни ${tex_num(t1)}$ и ${tex_num(t2)}$; температура растёт с самого начала, поэтому прибор нужно отключить не позднее, чем через '
                   f'${tex_num(ans)}$ мин.')
        elif k == 'winch':
            w, beta, phi = p['w'], p['beta'], p['phi']
            cond = (f'Для сматывания кабеля на заводе используют лебёдку, которая равноускоренно наматывает кабель на катушку. Угол, на который '
                    f'поворачивается катушка, изменяется со временем по закону $\\varphi=\\omega t+\\frac{{\\beta t^2}}{{2}}$, где $t$ — время в минутах, '
                    f'прошедшее после начала работы лебёдки, $\\omega={w}$ град/мин — начальная угловая скорость вращения катушки, а $\\beta={beta}$ '
                    f'град/мин² — угловое ускорение, с которым наматывается кабель. Определите время, прошедшее после начала работы лебёдки, если '
                    f'известно, что за это время угол намотки $\\varphi$ достиг ${phi}^\\circ$. Ответ дайте в минутах.')
            sol = (f'$${w}t+\\frac{{{beta}t^2}}{{2}}={phi},\\qquad {tex_num(beta / 2)}t^2+{w}t-{phi}=0.$$ Положительный корень $t={tex_num(ans)}$ мин.')
        else:
            H0, a, b = p['H0'], p['a'], p['b']
            cond = (f'В боковой стенке высокого цилиндрического бака у самого дна закреплён кран. После его открытия вода начинает вытекать из бака, '
                    f'при этом высота столба воды в нём меняется по закону $H(t)=at^2+bt+H_0$, где $H$ — высота столба воды в метрах, $H_0={H0}$ м — '
                    f'начальный уровень воды, $a={tex_frac(a)}$ м/мин² и $b={tex_frac(b)}$ м/мин — постоянные, $t$ — время в минутах, прошедшее '
                    f'с момента открытия крана. Сколько минут вода будет вытекать из бака?')
            sol = (f'Вода вытекает, пока $H(t)>0$. Уравнение $${tex_frac(a)}t^2{"+" if b > 0 else "-"}{tex_frac(abs(b))}t+{H0}=0$$ имеет дискриминант '
                   f'${par(b)}^2-4\\cdot {tex_frac(a)}\\cdot {H0}=0$, единственный корень $t=-\\frac{{b}}{{2a}}={tex_num(ans)}$ мин.')
        return cond, sol

    def sample(self, rng):
        kind = rng.choice(['ball', 'heat', 'winch', 'tank'])
        if kind == 'ball':
            t1, t2 = sorted(rng.sample([Fraction(x, 5) for x in range(1, 16)], 2))
            # −5(t−t1)(t−t2) + H = −5t² + 5(t1+t2)t − 5t1t2 + H
            H = Fraction(rng.randint(2, 8))
            h0 = H - 5 * t1 * t2
            b = 5 * (t1 + t2)
            if h0 <= 0 or h0 > 3:
                return None
            return {'kind': kind, 'h0': h0, 'b': b, 'H': H}
        if kind == 'heat':
            a = Fraction(-rng.choice([5, 10, 20, 25, 30]))
            t1, t2 = sorted(rng.sample(range(2, 20), 2))
            dT = -a * t1 * t2
            b = -a * (t1 + t2)
            T0 = Fraction(rng.choice([1200, 1300, 1400, 1500, 1600]))
            return {'kind': kind, 'T0': T0, 'a': a, 'b': b, 'Tmax': T0 + dT}
        if kind == 'winch':
            beta = Fraction(rng.choice([2, 4, 6, 8, 10]))
            w = Fraction(rng.choice([10, 15, 20, 25, 30, 40]))
            t = Fraction(rng.randint(5, 30))
            return {'kind': kind, 'w': w, 'beta': beta, 'phi': w * t + beta * t * t / 2}
        T = rng.choice([12, 15, 20, 24, 30, 40, 48, 60])
        H0 = Fraction(rng.choice([2, 3, 4, 5, 6, 8, 9]))
        # H(t) = H0(1 − t/T)² = H0/T² t² − 2H0/T t + H0
        return {'kind': kind, 'H0': H0, 'a': H0 / T ** 2, 'b': -2 * H0 / T}


class Bathyscaphe(Applied):
    """v = c(f − f₀)/(f + f₀) → f"""
    code = '9.bathyscaphe'
    patterns = [r'испускает ультразвуковые импульсы частотой (\d+) МГц\. Скорость погружения батискафа.*?\$c=(\d+)\\text\{м\}/\\text\{с\}\$.*?скорость погружения батискафа равна (\d+) м/с']

    def parse(self, m, task):
        return {'f0': _n(m.group(1)), 'c': _n(m.group(2)), 'v': _n(m.group(3))}

    def solve(self, p):
        return p['f0'] * (p['c'] + p['v']) / (p['c'] - p['v'])

    def build(self, p):
        f0, c, v = p['f0'], p['c'], p['v']
        cond = (f'Локатор батискафа, равномерно погружающегося вертикально вниз, испускает ультразвуковые импульсы частотой {f0} МГц. Скорость '
                f'погружения батискафа $v$ (в м/с) вычисляется по формуле $v=c\\cdot\\frac{{f-f_0}}{{f+f_0}}$, где $c={c}$ м/с — скорость звука '
                f'в воде, $f_0$ — частота испускаемых импульсов (в МГц), $f$ — частота отражённого от дна сигнала (в МГц), регистрируемая '
                f'приёмником. Определите частоту отражённого сигнала, если скорость погружения батискафа равна {v} м/с. Ответ дайте в МГц.')
        sol = (f'$${v}={c}\\cdot\\frac{{f-{f0}}}{{f+{f0}}},\\qquad {v}(f+{f0})={c}(f-{f0}),\\qquad {c - v}f={(c + v) * f0},$$ '
               f'откуда $f={tex_num(self.solve(p))}$ МГц.')
        return cond, sol

    def sample(self, rng):
        c = Fraction(1500)
        v = Fraction(rng.choice([2, 3, 4, 5, 6, 10, 12, 15, 20, 25, 30]))
        f0 = Fraction(rng.randint(100, 800))
        return {'f0': f0, 'c': c, 'v': v}


class Capacitor(Applied):
    """t = αRC·log₂(U₀/U) → U"""
    code = '9.capacitor'
    patterns = [r'ёмкость высоковольтного конденсатора \$C=(\d+)·10\^\{-6\}\\text\{Ф\}.*?сопротивлением \$R=(\d+)·10\^6\\text\{Ом\}.*?\$U_0=(\d+)\\text\{кВ\}.*?\\alpha=' + TN + r'.*?прошло (\d+) секунд']

    def parse(self, m, task):
        return {'C': _n(m.group(1)), 'R': _n(m.group(2)), 'U0': _n(m.group(3)), 'alpha': _n(m.group(4)), 't': _n(m.group(5))}

    def solve(self, p):
        k = p['t'] / (p['alpha'] * p['R'] * p['C'])   # R·C: 10⁶·10⁻⁶ = 1
        if k.denominator != 1:
            raise ValueError('дробный показатель')
        return p['U0'] / 2 ** int(k)

    def build(self, p):
        C, R, U0, a, t = p['C'], p['R'], p['U0'], p['alpha'], p['t']
        k = int(t / (a * R * C))
        cond = (f'В телевизоре ёмкость высоковольтного конденсатора $C={C}\\cdot 10^{{-6}}$ Ф. Параллельно с конденсатором подключён резистор '
                f'с сопротивлением $R={R}\\cdot 10^6$ Ом. Во время работы телевизора напряжение на конденсаторе $U_0={U0}$ кВ. После выключения '
                f'телевизора напряжение на конденсаторе убывает до значения $U$ (в кВ) за время (в секундах), определяемое выражением '
                f'$t=\\alpha RC\\log_2\\frac{{U_0}}{{U}}$, где $\\alpha={tex_num(a)}$ — постоянная. Определите напряжение на конденсаторе, если '
                f'после выключения телевизора прошло {t} секунд. Ответ дайте в киловольтах.')
        sol = (f'$\\alpha RC={tex_num(a)}\\cdot {R}\\cdot 10^6\\cdot {C}\\cdot 10^{{-6}}={tex_num(a * R * C)}$, поэтому '
               f'$$\\log_2\\frac{{{U0}}}{{U}}=\\frac{{{t}}}{{{tex_num(a * R * C)}}}={k},\\qquad U=\\frac{{{U0}}}{{2^{{{k}}}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        C, R = Fraction(rng.randint(2, 9)), Fraction(rng.randint(2, 8))
        a = Fraction(rng.choice([1, 2, 3])) / 2 + 1
        k = rng.randint(1, 4)
        t = a * R * C * k
        U0 = Fraction(rng.choice([8, 12, 16, 20, 24, 32, 40, 48, 64]))
        return {'C': C, 'R': R, 'U0': U0, 'alpha': a, 't': t} if t.denominator == 1 else None


class EMF(Applied):
    """U = εR/(R + r) → R"""
    code = '9.emf'
    patterns = [r'К источнику с ЭДС \$\\text\{ε\}=(\d+)\\text\{В\}\$ и внутренним сопротивлением \$r=(\d+)\\text\{Ом\}\$.*?напряжение на ней будет равно \$(\d+)\\text\{В\}\$']

    def parse(self, m, task):
        return {'e': _n(m.group(1)), 'r': _n(m.group(2)), 'U': _n(m.group(3))}

    def solve(self, p):
        return p['U'] * p['r'] / (p['e'] - p['U'])

    def build(self, p):
        e, r, U = p['e'], p['r'], p['U']
        cond = (f'К источнику с ЭДС $\\varepsilon={e}$ В и внутренним сопротивлением $r={r}$ Ом хотят подключить нагрузку с сопротивлением $R$ '
                f'(в Ом). Напряжение (в В) на этой нагрузке вычисляется по формуле $U=\\frac{{\\varepsilon R}}{{R+r}}$. При каком значении '
                f'сопротивления нагрузки напряжение на ней будет равно {U} В? Ответ дайте в омах.')
        sol = (f'$${U}=\\frac{{{e}R}}{{R+{r}}},\\qquad {U}R+{U * r}={e}R,\\qquad {e - U}R={U * r},\\qquad R={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        e = Fraction(rng.choice([60, 90, 100, 120, 150, 180, 200, 220, 240]))
        r = Fraction(rng.randint(1, 4))
        U = Fraction(rng.randint(int(e * 0.5), int(e) - 5))
        return {'e': e, 'r': r, 'U': U}


class SimpleFormula(Applied):
    """Горизонт l = √(2Rh), адиабата pV^k = C, закон Ома I = U/R"""
    code = '9.formula'
    patterns = [r'(?P<horizon>l=\\sqrt\{2Rh\}\$, где \$R=(\d+)\\text\{км\}\$.*?горизонт виден на расстоянии (\d+) километр)',
                r'(?P<adiabat>pV\^k=(\d+)\{,\}(\d)·10\^(\d+)\\text\{Па\}·\\text\{м\}\^5\$.*?k=\\frac\{5\}\{3\}.*?при давлении \$p\$, равном \$(\d+)·10\^(\d+)\\text\{Па\})',
                r'(?P<ohm>сила тока превышает (\d+) А\..*?с напряжением (\d+) В)']

    def parse(self, m, task):
        g = m.groupdict()
        if g.get('horizon'):
            r = re.search(r'R=(\d+).*?расстоянии (\d+)', m.group(0))
            return {'kind': 'horizon', 'R': _n(r.group(1)), 'l': _n(r.group(2))}
        if g.get('adiabat'):
            r = re.search(r'pV\^k=(\d+)\{,\}(\d)·10\^(\d+).*?равном \$(\d+)·10\^(\d+)', m.group(0))
            C = Fraction(f'{r.group(1)}.{r.group(2)}') * Fraction(10) ** int(r.group(3))
            P = Fraction(int(r.group(4))) * Fraction(10) ** int(r.group(5))
            return {'kind': 'adiabat', 'C': C, 'p': P}
        r = re.search(r'превышает (\d+) А.*?напряжением (\d+) В', m.group(0))
        return {'kind': 'ohm', 'I': _n(r.group(1)), 'U': _n(r.group(2))}

    def solve(self, p):
        if p['kind'] == 'horizon':
            return p['l'] ** 2 / (2 * p['R'])
        if p['kind'] == 'adiabat':
            q = p['C'] / p['p']            # V^{5/3} = q → V = q^{3/5}
            v = round(float(q) ** 0.6)
            if Fraction(v) ** 5 != q ** 3:
                raise ValueError('не точная степень')
            return Fraction(v)
        return p['U'] / p['I']

    def build(self, p):
        k = p['kind']
        if k == 'horizon':
            R, l = p['R'], p['l']
            cond = (f'Расстояние от наблюдателя, находящегося на небольшой высоте $h$ (в километрах) над землёй, до наблюдаемой им линии горизонта '
                    f'вычисляется по формуле $l=\\sqrt{{2Rh}}$, где $R={R}$ км — радиус Земли. С какой высоты горизонт виден на расстоянии {l} '
                    f'километров? Ответ дайте в километрах.')
            sol = f'$$l^2=2Rh,\\qquad h=\\frac{{l^2}}{{2R}}=\\frac{{{l}^2}}{{2\\cdot {R}}}=\\frac{{{l * l}}}{{{2 * R}}}={tex_num(self.solve(p))}.$$'
        elif k == 'adiabat':
            C, P = p['C'], p['p']
            cond = (f'При адиабатическом процессе для идеального газа выполняется закон $pV^k={_sci(C)}$ Па·м⁵, где $p$ — давление в газе в паскалях, '
                    f'$V$ — объём газа (в м³), $k=\\frac{{5}}{{3}}$. Найдите, какой объём $V$ (в м³) будет занимать газ при давлении $p$, равном '
                    f'${_sci(P)}$ Па.')
            q = C / P
            sol = (f'$$V^{{\\frac{{5}}{{3}}}}=\\frac{{{_sci(C)}}}{{{_sci(P)}}}={tex_num(q)},\\qquad V=\\left({tex_num(q)}\\right)^{{\\frac{{3}}{{5}}}}'
                   f'={tex_num(self.solve(p))},$$ так как ${tex_num(self.solve(p))}^5={tex_num(self.solve(p) ** 5)}={tex_num(q)}^3$.')
        else:
            I, U = p['I'], p['U']
            cond = (f'Сила тока $I$ (в А) в электросети вычисляется по закону Ома: $I=\\frac{{U}}{{R}}$, где $U$ — напряжение электросети (в В), $R$ — '
                    f'сопротивление подключаемого электроприбора (в Ом). Электросеть прекращает работать, если сила тока превышает {I} А. Определите, '
                    f'какое наименьшее сопротивление может быть у электроприбора, подключаемого к электросети с напряжением {U} В, чтобы электросеть '
                    f'продолжала работать. Ответ дайте в омах.')
            sol = (f'Нужно $\\frac{{{U}}}{{R}}\\le {I}$, то есть $R\\ge\\frac{{{U}}}{{{I}}}={tex_num(self.solve(p))}$.')
        return cond, sol

    def sample(self, rng):
        k = rng.choice(['horizon', 'adiabat', 'ohm'])
        if k == 'horizon':
            return {'kind': k, 'R': Fraction(6400), 'l': Fraction(rng.choice([16, 32, 40, 48, 64, 80, 96, 112, 128, 160]))}
        if k == 'adiabat':
            V = rng.choice([2, 4, 8, 16, 32])
            P = Fraction(rng.choice([1, 2, 4, 5, 8])) * 10 ** rng.choice([4, 5])
            C = P * Fraction(V) ** 5 ** 1
            # V^{5/3} = C/P → C = P·V^{5/3}: берём V = t³, тогда V^{5/3} = t⁵
            t = rng.choice([2, 3, 4])
            C = P * t ** 5
            return {'kind': k, 'C': C, 'p': P}
        return {'kind': k, 'I': Fraction(rng.choice([2, 4, 5, 8, 10])), 'U': Fraction(220)}


def _sci(x: Fraction) -> str:
    """6 400 000 → 6{,}4\\cdot 10^6"""
    e = 0
    while x >= 10:
        x /= 10
        e += 1
    return f'{tex_num(x)}\\cdot 10^{{{e}}}' if e else tex_num(x)


TEMPLATES = [CarAcceleration(), DivingBell(), Motorcyclist(), Isotope(), DopplerApproach(), Lens(), StefanBoltzmann(), TrainWhistle(),
             ParallelResistors(), Collision(), QuadraticTime(), Bathyscaphe(), Capacitor(), EMF(), SimpleFormula()]
EXTRA = []
