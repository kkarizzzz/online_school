"""№ 5. Сложная теория вероятностей: независимые события, сумма, условная и полная вероятность"""
import itertools
import math
import random
import re
from fractions import Fraction

from app.bankgen.core import Rendered, Template, dec, nice_number, par, plural, tex_num

P = r'(\d+,\d+|\d+)'


def _p(s: str) -> Fraction:
    return Fraction(s.replace(',', '.'))


def _dp(rng: random.Random, lo: int = 1, hi: int = 9, step: int = 10) -> Fraction:
    return Fraction(rng.randint(lo, hi), step)


class Prob(Template):
    number = 5
    topic = 'Теоремы о вероятностях'

    def nice(self, x):
        return nice_number(x, max_decimals=4) and 0 < x < 1

    def render(self, p):
        cond, sol = self.build(p)
        return Rendered(cond, sol + f'\n\n**Ответ:** {dec(self.solve(p))}.')


class Batteries(Prob):
    """Формула полной вероятности: брак p, система бракует неисправную с вероятностью a, исправную — b"""
    topic, code = 'Формула полной вероятности', '5.total'
    patterns = [r'Вероятность того, что готовая батарейка неисправна, равна ' + P + r'\..*?забракует неисправную батарейку, равна ' + P
                + r'\..*?по ошибке забракует исправную батарейку, равна ' + P + r'\.']

    def parse(self, m, task):
        return {'p': _p(m.group(1)), 'a': _p(m.group(2)), 'b': _p(m.group(3))}

    def solve(self, p):
        return p['p'] * p['a'] + (1 - p['p']) * p['b']

    def build(self, p):
        q, a, b = p['p'], p['a'], p['b']
        cond = (f'Автоматическая линия изготавливает батарейки. Вероятность того, что готовая батарейка неисправна, равна {dec(q)}. '
                f'Перед упаковкой каждая батарейка проходит систему контроля качества. Вероятность того, что система забракует '
                f'неисправную батарейку, равна {dec(a)}. Вероятность того, что система по ошибке забракует исправную батарейку, '
                f'равна {dec(b)}. Найдите вероятность того, что случайно выбранная изготовленная батарейка будет забракована системой контроля.')
        sol = (f'Батарейку бракуют в двух несовместных случаях: она неисправна и забракована (${tex_num(q)}\\cdot {tex_num(a)}$) '
               f'или исправна, но забракована по ошибке (${tex_num(1 - q)}\\cdot {tex_num(b)}$). $$P={tex_num(q)}\\cdot {tex_num(a)}+'
               f'{tex_num(1 - q)}\\cdot {tex_num(b)}={tex_num(q * a)}+{tex_num((1 - q) * b)}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        return {'p': _dp(rng, 1, 3, 10) if rng.random() < 0.5 else Fraction(rng.choice([2, 4, 5, 6, 8]), 100),
                'a': Fraction(rng.choice([90, 95, 97, 98, 99]), 100), 'b': Fraction(rng.choice([1, 2, 3, 5]), 100)}


class Shooter(Prob):
    """Четыре мишени, вероятность попадания p: попасть в первые k и промахнуться по остальным"""
    topic, code = 'Независимые события', '5.shooter'
    patterns = [r'Стрелок стреляет по одному разу (?:в|по) кажд\w+ из (\w+) мишеней\. Вероятность попадания в мишень при каждом отдельном выстреле равна '
                + P + r'\. Найдите вероятность того, что стрелок попадёт в (\w+) (?:перв\w+ )?мишен\w* и не попадёт в (\w+ )?последн\w+']

    WORDS = {'одну': 1, 'первую': 1, 'две': 2, 'три': 3, 'четыре': 4, 'четырёх': 4, 'трёх': 3, 'пяти': 5, 'пять': 5}

    def parse(self, m, task):
        n = self.WORDS[m.group(1)]
        hit = self.WORDS[m.group(3)]
        return {'n': n, 'p': _p(m.group(2)), 'hit': hit}

    def solve(self, p):
        return p['p'] ** p['hit'] * (1 - p['p']) ** (p['n'] - p['hit'])

    def build(self, p):
        n, q, hit = p['n'], p['p'], p['hit']
        miss = n - hit
        nw = {3: 'трёх', 4: 'четырёх', 5: 'пяти'}[n]
        hw = {1: 'первую мишень', 2: 'две первые мишени', 3: 'три первые мишени', 4: 'четыре первые мишени'}[hit]
        mw = {1: 'последнюю', 2: 'две последние', 3: 'три последние', 4: 'четыре последние'}[miss]
        cond = (f'Стрелок стреляет по одному разу в каждую из {nw} мишеней. Вероятность попадания в мишень при каждом отдельном выстреле '
                f'равна {dec(q)}. Найдите вероятность того, что стрелок попадёт в {hw} и не попадёт в {mw}.')
        sol = (f'Выстрелы независимы, вероятность промаха $1-{tex_num(q)}={tex_num(1 - q)}$. Перемножаем вероятности: '
               f'$$P={tex_num(q)}^{{{hit}}}\\cdot {tex_num(1 - q)}^{{{miss}}}={tex_num(q ** hit)}\\cdot {tex_num((1 - q) ** miss)}={tex_num(self.solve(p))}.$$'
               .replace('^{1}', ''))
        return cond, sol

    def sample(self, rng):
        n = rng.choice([3, 4, 4])
        return {'n': n, 'p': _dp(rng, 1, 9), 'hit': rng.randint(1, n - 1)}


class CoffeeMachines(Prob):
    """Два автомата: P(A) = P(B) = p, P(AB) = q → кофе останется в обоих: 1 − (2p − q)"""
    topic, code = 'Сложение вероятностей', '5.coffee'
    patterns = [r'Вероятность того, что к концу дня в первом автомате закончится кофе, равна ' + P + r'\..*?кофе закончится в двух автоматах, равна ' + P]

    def parse(self, m, task):
        return {'p': _p(m.group(1)), 'q': _p(m.group(2))}

    def solve(self, p):
        return 1 - (2 * p['p'] - p['q'])

    def build(self, p):
        a, q = p['p'], p['q']
        cond = (f'В торговом центре два одинаковых автомата продают кофе. Вероятность того, что к концу дня в первом автомате закончится '
                f'кофе, равна {dec(a)}. Вероятность того, что кофе закончится во втором автомате, такая же. Вероятность того, что кофе '
                f'закончится в двух автоматах, равна {dec(q)}. Найдите вероятность того, что к концу дня кофе останется в двух автоматах.')
        sol = (f'Кофе закончится хотя бы в одном автомате с вероятностью $$P(A\\cup B)=P(A)+P(B)-P(AB)={tex_num(a)}+{tex_num(a)}-{tex_num(q)}'
               f'={tex_num(2 * a - q)}.$$ Кофе останется в обоих — противоположное событие: $1-{tex_num(2 * a - q)}={tex_num(self.solve(p))}$.')
        return cond, sol

    def sample(self, rng):
        a = Fraction(rng.randint(10, 40), 100)
        q = Fraction(rng.randint(2, int(a * 100) - 1), 100)
        return {'p': a, 'q': q}


class Markers(Prob):
    """Из коробки берут два предмета: по одному двух цветов"""
    topic, code = 'Комбинаторика в вероятности', '5.markers'
    patterns = [r'В коробке (\d+) (\w+), (\d+) (\w+) и (\d+) (\w+) фломастеров\. Случайным образом выбирают два фломастера\. '
                r'Найдите вероятность того, что окажутся выбраны один (\w+) и один (\w+) фломастеры']

    STEMS = {'синих': 'син', 'красных': 'красн', 'зелёных': 'зелён', 'чёрных': 'чёрн', 'жёлтых': 'жёлт'}

    def parse(self, m, task):
        colors = {m.group(2): int(m.group(1)), m.group(4): int(m.group(3)), m.group(6): int(m.group(5))}
        def find(word):
            for c in colors:
                if c[:4] == word[:4]:
                    return c
            raise ValueError(word)
        return {'colors': colors, 'x': find(m.group(7)), 'y': find(m.group(8))}

    def solve(self, p):
        n = sum(p['colors'].values())
        return Fraction(p['colors'][p['x']] * p['colors'][p['y']], math.comb(n, 2))

    def build(self, p):
        c = p['colors']
        n = sum(c.values())
        names = list(c)
        cond = (f'В коробке {c[names[0]]} {names[0]}, {c[names[1]]} {names[1]} и {c[names[2]]} {names[2]} фломастеров. Случайным образом '
                f'выбирают два фломастера. Найдите вероятность того, что окажутся выбраны один {_one(p["x"])} и один {_one(p["y"])} фломастеры.')
        a, b = c[p['x']], c[p['y']]
        sol = (f'Всего способов выбрать два фломастера из ${n}$: $C_{{{n}}}^2=\\frac{{{n}\\cdot {n - 1}}}{{2}}={math.comb(n, 2)}$. '
               f'Благоприятных — ${a}\\cdot {b}={a * b}$ (любой {_one(p["x"])} в паре с любым {_one(p["y"], "instr")}). '
               f'$$P=\\frac{{{a * b}}}{{{math.comb(n, 2)}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        names = ['синих', 'красных', 'зелёных']
        counts = [rng.randint(2, 15) for _ in names]
        x, y = rng.sample(names, 2)
        return {'colors': dict(zip(names, counts)), 'x': x, 'y': y}

    def nice(self, x):
        return nice_number(x, max_decimals=3) and 0 < x < 1


def _one(plural: str, case: str = 'nom') -> str:
    base = {'синих': ('синий', 'синим'), 'красных': ('красный', 'красным'), 'зелёных': ('зелёный', 'зелёным'),
            'чёрных': ('чёрный', 'чёрным'), 'жёлтых': ('жёлтый', 'жёлтым')}[plural]
    return base[0] if case == 'nom' else base[1]


class Interval(Prob):
    """P(X < b) = p, P(X > a) = q → P(a < X < b) = p + q − 1"""
    topic, code = 'Сложение вероятностей', '5.interval'
    patterns = [r'вероятность того, что (?:её )?масса окажется меньше (\d+) г, равна ' + P + r'\. Вероятность того, что масса (?:буханки )?окажется больше (\d+) г, равна ' + P,
                r'(?P<pass>пассажиров)']

    def parse(self, m, task):
        if m.groupdict().get('pass'):
            mm = re.search(r'окажется меньше (\d+) пассажиров, равна ' + P + r'\. Вероятность того, что окажется меньше (\d+) пассажиров, равна ' + P,
                           task['condition'])
            if not mm:
                return None
            return {'kind': 'bus', 'b': int(mm.group(1)), 'pb': _p(mm.group(2)), 'a': int(mm.group(3)), 'pa': _p(mm.group(4))}
        return {'kind': 'bread', 'b': int(m.group(1)), 'pb': _p(m.group(2)), 'a': int(m.group(3)), 'pa': _p(m.group(4))}

    def solve(self, p):
        if p['kind'] == 'bus':
            return p['pb'] - p['pa']
        return p['pb'] + p['pa'] - 1

    def build(self, p):
        if p['kind'] == 'bus':
            cond = (f'Из районного центра в деревню ежедневно ходит автобус. Вероятность того, что в понедельник в автобусе окажется меньше '
                    f'{p["b"]} пассажиров, равна {dec(p["pb"])}. Вероятность того, что окажется меньше {p["a"]} пассажиров, равна {dec(p["pa"])}. '
                    f'Найдите вероятность того, что число пассажиров будет от {p["a"]} до {p["b"] - 1} включительно.')
            sol = (f'Событие «меньше {p["b"]}» — объединение несовместных событий «меньше {p["a"]}» и «от {p["a"]} до {p["b"] - 1}». '
                   f'$$P={tex_num(p["pb"])}-{tex_num(p["pa"])}={tex_num(self.solve(p))}.$$')
        else:
            cond = (f'При выпечке хлеба производится контрольное взвешивание свежей буханки. Известно, что вероятность того, что её масса '
                    f'окажется меньше {p["b"]} г, равна {dec(p["pb"])}. Вероятность того, что масса буханки окажется больше {p["a"]} г, '
                    f'равна {dec(p["pa"])}. Найдите вероятность того, что масса буханки окажется больше {p["a"]} г, но меньше {p["b"]} г.')
            sol = (f'Событие «меньше {p["b"]} г» и событие «больше {p["a"]} г» вместе покрывают все исходы, а их пересечение — искомое. '
                   f'$$P(A\\cap B)=P(A)+P(B)-P(A\\cup B)={tex_num(p["pb"])}+{tex_num(p["pa"])}-1={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        if rng.random() < 0.5:
            a = rng.randint(10, 20)
            return {'kind': 'bus', 'b': a + rng.randint(5, 12), 'pb': Fraction(rng.randint(80, 97), 100), 'a': a,
                    'pa': Fraction(rng.randint(40, 70), 100)}
        mass = rng.choice([500, 600, 800, 1000])
        d = rng.choice([10, 20])
        return {'kind': 'bread', 'b': mass + d, 'pb': Fraction(rng.randint(85, 98), 100), 'a': mass - d,
                'pa': Fraction(rng.randint(80, 97), 100)}


class Exams(Prob):
    """Решит больше k задач / больше k−1 → ровно k; несовместные темы → сумма"""
    topic, code = 'Сложение вероятностей', '5.exams'
    patterns = [r'(?P<kind1>учащийся А\. верно решит больше (?P<k>\w+) задач, равна ' + P + r'\. Вероятность того, что А\. верно решит больше (?P<k2>\w+) задач, равна (?P<p2>\d+,\d+))',
                r'(?P<kind2>вопрос по теме «(?P<t1>[^»]+)», равна (?P<q1>\d+,\d+)\. Вероятность того, что это вопрос по теме «(?P<t2>[^»]+)», равна (?P<q2>\d+,\d+))']

    def parse(self, m, task):
        g = m.groupdict()
        if g.get('kind1'):
            return {'kind': 'exact', 'p1': _p(m.group(3)), 'p2': _p(g['p2']), 'k': g['k'], 'k2': g['k2']}
        return {'kind': 'union', 'p1': _p(g['q1']), 'p2': _p(g['q2']), 't1': g['t1'], 't2': g['t2']}

    def solve(self, p):
        return p['p2'] - p['p1'] if p['kind'] == 'exact' else p['p1'] + p['p2']

    def build(self, p):
        if p['kind'] == 'exact':
            words = {'трёх': ('трёх', 'двух', 3), 'четырёх': ('четырёх', 'трёх', 4), 'пяти': ('пяти', 'четырёх', 5), 'шести': ('шести', 'пяти', 6)}
            k, kp, n = words[p.get('k', 'четырёх')]
            cond = (f'Вероятность того, что на тестировании по математике учащийся А. верно решит больше {k} задач, равна {dec(p["p1"])}. '
                    f'Вероятность того, что А. верно решит больше {kp} задач, равна {dec(p["p2"])}. Найдите вероятность того, что А. верно '
                    f'решит ровно {n} задачи.' if n < 5 else '')
            if n >= 5:
                cond = (f'Вероятность того, что на тестировании по математике учащийся А. верно решит больше {k} задач, равна {dec(p["p1"])}. '
                        f'Вероятность того, что А. верно решит больше {kp} задач, равна {dec(p["p2"])}. Найдите вероятность того, что А. верно '
                        f'решит ровно {n} задач.')
            sol = (f'Событие «больше {kp}» — объединение несовместных событий «ровно {n}» и «больше {k}». '
                   f'$$P=\\,{tex_num(p["p2"])}-{tex_num(p["p1"])}={tex_num(self.solve(p))}.$$')
        else:
            cond = (f'На экзамене по геометрии школьник должен ответить на один вопрос из списка экзаменационных вопросов. Вероятность того, '
                    f'что это вопрос по теме «{p["t1"]}», равна {dec(p["p1"])}. Вероятность того, что это вопрос по теме «{p["t2"]}», равна '
                    f'{dec(p["p2"])}. Вопросов, которые одновременно относятся к этим двум темам, нет. Найдите вероятность того, что на экзамене '
                    f'школьнику достанется вопрос по одной из этих двух тем.')
            sol = (f'События несовместны, поэтому вероятности складываются: $${tex_num(p["p1"])}+{tex_num(p["p2"])}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        if rng.random() < 0.5:
            p1 = Fraction(rng.randint(40, 75), 100)
            return {'kind': 'exact', 'p1': p1, 'p2': p1 + Fraction(rng.randint(5, 20), 100),
                    'k': rng.choice(['трёх', 'четырёх', 'пяти']), 'k2': ''}
        t1, t2 = rng.sample(['Вписанная окружность', 'Тригонометрия', 'Параллелограмм', 'Векторы', 'Подобие', 'Площади'], 2)
        return {'kind': 'union', 'p1': Fraction(rng.randint(5, 40), 100), 'p2': Fraction(rng.randint(5, 40), 100), 't1': t1, 't2': t2}


class Lamps(Prob):
    """n ламп перегорают независимо с вероятностью p: хотя бы одна не перегорит = 1 − pⁿ"""
    topic, code = 'Независимые события', '5.lamps'
    patterns = [r'Помещение освещается (?:фонарём с )?(\w+) лампами\. Вероятность перегорания (?:каждой|одной) лампы в течение года равна ' + P]

    WORDS = {'двумя': 2, 'тремя': 3, 'четырьмя': 4, 'пятью': 5}

    def parse(self, m, task):
        return {'n': self.WORDS[m.group(1)], 'p': _p(m.group(2))}

    def solve(self, p):
        return 1 - p['p'] ** p['n']

    def build(self, p):
        n, q = p['n'], p['p']
        word = {2: 'двумя', 3: 'тремя', 4: 'четырьмя', 5: 'пятью'}[n]
        cond = (f'Помещение освещается {word} лампами. Вероятность перегорания каждой лампы в течение года равна {dec(q)}. Лампы перегорают '
                f'независимо друг от друга. Найдите вероятность того, что в течение года хотя бы одна лампа не перегорит.')
        sol = (f'Противоположное событие — перегорят {"обе" if n == 2 else "все " + str(n)} лампы; по независимости его вероятность ${tex_num(q)}^{n}={tex_num(q ** n)}$. '
               f'$$P=1-{tex_num(q ** n)}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        return {'n': rng.choice([2, 3, 4]), 'p': _dp(rng, 1, 9)}


class Captains(Prob):
    """Жребий с монетой в нескольких матчах: все разы / не больше одного раза / только во второй игре"""
    topic, code = 'Независимые события', '5.coin-matches'
    patterns = [r'Команда «([^»]+)» играет (\w+) матча с разными командами\. Найдите вероятность того, что в этих матчах команда «[^»]+» начнёт игру с мячом (все (?:\w+ )?раза|не (?:более|больше) одного раза|ровно (\w+) раза?)',
                r'Команда «([^»]+)» по очереди играет с командами «[^»]+», «[^»]+» и «[^»]+»\. Найдите вероятность того, что «[^»]+» будет начинать с мячом только (\w+) игру']

    WORDS = {'два': 2, 'две': 2, 'три': 3, 'четыре': 4, 'один': 1}

    def parse(self, m, task):
        if 'по очереди' in m.group(0):
            return {'team': m.group(1), 'n': 3, 'event': 'only'}
        n = self.WORDS[m.group(2)]
        ev = m.group(3)
        if ev.startswith('все'):
            return {'team': m.group(1), 'n': n, 'event': 'all'}
        if ev.startswith('не'):
            return {'team': m.group(1), 'n': n, 'event': 'le1'}
        return {'team': m.group(1), 'n': n, 'event': 'eq', 'k': self.WORDS[m.group(4)]}

    def solve(self, p):
        n = p['n']
        if p['event'] in ('all', 'only'):
            return Fraction(1, 2 ** n)
        if p['event'] == 'le1':
            return Fraction(1 + n, 2 ** n)
        return Fraction(math.comb(n, p['k']), 2 ** n)

    def build(self, p):
        n, team = p['n'], p['team']
        nw = {2: 'два', 3: 'три', 4: 'четыре'}[n]
        head = 'Перед началом футбольного матча судья бросает монетку, чтобы определить, какая из команд начнёт игру с мячом. '
        if p['event'] == 'only':
            cond = (f'Перед началом волейбольного матча капитаны команд тянут жребий, чтобы определить, какая из команд начнёт игру с мячом. '
                    f'Команда «{team}» по очереди играет с командами «Статор», «Стартёр» и «Мотор». Найдите вероятность того, что «{team}» '
                    f'будет начинать с мячом только вторую игру.')
            sol = ('Нужно: в первой игре не начинать, во второй — начинать, в третьей — нет. Жребии независимы, каждый исход имеет вероятность '
                   '$\\frac{1}{2}$: $$P=\\frac{1}{2}\\cdot\\frac{1}{2}\\cdot\\frac{1}{2}=0{,}125.$$')
            return cond, sol
        ev = {'all': f'все {nw} раза', 'le1': 'не более одного раза', 'eq': f'ровно {["", "один", "два", "три"][p.get("k", 1)]} раз'
              + ('а' if p.get('k') in (2, 3) else '')}[p['event']]
        cond = head + f'Команда «{team}» играет {nw} матча с разными командами. Найдите вероятность того, что в этих матчах команда «{team}» начнёт игру с мячом {ev}.'
        total = 2 ** n
        if p['event'] == 'all':
            sol = f'Жребии независимы, в каждом шанс $\\frac{{1}}{{2}}$: $$P=\\left(\\frac{{1}}{{2}}\\right)^{n}={tex_num(self.solve(p))}.$$'
        elif p['event'] == 'le1':
            sol = (f'Всего исходов $2^{n}={total}$. Подходят: ни разу (1 исход) и ровно один раз ({n} исхода). '
                   f'$$P=\\frac{{1+{n}}}{{{total}}}={tex_num(self.solve(p))}.$$')
        else:
            sol = (f'Всего исходов $2^{n}={total}$, подходящих $C_{n}^{p["k"]}={math.comb(n, p["k"])}$. '
                   f'$$P=\\frac{{{math.comb(n, p["k"])}}}{{{total}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        team = rng.choice(['Метеор', 'Сапфир', 'Изумруд', 'Буревестник', 'Звезда', 'Ракета', 'Комета'])
        ev = rng.choice(['all', 'le1', 'eq', 'only'])
        n = rng.choice([2, 3, 4]) if ev != 'only' else 3
        p = {'team': team, 'n': n, 'event': ev}
        if ev == 'eq':
            p['k'] = rng.randint(1, n - 1)
        return p


class DiceCondition(Prob):
    """Две кости, известно, что k очков не выпало ни разу: условная вероятность суммы s"""
    topic, code = 'Условная вероятность', '5.dice'
    patterns = [r'Игральную кость бросили два раза\. Известно, что (\w+) очк\w+ не выпало ни разу\. Найдите при этом условии вероятность события «сумма очков равна (\d+)»']

    WORDS = {'одно': 1, 'два': 2, 'три': 3, 'четыре': 4, 'пять': 5, 'шесть': 6}

    def parse(self, m, task):
        return {'no': self.WORDS[m.group(1)], 's': int(m.group(2))}

    def _outcomes(self, p):
        allowed = [x for x in range(1, 7) if x != p['no']]
        pairs = list(itertools.product(allowed, repeat=2))
        return pairs, [q for q in pairs if sum(q) == p['s']]

    def solve(self, p):
        pairs, good = self._outcomes(p)
        return Fraction(len(good), len(pairs))

    def build(self, p):
        word = {1: 'одно очко', 2: 'два очка', 3: 'три очка', 4: 'четыре очка', 5: 'пять очков', 6: 'шесть очков'}[p['no']]
        cond = (f'Игральную кость бросили два раза. Известно, что {word} не выпало ни разу. Найдите при этом условии вероятность события '
                f'«сумма очков равна {p["s"]}».')
        pairs, good = self._outcomes(p)
        listing = ', '.join(f'({a};{b})' for a, b in good)
        sol = (f'При условии на каждой кости возможны 5 значений, всего $5\\cdot 5=25$ равновозможных исходов. Сумму {p["s"]} дают: {listing} '
               f'— это ${len(good)}$ {plural(len(good), "исход", "исхода", "исходов")}. $$P=\\frac{{{len(good)}}}{{25}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        p = {'no': rng.randint(1, 6), 's': rng.randint(3, 11)}
        return p if self._outcomes(p)[1] else None


class Cartridges(Prob):
    """Стрелок стреляет до первого попадания: наименьшее число патронов для P ≥ p"""
    topic, code = 'Независимые события', '5.cartridges'
    patterns = [r'попадает в цель с вероятностью ' + P + r' при каждом отдельном выстреле\. Какое наименьшее количество патронов нужно дать стрелку, '
                r'чтобы он поразил цель с вероятностью не (?:меньше|менее) ' + P]

    def parse(self, m, task):
        return {'p': _p(m.group(1)), 'target': _p(m.group(2))}

    def solve(self, p):
        miss = 1 - p['p']
        n = 1
        while 1 - miss ** n < p['target']:
            n += 1
        return n

    def build(self, p):
        q, t = p['p'], p['target']
        n = self.solve(p)
        cond = (f'Стрелок в тире стреляет по мишени до тех пор, пока не поразит её. Известно, что он попадает в цель с вероятностью {dec(q)} '
                f'при каждом отдельном выстреле. Какое наименьшее количество патронов нужно дать стрелку, чтобы он поразил цель с вероятностью '
                f'не меньше {dec(t)}?')
        rows = '; '.join(f'$n={k}$: $1-{tex_num(1 - q)}^{{{k}}}={tex_num(1 - (1 - q) ** k)}$' for k in range(1, n + 1))
        sol = (f'С $n$ патронами стрелок промахнётся все разы с вероятностью ${tex_num(1 - q)}^n$, поразит цель — с вероятностью $1-{tex_num(1 - q)}^n$. '
               f'Перебираем: {rows}. Впервые не меньше ${tex_num(t)}$ при $n={n}$.')
        return cond, sol

    def sample(self, rng):
        return {'p': _dp(rng, 3, 8), 'target': Fraction(rng.choice([7, 8, 9, 95]), 10 if rng.random() < 0.8 else 100)}

    def nice(self, x):
        return isinstance(x, int) and 2 <= x <= 6


TEMPLATES = [Batteries(), Shooter(), CoffeeMachines(), Markers(), Interval(), Exams(), Lamps(), Captains(), DiceCondition(), Cartridges()]
EXTRA = []
