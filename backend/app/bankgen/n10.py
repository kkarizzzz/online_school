"""№ 10. Текстовые задачи"""
import math
import random
import re
from fractions import Fraction

from app.bankgen.core import Rendered, Template, dec, frac, isqrt_exact, nice_number, plural, tex_num

N = r'(\d+(?:[,.]\d+)?)'


def _n(s: str) -> Fraction:
    return Fraction(s.replace(',', '.'))


def _hours(n) -> str:
    return f'{dec(n)} {plural(int(n), "час", "часа", "часов")}' if frac(n).denominator == 1 else f'{dec(n)} часа'


def _roots(a: Fraction, b: Fraction, c: Fraction) -> tuple[list[Fraction], Fraction, Fraction]:
    """Рациональные корни ax² + bx + c = 0, дискриминант и его корень"""
    D = b * b - 4 * a * c
    if D < 0:
        raise ValueError('нет корней')
    r = Fraction(isqrt_exact(D.numerator) or -1, isqrt_exact(D.denominator) or 1)
    if r < 0 or r * r != D:
        raise ValueError('корни иррациональные')
    return sorted({(-b - r) / (2 * a), (-b + r) / (2 * a)}), D, r


def _positive(a, b, c) -> Fraction:
    roots, _, _ = _roots(a, b, c)
    pos = [x for x in roots if x > 0]
    if len(pos) != 1:
        raise ValueError('не один положительный корень')
    return pos[0]


def _quad_text(a, b, c, var='x') -> str:
    from app.bankgen.core import poly
    return poly([a, b, c], var) + '=0'


class Word(Template):
    number = 10
    topic = 'Текстовые задачи'

    def render(self, p):
        cond, sol = self.build(p)
        return Rendered(cond, sol + f'\n\n**Ответ:** {dec(self.solve(p))}.')

    def nice(self, x):
        return nice_number(x, 1) and x > 0


# ---------------------------------------------------------------------------
# Движение
# ---------------------------------------------------------------------------

class BoatRoundTrip(Word):
    """S против течения и обратно, обратно на Δt быстрее: v ↔ u"""
    topic, code = 'Движение по воде', '10.boat'
    patterns = [r'Моторная лодка прошла против течения реки (\d+) км и вернулась в пункт отправления, затратив на обратный путь на (\d+) час\w* меньше\. '
                r'Найдите скорость (течения|лодки в неподвижной воде), если скорость (?:лодки в неподвижной воде|течения) равна (\d+) км/ч']

    def parse(self, m, task):
        return {'S': _n(m.group(1)), 'dt': _n(m.group(2)), 'ask': 'u' if m.group(3) == 'течения' else 'v', 'known': _n(m.group(4))}

    def solve(self, p):
        S, dt, k = p['S'], p['dt'], p['known']
        # S/(v−u) − S/(v+u) = dt ⇔ 2Su = dt(v² − u²)
        if p['ask'] == 'u':
            return _positive(dt, 2 * S, -dt * k * k)      # dt u² + 2S u − dt v² = 0
        return _positive(dt, Fraction(0), -dt * k * k - 2 * S * k)  # dt v² − (dt u² + 2Su) = 0

    def build(self, p):
        S, dt, k, x = p['S'], p['dt'], p['known'], self.solve(p)
        if p['ask'] == 'u':
            cond = (f'Моторная лодка прошла против течения реки {S} км и вернулась в пункт отправления, затратив на обратный путь на {_hours(dt)} меньше. '
                    f'Найдите скорость течения, если скорость лодки в неподвижной воде равна {k} км/ч. Ответ дайте в км/ч.')
            sol = (f'Пусть скорость течения $u$ км/ч. Против течения лодка идёт со скоростью ${k}-u$, по течению — ${k}+u$: '
                   f'$$\\frac{{{S}}}{{{k}-u}}-\\frac{{{S}}}{{{k}+u}}={dt}.$$ Приводим к общему знаменателю: ${2 * S}u={dt}({k * k}-u^2)$, '
                   f'то есть $${_quad_text(dt, 2 * S, -dt * k * k, "u")}.$$ Положительный корень $u={tex_num(x)}$.')
        else:
            cond = (f'Моторная лодка прошла против течения реки {S} км и вернулась в пункт отправления, затратив на обратный путь на {_hours(dt)} меньше. '
                    f'Найдите скорость лодки в неподвижной воде, если скорость течения равна {k} км/ч. Ответ дайте в км/ч.')
            sol = (f'Пусть скорость лодки в неподвижной воде $v$ км/ч: $$\\frac{{{S}}}{{v-{k}}}-\\frac{{{S}}}{{v+{k}}}={dt}.$$ '
                   f'Отсюда ${2 * S * k}={dt}(v^2-{k * k})$, $$v^2={tex_num(k * k + 2 * S * k / dt)},\\qquad v={tex_num(x)}.$$')
        return cond, sol

    def sample(self, rng):
        v, u = rng.randint(8, 25), rng.randint(1, 5)
        if v <= u + 3:
            return None
        # S = dt(v²−u²)/(2u)
        dt = rng.choice([1, 2, 3, 4, 5, 6])
        S = Fraction(dt * (v * v - u * u), 2 * u)
        if S.denominator != 1 or S > 400:
            return None
        if rng.random() < 0.5:
            return {'S': S, 'dt': Fraction(dt), 'ask': 'u', 'known': Fraction(v)}
        return {'S': S, 'dt': Fraction(dt), 'ask': 'v', 'known': Fraction(u)}


class Race(Word):
    """Два участника, путь S, первый быстрее на Δv и раньше на Δt: скорость первого/второго"""
    topic, code = 'Движение по суше', '10.race'
    patterns = [r'Два велосипедиста одновременно отправились в (\d+)-километровый пробег\. Первый ехал со скоростью,? на (\d+) км/ч большей, чем скорость второго, '
                r'и прибыл к финишу на (\d+) час\w* раньше второго\. Найдите скорость велосипедиста, (?:пришедшего|прибывшего) к финишу (первым|вторым)',
                r'(?P<ships>От пристани A к пристани B, расстояние между которыми равно (\d+) км, отправился с постоянной скоростью первый теплоход, а через (\d+) час\w* '
                r'после этого следом за ним со скоростью,? на (\d+) км/ч больш\w+(?: скорости первого)?,? отправился второй\. Найдите скорость (первого|второго) теплохода)']

    def parse(self, m, task):
        if m.groupdict().get('ships'):
            return {'kind': 'ships', 'S': _n(m.group(2)), 'dt': _n(m.group(3)), 'dv': _n(m.group(4)), 'ask': 1 if m.group(5) == 'первого' else 2}
        return {'kind': 'bikes', 'S': _n(m.group(1)), 'dv': _n(m.group(2)), 'dt': _n(m.group(3)), 'ask': 1 if m.group(4) == 'первым' else 2}

    def _slow(self, p):
        # S/x − S/(x+dv) = dt → dt x² + dt dv x − S dv = 0, x — скорость медленного
        return _positive(p['dt'], p['dt'] * p['dv'], -p['S'] * p['dv'])

    def solve(self, p):
        x = self._slow(p)
        if p['kind'] == 'bikes':
            return x + p['dv'] if p['ask'] == 1 else x
        return x if p['ask'] == 1 else x + p['dv']

    def build(self, p):
        S, dv, dt = p['S'], p['dv'], p['dt']
        x = self._slow(p)
        if p['kind'] == 'bikes':
            who = 'первым' if p['ask'] == 1 else 'вторым'
            cond = (f'Два велосипедиста одновременно отправились в {S}-километровый пробег. Первый ехал со скоростью, на {dv} км/ч большей, '
                    f'чем скорость второго, и прибыл к финишу на {_hours(dt)} раньше второго. Найдите скорость велосипедиста, пришедшего к финишу {who}. '
                    f'Ответ дайте в км/ч.')
            intro = f'Пусть скорость второго велосипедиста $x$ км/ч, тогда первого — $x+{dv}$. Второй был в пути на {_hours(dt)} дольше:'
        else:
            who = 'первого' if p['ask'] == 1 else 'второго'
            cond = (f'От пристани A к пристани B, расстояние между которыми равно {S} км, отправился с постоянной скоростью первый теплоход, а через '
                    f'{_hours(dt)} после этого следом за ним со скоростью на {dv} км/ч большей отправился второй. Найдите скорость {who} теплохода, '
                    f'если в пункт B оба теплохода прибыли одновременно. Ответ дайте в км/ч.')
            intro = f'Пусть скорость первого теплохода $x$ км/ч, второго — $x+{dv}$. Первый был в пути на {_hours(dt)} дольше:'
        sol = (f'{intro} $$\\frac{{{S}}}{{x}}-\\frac{{{S}}}{{x+{dv}}}={dt}.$$ Отсюда ${S * dv}={dt}x(x+{dv})$, $${_quad_text(dt, dt * dv, -S * dv)}.$$ '
               f'Положительный корень $x={tex_num(x)}$, искомая скорость — ${tex_num(self.solve(p))}$ км/ч.')
        return cond, sol

    def sample(self, rng):
        x = rng.randint(8, 30)
        dv = rng.choice([1, 2, 3, 4, 5, 6, 8, 10])
        dt = rng.choice([1, 2, 3, 4])
        S = Fraction(dt * x * (x + dv), dv)
        if S.denominator != 1 or S > 400:
            return None
        return {'kind': rng.choice(['bikes', 'ships']), 'S': S, 'dv': Fraction(dv), 'dt': Fraction(dt), 'ask': rng.choice([1, 2])}


class ReturnWithStop(Word):
    """Туда со скоростью x, обратно быстрее на Δv с остановкой s, время одинаковое"""
    topic, code = 'Движение по суше', '10.stop'
    patterns = [r'(?P<bike>Велосипедист выехал с постоянной скоростью из города А в город В, расстояние между которыми равно (\d+) км\. На следующий день он отправился обратно '
                r'со скоростью на (\d+) км/ч больше прежней\. По дороге он сделал остановку на (\d+) час\w*\..*?Найдите скорость велосипедиста на пути из ([АAВB]) в ([АAВB]))',
                r'(?P<barge>Пристани A и B расположены на озере, расстояние между ними равно (\d+) км\. Баржа отправилась.*?со скоростью на (\d+) км/ч больше прежней, '
                r'сделав по пути остановку на (\d+) час\w*\..*?Найдите скорость баржи на пути из ([АAВB]) в ([АAВB]))']

    def parse(self, m, task):
        g = [x for x in m.groups() if x is not None]
        return {'kind': 'bike' if m.groupdict().get('bike') else 'barge', 'S': _n(g[1]), 'dv': _n(g[2]), 's': _n(g[3]),
                'ask': 'there' if g[4] in 'АA' else 'back'}

    def _x(self, p):
        # S/x = S/(x+dv) + s → s x² + s dv x − S dv = 0
        return _positive(p['s'], p['s'] * p['dv'], -p['S'] * p['dv'])

    def solve(self, p):
        x = self._x(p)
        return x if p['ask'] == 'there' else x + p['dv']

    def build(self, p):
        S, dv, s = p['S'], p['dv'], p['s']
        x = self._x(p)
        route = 'из A в B' if p['ask'] == 'there' else 'из B в A'
        if p['kind'] == 'bike':
            cond = (f'Велосипедист выехал с постоянной скоростью из города A в город B, расстояние между которыми равно {S} км. На следующий день он '
                    f'отправился обратно со скоростью на {dv} км/ч больше прежней. По дороге он сделал остановку на {_hours(s)}. В результате он затратил '
                    f'на обратный путь столько же времени, сколько на путь из A в B. Найдите скорость велосипедиста на пути {route}. Ответ дайте в км/ч.')
        else:
            cond = (f'Пристани A и B расположены на озере, расстояние между ними равно {S} км. Баржа отправилась с постоянной скоростью из A в B. '
                    f'На следующий день после прибытия она отправилась тем же путём обратно со скоростью на {dv} км/ч больше прежней, сделав по пути '
                    f'остановку на {_hours(s)}. В результате она затратила на обратный путь столько же времени, сколько на путь из A в B. Найдите '
                    f'скорость баржи на пути {route}. Ответ дайте в км/ч.')
        sol = (f'Пусть скорость на пути из A в B равна $x$ км/ч, обратно — $x+{dv}$. Время в пути одинаковое, но обратно {_hours(s)} ушло на остановку: '
               f'$$\\frac{{{S}}}{{x}}=\\frac{{{S}}}{{x+{dv}}}+{s}.$$ Отсюда $${_quad_text(s, s * dv, -S * dv)},$$ положительный корень $x={tex_num(x)}$. '
               f'Скорость на пути {route} — ${tex_num(self.solve(p))}$ км/ч.')
        return cond, sol

    def sample(self, rng):
        x = rng.randint(6, 30)
        dv = rng.choice([1, 2, 3, 4, 5, 6])
        s = rng.choice([1, 2, 3, 4])
        S = Fraction(s * x * (x + dv), dv)
        if S.denominator != 1 or S > 400:
            return None
        return {'kind': rng.choice(['bike', 'barge']), 'S': S, 'dv': Fraction(dv), 's': Fraction(s), 'ask': rng.choice(['there', 'back'])}


class ShipStop(Word):
    """По течению S и обратно со стоянкой: всего T часов"""
    topic, code = 'Движение по воде', '10.ship'
    patterns = [r'Теплоход проходит по течению реки до пункта назначения (\d+) км и после стоянки возвращается в пункт отправления\. Найдите скорость '
                r'(теплохода в неподвижной воде|течения), если скорость (?:течения|теплохода в неподвижной воде) равна (\d+) км/ч, стоянка длится (\d+) час\w*, '
                r'а в пункт отправления теплоход возвращается через (\d+) час',
                r'(?P<boat>Катер в \$(\d+):00\$ вышел по течению реки из пункта А в пункт В, расположенный в (\d+) км от А\. Пробыв (?:в пункте В )?(\d+) час\w*(?: в пункте В)?, катер '
                r'отправился назад и вернулся в пункт А в \$(\d+):00\$ того же дня\. Определите собственную скорость катера \(в км/ч\), если известно, что скорость течения реки (\d+) км/ч)',
                r'(?P<dist>Теплоход, скорость которого в неподвижной воде равна (\d+) км/ч, проходит некоторое расстояние по реке и после стоянки возвращается в исходный пункт\. '
                r'Скорость течения равна (\d+) км/ч, стоянка длится (\d+) час\w*, а в исходный пункт теплоход возвращается через (\d+) час)']

    def parse(self, m, task):
        g = m.groupdict()
        if g.get('boat'):
            t1, S, s, t2, u = (_n(x) for x in re.findall(r'\d+', g['boat'].replace(':00', ''))[:5])
            return {'ask': 'v', 'S': S, 'known': u, 's': s, 'T': t2 - t1}
        if g.get('dist'):
            v, u, s, T = (_n(x) for x in re.findall(r'(\d+) (?:км/ч|час)', g['dist'])[:4])
            return {'ask': 'S', 'v': v, 'u': u, 's': s, 'T': T}
        return {'ask': 'v' if 'теплохода' in m.group(2) else 'u', 'S': _n(m.group(1)), 'known': _n(m.group(3)), 's': _n(m.group(4)), 'T': _n(m.group(5))}

    def solve(self, p):
        if p['ask'] == 'S':
            t = p['T'] - p['s']
            v, u = p['v'], p['u']
            # S/(v+u) + S/(v−u) = t → S = t(v²−u²)/(2v); за весь рейс 2S
            return 2 * t * (v * v - u * u) / (2 * v)
        S, k, t = p['S'], p['known'], p['T'] - p['s']
        if p['ask'] == 'v':
            # 2Sv = t(v² − u²) → t v² − 2S v − t u² = 0
            return _positive(t, -2 * S, -t * k * k)
        # 2Sv = t(v² − u²) → t u² + 2Sv − t v² = 0 → u² = v² − 2Sv/t
        u2 = k * k - 2 * S * k / t
        r = Fraction(isqrt_exact(u2.numerator) or -1, isqrt_exact(u2.denominator) or 1)
        if u2 <= 0 or r * r != u2:
            raise ValueError('иррационально')
        return r

    def build(self, p):
        if p['ask'] == 'S':
            v, u, s, T = p['v'], p['u'], p['s'], p['T']
            t = T - s
            cond = (f'Теплоход, скорость которого в неподвижной воде равна {v} км/ч, проходит некоторое расстояние по реке и после стоянки возвращается '
                    f'в исходный пункт. Скорость течения равна {u} км/ч, стоянка длится {_hours(s)}, а в исходный пункт теплоход возвращается через '
                    f'{_hours(T)} после отправления из него. Сколько километров проходит теплоход за весь рейс?')
            sol = (f'В движении теплоход был ${T}-{s}={t}$ ч. Пусть расстояние в одну сторону $S$ км: $$\\frac{{S}}{{{v + u}}}+\\frac{{S}}{{{v - u}}}={t}.$$ '
                   f'Отсюда $S={tex_num(self.solve(p) / 2)}$, а за весь рейс $2S={tex_num(self.solve(p))}$ км.')
            return cond, sol
        S, k, s, T = p['S'], p['known'], p['s'], p['T']
        t = T - s
        x = self.solve(p)
        if p['ask'] == 'v':
            cond = (f'Теплоход проходит по течению реки до пункта назначения {S} км и после стоянки возвращается в пункт отправления. Найдите скорость '
                    f'теплохода в неподвижной воде, если скорость течения равна {k} км/ч, стоянка длится {_hours(s)}, а в пункт отправления теплоход '
                    f'возвращается через {_hours(T)} после отплытия из него. Ответ дайте в км/ч.')
            sol = (f'В движении теплоход был ${T}-{s}={t}$ ч. Пусть его собственная скорость $v$ км/ч: $$\\frac{{{S}}}{{v+{k}}}+\\frac{{{S}}}{{v-{k}}}={t}.$$ '
                   f'Приводим к общему знаменателю: ${2 * S}v={t}(v^2-{k * k})$, $${_quad_text(t, -2 * S, -t * k * k, "v")}.$$ Положительный корень $v={tex_num(x)}$.')
        else:
            cond = (f'Теплоход проходит по течению реки до пункта назначения {S} км и после стоянки возвращается в пункт отправления. Найдите скорость '
                    f'течения, если скорость теплохода в неподвижной воде равна {k} км/ч, стоянка длится {_hours(s)}, а в пункт отправления теплоход '
                    f'возвращается через {_hours(T)} после отплытия из него. Ответ дайте в км/ч.')
            sol = (f'В движении теплоход был ${t}$ ч. Пусть скорость течения $u$: $$\\frac{{{S}}}{{{k}+u}}+\\frac{{{S}}}{{{k}-u}}={t},\\qquad '
                   f'{2 * S * k}={t}({k * k}-u^2),\\qquad u^2={tex_num(x * x)},\\qquad u={tex_num(x)}.$$')
        return cond, sol

    def sample(self, rng):
        v, u = rng.randint(10, 30), rng.randint(1, 5)
        if v < 3 * u:
            return None
        ask = rng.choice(['v', 'u', 'S'])
        t = rng.randint(4, 40)
        S = Fraction(t * (v * v - u * u), 2 * v)
        s = rng.randint(1, 8)
        if ask == 'S':
            return {'ask': 'S', 'v': Fraction(v), 'u': Fraction(u), 's': Fraction(s), 'T': Fraction(t + s)}
        if S.denominator != 1 or S > 500:
            return None
        return {'ask': ask, 'S': S, 'known': Fraction(u if ask == 'v' else v), 's': Fraction(s), 'T': Fraction(t + s)}


class AverageSpeed(Word):
    """Средняя скорость по участкам: заданы времена или расстояния"""
    topic, code = 'Движение по суше', '10.average'
    patterns = [r'(Первый час|Первые (\d+) км) автомобиль ехал со скоростью (\d+) км/ч, следующие (\S+) (?:часа|км) — со скоростью (\d+) км/ч, а затем (\S+) (?:часа|км) — со скоростью (\d+) км/ч']

    WORDS = {'один': 1, 'два': 2, 'три': 3, 'четыре': 4, 'пять': 5, 'два часа': 2}

    def _num(self, s):
        return Fraction(self.WORDS[s]) if s in self.WORDS else _n(s)

    def parse(self, m, task):
        if m.group(1) == 'Первый час':
            return {'by': 'time', 'parts': [(Fraction(1), _n(m.group(3))), (self._num(m.group(4)), _n(m.group(5))), (self._num(m.group(6)), _n(m.group(7)))]}
        return {'by': 'dist', 'parts': [(_n(m.group(2)), _n(m.group(3))), (self._num(m.group(4)), _n(m.group(5))), (self._num(m.group(6)), _n(m.group(7)))]}

    def solve(self, p):
        if p['by'] == 'time':
            return sum(t * v for t, v in p['parts']) / sum(t for t, _ in p['parts'])
        return sum(s for s, _ in p['parts']) / sum(s / v for s, v in p['parts'])

    def build(self, p):
        parts = p['parts']
        if p['by'] == 'time':
            words = {1: 'один час', 2: 'два часа', 3: 'три часа', 4: 'четыре часа'}
            cond = (f'Первый час автомобиль ехал со скоростью {parts[0][1]} км/ч, следующие {words[int(parts[1][0])].split()[0]} часа — со скоростью '
                    f'{parts[1][1]} км/ч, а затем {words[int(parts[2][0])]} — со скоростью {parts[2][1]} км/ч. Найдите среднюю скорость автомобиля на '
                    f'протяжении всего пути. Ответ дайте в км/ч.').replace('следующие один часа', 'следующий час').replace('следующие четыре часа', 'следующие четыре часа')
            S = ' + '.join(f'{dec(t)}\\cdot {v}' for t, v in parts)
            total_s = sum(t * v for t, v in parts)
            total_t = sum(t for t, _ in parts)
            sol = (f'Средняя скорость — весь путь, делённый на всё время. Путь: $${S}={tex_num(total_s)}\\text{{ км}},$$ время ${tex_num(total_t)}$ ч. '
                   f'$$v_{{\\text{{ср}}}}=\\frac{{{tex_num(total_s)}}}{{{tex_num(total_t)}}}={tex_num(self.solve(p))}.$$')
        else:
            cond = (f'Первые {parts[0][0]} км автомобиль ехал со скоростью {parts[0][1]} км/ч, следующие {parts[1][0]} км — со скоростью {parts[1][1]} км/ч, '
                    f'а затем {parts[2][0]} км — со скоростью {parts[2][1]} км/ч. Найдите среднюю скорость автомобиля на протяжении всего пути. Ответ дайте в км/ч.')
            times = ' + '.join(f'\\frac{{{s}}}{{{v}}}' for s, v in parts)
            total_t = sum(s / v for s, v in parts)
            total_s = sum(s for s, _ in parts)
            sol = (f'Время на участках: $${times}={tex_num(total_t)}\\text{{ ч}},$$ путь ${tex_num(total_s)}$ км. '
                   f'$$v_{{\\text{{ср}}}}=\\frac{{{tex_num(total_s)}}}{{{tex_num(total_t)}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        if rng.random() < 0.5:
            parts = [(Fraction(1), Fraction(rng.randint(8, 24) * 5)), (Fraction(rng.choice([2, 3])), Fraction(rng.randint(8, 24) * 5)),
                     (Fraction(rng.choice([2, 3, 4])), Fraction(rng.randint(8, 24) * 5))]
            return {'by': 'time', 'parts': parts}
        parts = []
        for _ in range(3):
            v = rng.choice([40, 45, 50, 60, 70, 75, 80, 90, 100, 120])
            t = Fraction(rng.choice([1, 2, 3, 4]), rng.choice([1, 2]))
            s = v * t
            if s.denominator != 1:
                return None
            parts.append((s, Fraction(v)))
        return {'by': 'dist', 'parts': parts}


class Braking(Word):
    """S = v₀t − at²/2 → время"""
    topic, code = 'Движение по суше', '10.braking'
    patterns = [r'со скоростью \$v_0=(\d+)\\text\{м/с\}(?:\\text)?\$, начал торможение с постоянным ускорением \$a=(\d+)\{?\\text\{м/с\}\}?\^2\$.*?автомобиль проехал (\d+) метр']

    def parse(self, m, task):
        return {'v0': _n(m.group(1)), 'a': _n(m.group(2)), 'S': _n(m.group(3))}

    def solve(self, p):
        roots, _, _ = _roots(p['a'] / 2, -p['v0'], p['S'])
        pos = [x for x in roots if x > 0]
        return min(pos)

    def build(self, p):
        v0, a, S = p['v0'], p['a'], p['S']
        roots, D, r = _roots(a / 2, -v0, S)
        cond = (f'Автомобиль, движущийся со скоростью $v_0={v0}$ м/с, начал торможение с постоянным ускорением $a={a}$ м/с². За $t$ секунд после '
                f'начала торможения он прошёл путь $S=v_0t-\\frac{{at^2}}{{2}}$ (м). Определите время, прошедшее с момента начала торможения, если известно, '
                f'что за это время автомобиль проехал {S} метров. Ответ дайте в секундах.')
        sol = (f'$${v0}t-\\frac{{{a}t^2}}{{2}}={S},\\qquad {_quad_text(a / 2, -v0, S, "t")}.$$ Корни ${", ".join(tex_num(x) for x in roots)}$. '
               f'Автомобиль останавливается в момент $t=\\frac{{v_0}}{{a}}={tex_num(v0 / a)}$, после этого формула не действует, поэтому '
               f'подходит меньший корень $t={tex_num(self.solve(p))}$ с.')
        return cond, sol

    def sample(self, rng):
        a = Fraction(rng.choice([2, 3, 4, 5, 6]))
        t = Fraction(rng.randint(2, 8))
        v0 = Fraction(rng.randint(int(a * t) + 2, int(a * t) + 20))
        S = v0 * t - a * t * t / 2
        return {'v0': v0, 'a': a, 'S': S} if S.denominator == 1 else None


class RaftYacht(Word):
    """Плот и яхта: яхта догоняет до B и возвращается, пока плот проплыл r км"""
    topic, code = 'Движение по воде', '10.raft'
    patterns = [r'Расстояние между пристанями A и B равно (\d+) км\. Из A в B по течению реки отправился плот, а через (\d+) час\w* вслед за ним отправилась яхта.*?'
                r'К этому времени плот проплыл (\d+) км\. Найдите скорость яхты в неподвижной воде, если скорость течения реки равна (\d+) км/ч']

    def parse(self, m, task):
        return {'S': _n(m.group(1)), 'd': _n(m.group(2)), 'r': _n(m.group(3)), 'u': _n(m.group(4))}

    def solve(self, p):
        t = p['r'] / p['u'] - p['d']
        # S/(v+u) + S/(v−u) = t → t v² − 2S v − t u² = 0
        return _positive(t, -2 * p['S'], -t * p['u'] ** 2)

    def build(self, p):
        S, d, r, u = p['S'], p['d'], p['r'], p['u']
        t = r / u - d
        cond = (f'Расстояние между пристанями A и B равно {S} км. Из A в B по течению реки отправился плот, а через {_hours(d)} вслед за ним отправилась яхта, '
                f'которая, прибыв в пункт B, тотчас повернула обратно и возвратилась в A. К этому времени плот проплыл {r} км. Найдите скорость яхты '
                f'в неподвижной воде, если скорость течения реки равна {u} км/ч. Ответ дайте в км/ч.')
        sol = (f'Плот плывёт со скоростью течения и был в пути $\\frac{{{r}}}{{{u}}}={tex_num(r / u)}$ ч, яхта — на {_hours(d)} меньше, ${tex_num(t)}$ ч. '
               f'$$\\frac{{{S}}}{{v+{u}}}+\\frac{{{S}}}{{v-{u}}}={tex_num(t)},\\qquad {_quad_text(t, -2 * S, -t * u * u, "v")}.$$ '
               f'Положительный корень $v={tex_num(self.solve(p))}$.')
        return cond, sol

    def sample(self, rng):
        u = rng.randint(2, 5)
        v = rng.randint(3 * u, 30)
        t = rng.randint(4, 15)
        S = Fraction(t * (v * v - u * u), 2 * v)
        d = rng.randint(1, 4)
        r = u * (t + d)
        if S.denominator != 1 or r >= S:
            return None
        return {'S': S, 'd': Fraction(d), 'r': Fraction(r), 'u': Fraction(u)}


class Trains(Word):
    """Поезда навстречу: длина скорого по времени прохождения"""
    topic, code = 'Движение по суше', '10.trains'
    patterns = [r'скорости которых равны соответственно (\d+) км/ч и (\d+) км/ч\. Длина пассажирского поезда равна (\d+) метр\w*\. Найдите длину скорого поезда, если время, за которое он прошёл мимо пассажирского, равно (\d+) секунд']

    def parse(self, m, task):
        return {'v1': _n(m.group(1)), 'v2': _n(m.group(2)), 'L2': _n(m.group(3)), 't': _n(m.group(4))}

    def solve(self, p):
        return (p['v1'] + p['v2']) * 1000 / 3600 * p['t'] - p['L2']

    def build(self, p):
        v1, v2, L2, t = p['v1'], p['v2'], p['L2'], p['t']
        w = (v1 + v2) * 1000 / 3600
        cond = (f'По двум параллельным железнодорожным путям навстречу друг другу следуют скорый и пассажирский поезда, скорости которых равны '
                f'соответственно {v1} км/ч и {v2} км/ч. Длина пассажирского поезда равна {L2} метрам. Найдите длину скорого поезда, если время, '
                f'за которое он прошёл мимо пассажирского, равно {t} секундам. Ответ дайте в метрах.')
        sol = (f'Скорость сближения ${v1}+{v2}={v1 + v2}$ км/ч $=\\frac{{{v1 + v2}\\cdot 1000}}{{3600}}={tex_num(w)}$ м/с. За {t} с поезда вместе '
               f'проходят суммарную длину: $${tex_num(w)}\\cdot {t}={tex_num(w * t)}\\text{{ м}},$$ поэтому длина скорого ${tex_num(w * t)}-{L2}={tex_num(self.solve(p))}$ м.')
        return cond, sol

    def sample(self, rng):
        v1 = rng.randint(60, 120)
        v2 = rng.randint(30, 70)
        if (v1 + v2) % 18:
            return None
        t = rng.choice([18, 24, 30, 36, 45, 54])
        L2 = rng.choice([200, 250, 300, 350, 400, 450])
        p = {'v1': Fraction(v1), 'v2': Fraction(v2), 'L2': Fraction(L2), 't': Fraction(t)}
        return p if 200 < self.solve(p) < 1200 else None


class Meeting(Word):
    """Автомобили навстречу, второй выехал на час позже, встреча на расстоянии d от A"""
    topic, code = 'Движение по суше', '10.meeting'
    patterns = [r'Расстояние между городами A и B равно (\d+) км\. Из города A в город B выехал первый автомобиль, а через (час|\d+ час\w*) после этого навстречу ему из города B '
                r'выехал со скоростью (\d+) км/ч второй автомобиль\. Найдите скорость первого автомобиля, если автомобили встретились на расстоянии (\d+) км от города A']

    def parse(self, m, task):
        return {'D': _n(m.group(1)), 'delay': Fraction(1) if m.group(2) == 'час' else _n(m.group(2).split()[0]), 'v2': _n(m.group(3)), 'd': _n(m.group(4))}

    def solve(self, p):
        t2 = (p['D'] - p['d']) / p['v2']
        return p['d'] / (t2 + p['delay'])

    def build(self, p):
        D, dl, v2, d = p['D'], p['delay'], p['v2'], p['d']
        t2 = (D - d) / v2
        cond = (f'Расстояние между городами A и B равно {D} км. Из города A в город B выехал первый автомобиль, а через {"час" if dl == 1 else _hours(dl)} после '
                f'этого навстречу ему из города B выехал со скоростью {v2} км/ч второй автомобиль. Найдите скорость первого автомобиля, если автомобили '
                f'встретились на расстоянии {d} км от города A. Ответ дайте в км/ч.')
        sol = (f'Второй автомобиль до встречи проехал ${D}-{d}={D - d}$ км за $\\frac{{{D - d}}}{{{v2}}}={tex_num(t2)}$ ч. Первый был в пути на {_hours(dl)} '
               f'дольше — ${tex_num(t2 + dl)}$ ч — и проехал {d} км: $$v_1=\\frac{{{d}}}{{{tex_num(t2 + dl)}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        v1, v2 = rng.randint(4, 12) * 10, rng.randint(4, 12) * 10
        t2 = rng.randint(1, 4)
        dl = 1
        d = v1 * (t2 + dl)
        D = d + v2 * t2
        return {'D': Fraction(D), 'delay': Fraction(dl), 'v2': Fraction(v2), 'd': Fraction(d)}


# ---------------------------------------------------------------------------
# Работа
# ---------------------------------------------------------------------------

class Workers(Word):
    """Заказ из N деталей: первый быстрее на Δt часов и делает на Δk деталей в час больше"""
    topic, code = 'Совместная работа', '10.workers'
    patterns = [r'Заказ на изготовление (\d+) детал\w+ первый рабочий выполняет на (\d+) час\w* быстрее, чем второй\. Сколько деталей за час изготавливает (первый|второй) рабочий, '
                r'если известно, что (?:он|первый) за час изготавливает на (\d+) детал\w+ больше']

    def parse(self, m, task):
        return {'N': _n(m.group(1)), 'dt': _n(m.group(2)), 'ask': 1 if m.group(3) == 'первый' else 2, 'dk': _n(m.group(4))}

    def _x(self, p):
        # N/x − N/(x+dk) = dt → dt x² + dt dk x − N dk = 0
        return _positive(p['dt'], p['dt'] * p['dk'], -p['N'] * p['dk'])

    def solve(self, p):
        x = self._x(p)
        return x + p['dk'] if p['ask'] == 1 else x

    def build(self, p):
        N, dt, dk = p['N'], p['dt'], p['dk']
        x = self._x(p)
        who = 'первый' if p['ask'] == 1 else 'второй'
        tail = 'он за час изготавливает на {dk} {w} больше второго' if p['ask'] == 1 else 'первый за час изготавливает на {dk} {w} больше'
        tail = tail.format(dk=dk, w=plural(int(dk), 'деталь', 'детали', 'деталей'))
        cond = (f'Заказ на изготовление {N} {plural(int(N), "детали", "деталей", "деталей")} первый рабочий выполняет на {_hours(dt)} быстрее, чем второй. '
                f'Сколько деталей за час изготавливает {who} рабочий, если известно, что {tail}?')
        sol = (f'Пусть второй рабочий делает $x$ деталей в час, тогда первый — $x+{dk}$. Второй работает на {_hours(dt)} дольше: '
               f'$$\\frac{{{N}}}{{x}}-\\frac{{{N}}}{{x+{dk}}}={dt},\\qquad {_quad_text(dt, dt * dk, -N * dk)}.$$ Положительный корень $x={tex_num(x)}$, '
               f'поэтому {who} рабочий делает ${tex_num(self.solve(p))}$ {plural(int(self.solve(p)), "деталь", "детали", "деталей")} в час.')
        return cond, sol

    def sample(self, rng):
        x = rng.randint(4, 30)
        dk = rng.randint(1, 8)
        dt = rng.randint(1, 8)
        N = Fraction(dt * x * (x + dk), dk)
        if N.denominator != 1 or N > 500:
            return None
        return {'N': N, 'dt': Fraction(dt), 'ask': rng.choice([1, 2]), 'dk': Fraction(dk)}


class Pipes(Word):
    """Трубы: первая пропускает на d л/мин меньше, резервуар V она заполняет на Δt дольше"""
    topic, code = 'Совместная работа', '10.pipes'
    patterns = [r'Первая труба пропускает на (\d+) литр\w* воды в минуту меньше, чем вторая\. Сколько литров воды в минуту пропускает (первая|вторая) труба, если резервуар объёмом '
                r'(\d+) литр\w* она заполняет на (\d+) минут\w* (быстрее|дольше)']

    def parse(self, m, task):
        return {'d': _n(m.group(1)), 'ask': 1 if m.group(2) == 'первая' else 2, 'V': _n(m.group(3)), 'dt': _n(m.group(4))}

    def _x(self, p):
        # x — первая: V/x − V/(x+d) = dt
        return _positive(p['dt'], p['dt'] * p['d'], -p['V'] * p['d'])

    def solve(self, p):
        x = self._x(p)
        return x if p['ask'] == 1 else x + p['d']

    def build(self, p):
        d, V, dt = p['d'], p['V'], p['dt']
        x = self._x(p)
        if p['ask'] == 1:
            tail = f'она заполняет на {dt} {plural(int(dt), "минуту", "минуты", "минут")} дольше, чем вторая труба'
            who = 'первая'
        else:
            tail = f'она заполняет на {dt} {plural(int(dt), "минуту", "минуты", "минут")} быстрее, чем первая труба'
            who = 'вторая'
        cond = (f'Первая труба пропускает на {d} {plural(int(d), "литр", "литра", "литров")} воды в минуту меньше, чем вторая. Сколько литров воды в минуту '
                f'пропускает {who} труба, если резервуар объёмом {V} {plural(int(V), "литр", "литра", "литров")} {tail}?')
        sol = (f'Пусть первая труба пропускает $x$ л/мин, вторая — $x+{d}$. Первая заполняет резервуар на {dt} мин дольше: '
               f'$$\\frac{{{V}}}{{x}}-\\frac{{{V}}}{{x+{d}}}={dt},\\qquad {_quad_text(dt, dt * d, -V * d)}.$$ Положительный корень $x={tex_num(x)}$, '
               f'{who} труба пропускает ${tex_num(self.solve(p))}$ л/мин.')
        return cond, sol

    def sample(self, rng):
        x = rng.randint(3, 30)
        d = rng.randint(1, 8)
        dt = rng.randint(1, 10)
        V = Fraction(dt * x * (x + d), d)
        if V.denominator != 1 or V > 800:
            return None
        return {'d': Fraction(d), 'ask': rng.choice([1, 2]), 'V': V, 'dt': Fraction(dt)}


class Together(Word):
    """Совместная работа: оба мастера / три насоса вместе; один из двоих по общему времени"""
    topic, code = 'Совместная работа', '10.together'
    patterns = [r'Один мастер может выполнить заказ за (\d+) час\w*, а другой — за (\d+) час\w*\. За сколько часов выполнят этот заказ оба мастера',
                r'(?P<pumps>Первый насос наполняет бак за (\d+) минут\w*, второй — за (\d+) минут\w*, а третий — за (\d+) час\w* (\d+) минут)',
                r'(?P<pair>([А-ЯЁ][а-яё]+) и ([А-ЯЁ][а-яё]+), работая вместе, пропалывают грядку за (\d+) минут\w*, а одна ([А-ЯЁ][а-яё]+) — за (\d+) минут)']

    def parse(self, m, task):
        g = m.groupdict()
        if g.get('pumps'):
            a, b, h, mi = (int(x) for x in re.findall(r'\d+', g['pumps']))
            return {'kind': 'three', 'times': [Fraction(a), Fraction(b), Fraction(60 * h + mi)]}
        if g.get('pair'):
            names = re.match(r'([А-ЯЁ][а-яё]+) и ([А-ЯЁ][а-яё]+), работая вместе, пропалывают грядку за (\d+) минут\w*, а одна ([А-ЯЁ][а-яё]+) — за (\d+)', g['pair'])
            other = names.group(1) if names.group(4) == names.group(2) else names.group(2)
            return {'kind': 'pair', 'T': _n(names.group(3)), 'alone': _n(names.group(5)), 'who': names.group(4), 'other': other}
        return {'kind': 'two', 'times': [_n(m.group(1)), _n(m.group(2))]}

    def solve(self, p):
        if p['kind'] == 'pair':
            return 1 / (1 / p['T'] - 1 / p['alone'])
        return 1 / sum(1 / t for t in p['times'])

    def build(self, p):
        x = self.solve(p)
        if p['kind'] == 'two':
            a, b = p['times']
            cond = (f'Один мастер может выполнить заказ за {_hours(a)}, а другой — за {_hours(b)}. За сколько часов выполнят этот заказ оба мастера, работая вместе?')
            sol = (f'За час первый выполняет $\\frac{{1}}{{{a}}}$ заказа, второй — $\\frac{{1}}{{{b}}}$, вместе $$\\frac{{1}}{{{a}}}+\\frac{{1}}{{{b}}}=\\frac{{1}}{{{tex_num(x)}}}.$$ '
                   f'Значит, вместе они выполнят заказ за ${tex_num(x)}$ ч.')
        elif p['kind'] == 'three':
            a, b, c = p['times']
            hc, mc = divmod(int(c), 60)
            cond = (f'Первый насос наполняет бак за {a} минут, второй — за {b} минут, а третий — за {hc} час {mc} минут. За сколько минут наполнят этот бак '
                    f'три насоса, работая одновременно?')
            sol = (f'Третий насос наполняет бак за ${int(c)}$ минут. Производительности (часть бака в минуту) складываются: '
                   f'$$\\frac{{1}}{{{a}}}+\\frac{{1}}{{{b}}}+\\frac{{1}}{{{int(c)}}}=\\frac{{1}}{{{tex_num(x)}}}.$$ Вместе — за ${tex_num(x)}$ мин.')
        else:
            T, al, who, other = p['T'], p['alone'], p['who'], p['other']
            cond = (f'{other} и {who}, работая вместе, пропалывают грядку за {T} минут, а одна {who} — за {al} минут. За сколько минут пропалывает эту грядку одна {other}?')
            sol = (f'За минуту вдвоём они пропалывают $\\frac{{1}}{{{T}}}$ грядки, {who} одна — $\\frac{{1}}{{{al}}}$. На долю {other.rstrip("я").rstrip("а")}ы '
                   f'приходится $$\\frac{{1}}{{{T}}}-\\frac{{1}}{{{al}}}=\\frac{{1}}{{{tex_num(x)}}},$$ то есть одна она пропалывает грядку за ${tex_num(x)}$ мин.')
            sol = sol.replace(f'На долю {other.rstrip("я").rstrip("а")}ы приходится', f'Производительность: {other} —')
        return cond, sol

    PAIRS = [('Катя', 'Настя'), ('Аня', 'Таня'), ('Юля', 'Уля'), ('Оля', 'Вера'), ('Маша', 'Даша')]

    def sample(self, rng):
        kind = rng.choice(['two', 'three', 'pair'])
        if kind == 'two':
            a, b = rng.sample(range(6, 60), 2)
            return {'kind': kind, 'times': [Fraction(a), Fraction(b)]}
        if kind == 'three':
            a, b = rng.randint(5, 30), rng.randint(5, 30)
            c = rng.randint(61, 180)
            return {'kind': kind, 'times': [Fraction(a), Fraction(b), Fraction(c)]}
        other, who = rng.choice(self.PAIRS)
        T = rng.randint(10, 40)
        al = rng.randint(T + 5, 4 * T)
        return {'kind': kind, 'T': Fraction(T), 'alone': Fraction(al), 'who': who, 'other': other}

    def nice(self, x):
        return frac(x).denominator == 1 and x > 0


# ---------------------------------------------------------------------------
# Проценты, смеси и сплавы
# ---------------------------------------------------------------------------

class Alloys(Word):
    """Два сплава p₁ и p₂, масса одного больше на d, получили p₃: масса третьего"""
    topic, code = 'Смеси и сплавы', '10.alloys'
    patterns = [r'Имеется два сплава\. Первый сплав содержит (\d+) ?% (\w+), второй — (\d+) ?% \w+\. Масса (первого|второго) сплава (больше|меньше) массы (?:первого|второго) на (\d+) кг\. '
                r'Из этих двух сплавов получили третий сплав, содержащий (\d+) ?% \w+']

    def parse(self, m, task):
        p1, metal, p2 = _n(m.group(1)), m.group(2), _n(m.group(3))
        d = _n(m.group(6))
        bigger_first = (m.group(4) == 'первого') == (m.group(5) == 'больше')
        return {'p1': p1, 'p2': p2, 'p3': _n(m.group(7)), 'd': d if bigger_first else -d, 'metal': metal}

    def _masses(self, p):
        # m1 = m2 + d; p1 m1 + p2 m2 = p3 (m1 + m2) → m2 (p1 + p2 − 2p3) = d (p3 − p1)
        m2 = p['d'] * (p['p3'] - p['p1']) / (p['p1'] + p['p2'] - 2 * p['p3'])
        return m2 + p['d'], m2

    def solve(self, p):
        m1, m2 = self._masses(p)
        if m1 <= 0 or m2 <= 0:
            raise ValueError('отрицательная масса')
        return m1 + m2

    def build(self, p):
        p1, p2, p3, d, metal = p['p1'], p['p2'], p['p3'], p['d'], p['metal']
        m1, m2 = self._masses(p)
        rel = f'Масса первого сплава больше массы второго на {abs(d)} кг' if d > 0 else f'Масса первого сплава меньше массы второго на {abs(d)} кг'
        cond = (f'Имеется два сплава. Первый сплав содержит {p1}% {metal}, второй — {p2}% {metal}. {rel}. Из этих двух сплавов получили третий сплав, '
                f'содержащий {p3}% {metal}. Найдите массу третьего сплава. Ответ дайте в килограммах.')
        sign = '+' if d > 0 else '-'
        sol = (f'Пусть масса второго сплава $x$ кг, тогда первого $x{sign}{abs(d)}$. Масса {metal} в третьем сплаве складывается из её масс в двух первых: '
               f'$${tex_num(p1 / 100)}(x{sign}{abs(d)})+{tex_num(p2 / 100)}x={tex_num(p3 / 100)}(2x{sign}{abs(d)}).$$ Отсюда $x={tex_num(m2)}$, '
               f'масса третьего сплава $2x{sign}{abs(d)}={tex_num(self.solve(p))}$ кг.')
        return cond, sol

    def sample(self, rng):
        p1, p2 = rng.sample([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70], 2)
        m2 = rng.randint(2, 30) * 5
        d = rng.choice([5, 10, 15, 20, 30, 40, 50]) * rng.choice([1, -1])
        m1 = m2 + d
        if m1 <= 0:
            return None
        p3 = Fraction(p1 * m1 + p2 * m2, m1 + m2)
        if p3.denominator != 1:
            return None
        return {'p1': Fraction(p1), 'p2': Fraction(p2), 'p3': p3, 'd': Fraction(d), 'metal': rng.choice(['меди', 'никеля', 'цинка', 'олова'])}

    def nice(self, x):
        return frac(x).denominator == 1 and x > 0


class Vessels(Word):
    """Два сосуда: смесь всего — p%, равных масс — q%: концентрация в первом"""
    topic, code = 'Смеси и сплавы', '10.vessels'
    patterns = [r'Имеется два сосуда\. Первый содержит (\d+) кг, а второй — (\d+) кг растворов кислоты различной концентрации\. Если эти растворы смешать, то получится раствор, '
                r'содержащий (\d+) ?% кислоты\. Если же смешать равные массы этих растворов, то получится раствор, содержащий (\d+) ?% кислоты\. Сколько процентов кислоты содержится в (первом|втором)']

    def parse(self, m, task):
        return {'m1': _n(m.group(1)), 'm2': _n(m.group(2)), 'p': _n(m.group(3)), 'q': _n(m.group(4)), 'ask': 1 if m.group(5) == 'первом' else 2}

    def _c(self, p):
        # m1 c1 + m2 c2 = (m1+m2) p,  c1 + c2 = 2q → c1 (m1 − m2) = (m1+m2)p − 2q m2
        c1 = ((p['m1'] + p['m2']) * p['p'] - 2 * p['q'] * p['m2']) / (p['m1'] - p['m2'])
        return c1, 2 * p['q'] - c1

    def solve(self, p):
        c1, c2 = self._c(p)
        if not (0 < c1 < 100 and 0 < c2 < 100):
            raise ValueError('концентрация вне 0–100')
        return c1 if p['ask'] == 1 else c2

    def build(self, p):
        m1, m2, pp, q = p['m1'], p['m2'], p['p'], p['q']
        c1, c2 = self._c(p)
        which = 'первом' if p['ask'] == 1 else 'втором'
        cond = (f'Имеется два сосуда. Первый содержит {m1} кг, а второй — {m2} кг растворов кислоты различной концентрации. Если эти растворы смешать, '
                f'то получится раствор, содержащий {pp}% кислоты. Если же смешать равные массы этих растворов, то получится раствор, содержащий {q}% кислоты. '
                f'Сколько процентов кислоты содержится в {which} сосуде?')
        sol = (f'Пусть концентрации $x\\%$ и $y\\%$. Из первого условия ${m1}x+{m2}y={m1 + m2}\\cdot {pp}$, из второго (равные массы) $x+y=2\\cdot {q}={2 * q}$. '
               f'Подставим $y={2 * q}-x$: $${m1}x+{m2}({2 * q}-x)={(m1 + m2) * pp},\\qquad {m1 - m2}x={tex_num((m1 + m2) * pp - 2 * q * m2)},$$ '
               f'откуда $x={tex_num(c1)}$, $y={tex_num(c2)}$.')
        return cond, sol

    def sample(self, rng):
        m1, m2 = rng.sample(range(5, 60, 5), 2)
        c1, c2 = rng.sample(range(5, 95), 2)
        p = Fraction(m1 * c1 + m2 * c2, m1 + m2)
        q = Fraction(c1 + c2, 2)
        if p.denominator != 1 or q.denominator != 1:
            return None
        return {'m1': Fraction(m1), 'm2': Fraction(m2), 'p': p, 'q': q, 'ask': rng.choice([1, 2])}

    def nice(self, x):
        return frac(x).denominator == 1 and x > 0


class Percent(Word):
    """k человек составили p% от всех — сколько всего"""
    topic, code = 'Проценты', '10.percent'
    patterns = [r'Призёрами городской олимпиады по (\w+) стали (\d+) ученик\w*, что составило (\d+(?:,\d+)?) ?% от числа участников']

    def parse(self, m, task):
        return {'subj': m.group(1), 'k': _n(m.group(2)), 'p': _n(m.group(3))}

    def solve(self, p):
        return p['k'] * 100 / p['p']

    def build(self, p):
        cond = (f'Призёрами городской олимпиады по {p["subj"]} стали {p["k"]} {plural(int(p["k"]), "ученик", "ученика", "учеников")}, что составило '
                f'{dec(p["p"])}% от числа участников. Сколько человек участвовало в олимпиаде?')
        sol = (f'${p["k"]}$ человек — это ${tex_num(p["p"])}\\%$, значит всего $$\\frac{{{p["k"]}\\cdot 100}}{{{tex_num(p["p"])}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        n = rng.choice([40, 50, 60, 80, 100, 120, 150, 200, 240, 250, 300, 400])
        pct = Fraction(rng.choice([2, 4, 5, 6, 8, 10, 12, 15, 20, 25]))
        k = n * pct / 100
        return {'subj': rng.choice(['математике', 'физике', 'химии', 'информатике']), 'k': k, 'p': pct} if k.denominator == 1 else None

    def nice(self, x):
        return frac(x).denominator == 1


# ---------------------------------------------------------------------------
# Прототипы из банков подготовки, которых нет в открытом банке ФИПИ
# ---------------------------------------------------------------------------

class PriceChange(Word):
    """Цену подняли на p%, потом снизили на q%: итоговая цена / на сколько процентов изменилась"""
    topic, code = 'Проценты', '10.price'

    def solve(self, p):
        return p['price'] * (100 + p['up']) / 100 * (100 - p['down']) / 100

    def build(self, p):
        cond = (f'Товар стоил {p["price"]} рублей. Сначала его цену повысили на {p["up"]}%, а затем новую цену снизили на {p["down"]}%. '
                f'Сколько рублей стал стоить товар?')
        mid = p['price'] * (100 + p['up']) / 100
        sol = (f'После повышения: ${p["price"]}\\cdot {tex_num(Fraction(100 + p["up"], 100))}={tex_num(mid)}$ р. После снижения: '
               f'${tex_num(mid)}\\cdot {tex_num(Fraction(100 - p["down"], 100))}={tex_num(self.solve(p))}$ р.')
        return cond, sol

    def sample(self, rng):
        return {'price': Fraction(rng.choice([400, 500, 800, 1000, 1200, 1500, 2000, 2500, 3000])),
                'up': Fraction(rng.choice([10, 20, 25, 30, 40, 50])), 'down': Fraction(rng.choice([10, 20, 25, 30, 40, 50]))}


class Deposit(Word):
    """Вклад под r% годовых: через сколько лет / какая сумма"""
    topic, code = 'Проценты', '10.deposit'

    def solve(self, p):
        return p['S'] * (1 + p['r'] / 100) ** p['n']

    def build(self, p):
        cond = (f'Вкладчик положил в банк {p["S"]} рублей под {p["r"]}% годовых. Проценты начисляются раз в год и прибавляются к вкладу. '
                f'Какая сумма будет на счёте через {p["n"]} {plural(p["n"], "год", "года", "лет")}? Ответ дайте в рублях.')
        k = 1 + p['r'] / 100
        sol = (f'Каждый год вклад умножается на ${tex_num(k)}$: $${p["S"]}\\cdot {tex_num(k)}^{{{p["n"]}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        return {'S': Fraction(rng.choice([10000, 20000, 50000, 100000, 200000])), 'r': Fraction(rng.choice([5, 10, 20, 25])), 'n': rng.choice([2, 3])}

    def nice(self, x):
        return nice_number(x, 2, limit=10 ** 7)


class CircleRace(Word):
    """Круговая трасса: второй догоняет первого на круг"""
    topic, code = 'Движение по суше', '10.circle'

    def solve(self, p):
        # круг L км, скорости v и v+d, через t часов второй обогнал на круг: d·t = L → d = L/t
        return p['v'] + p['L'] / p['t']

    def build(self, p):
        t_min = p['t'] * 60
        cond = (f'Из одной точки круговой трассы, длина которой равна {p["L"]} км, одновременно в одном направлении стартовали два автомобиля. '
                f'Скорость первого автомобиля равна {p["v"]} км/ч, и через {dec(t_min)} минут после старта он опережал второй автомобиль на один круг. '
                f'Найдите скорость второго автомобиля... ').replace('Найдите скорость второго автомобиля... ', '')
        # формулировка: первый быстрее; ищем скорость первого, дана скорость второго
        cond = (f'Из одной точки круговой трассы, длина которой равна {p["L"]} км, одновременно в одном направлении стартовали два автомобиля. '
                f'Скорость второго автомобиля равна {p["v"]} км/ч, и через {dec(t_min)} минут после старта первый автомобиль опережал второй на один круг. '
                f'Найдите скорость первого автомобиля. Ответ дайте в км/ч.')
        sol = (f'За {dec(t_min)} мин $={tex_num(p["t"])}$ ч первый проехал на один круг ({p["L"]} км) больше, поэтому разность скоростей '
               f'$\\frac{{{p["L"]}}}{{{tex_num(p["t"])}}}={tex_num(p["L"] / p["t"])}$ км/ч. Скорость первого: ${p["v"]}+{tex_num(p["L"] / p["t"])}={tex_num(self.solve(p))}$ км/ч.')
        return cond, sol

    def sample(self, rng):
        t = Fraction(rng.choice([10, 12, 15, 20, 30, 40]), 60)
        L = Fraction(rng.choice([3, 4, 5, 6, 8, 10, 12, 14, 15]))
        return {'t': t, 'L': L, 'v': Fraction(rng.randint(6, 12) * 10)}

    def nice(self, x):
        return frac(x).denominator == 1


TEMPLATES = [BoatRoundTrip(), Race(), ReturnWithStop(), ShipStop(), AverageSpeed(), Braking(), RaftYacht(), Trains(), Meeting(), Workers(), Pipes(),
             Together(), Alloys(), Vessels(), Percent()]
EXTRA = [(PriceChange(), 8), (Deposit(), 6), (CircleRace(), 8)]
