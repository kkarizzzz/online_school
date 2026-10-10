"""№ 4. Простая теория вероятностей: классическое определение"""
import random
import re
from fractions import Fraction

from app.bankgen.core import Rendered, Template, dec, frac, nice_number, tex_frac, tex_num

ORDINALS = ['первым', 'вторым', 'третьим', 'четвёртым', 'пятым', 'шестым', 'седьмым', 'восьмым', 'девятым', 'десятым',
            'одиннадцатым', 'двенадцатым', 'тринадцатым', 'четырнадцатым', 'пятнадцатым']
WORD_NUM = {'одного': 1, 'двух': 2, 'трёх': 3, 'четырёх': 4, 'пяти': 5, 'шести': 6, 'семи': 7, 'восьми': 8, 'девяти': 9,
            'десяти': 10, 'одиннадцати': 11, 'двенадцати': 12, 'тринадцати': 13, 'четырнадцати': 14, 'пятнадцати': 15,
            'двадцати': 20, 'трёх человек': 3, 'семь': 7, 'трёх': 3}
COUNT_WORDS = {2: 'двух', 3: 'трёх', 4: 'четырёх', 5: 'пяти'}
PEOPLE_WORDS = {2: 'двух человек', 3: 'трёх человек', 4: 'четырёх человек', 5: 'пять человек', 6: 'шесть человек',
                7: 'семь человек', 8: 'восемь человек'}


def _int(s: str) -> int:
    s = s.strip()
    if s.isdigit():
        return int(s)
    for w, n in WORD_NUM.items():
        if s.startswith(w):
            return n
    raise ValueError(s)


class Prob(Template):
    number = 4
    topic = 'Классическое определение вероятности'

    def nice(self, x):
        return nice_number(x, max_decimals=3) and 0 < x < 1

    def render(self, p):
        cond, sol = self.build(p)
        return Rendered(cond, sol + f'\n\n**Ответ:** {dec(self.solve(p))}.')

    def build(self, p) -> tuple[str, str]:
        raise NotImplementedError


def _classic(fav: int, total: int, fav_text: str, total_text: str) -> str:
    return (f'Все исходы равновозможны: всего их ${total}$ ({total_text}), благоприятных — ${fav}$ ({fav_text}). '
            f'$$P=\\frac{{{fav}}}{{{total}}}={tex_num(Fraction(fav, total))}.$$')


class Defects(Prob):
    """В среднем k из n с дефектом → вероятность без дефекта"""
    code = '4.defects'
    patterns = [r'В среднем (\d+) (сум\w*) из (\d+) имеют скрыт\w+ дефект\w*',
                r'В среднем из (\d+) (садовых насосов), поступивших в продажу, (\d+) подтекают']

    ITEMS = [('сумок', 'сумка', 'скрытый дефект', 'без скрытого дефекта'), ('насосов', 'насос', 'подтекают', 'не подтекает'),
             ('фонариков', 'фонарик', 'неисправны', 'окажется исправным'), ('чайников', 'чайник', 'с браком', 'окажется без брака')]

    def parse(self, m, task):
        if 'насос' in m.group(2):
            return {'n': int(m.group(1)), 'k': int(m.group(3)), 'item': 1}
        return {'k': int(m.group(1)), 'n': int(m.group(3)), 'item': 0}

    def solve(self, p):
        return 1 - Fraction(p['k'], p['n'])

    def build(self, p):
        k, n = p['k'], p['n']
        many, one, bad, good = self.ITEMS[p['item']]
        if p['item'] == 0:
            cond = f'Фабрика выпускает сумки. В среднем {k} сумок из {n} имеют скрытый дефект. Найдите вероятность того, что купленная сумка окажется без скрытого дефекта.'
        elif p['item'] == 1:
            cond = f'В среднем из {n} садовых насосов, поступивших в продажу, {k} подтекают. Найдите вероятность того, что один случайно выбранный для контроля насос не подтекает.'
        else:
            cond = f'В среднем из {n} {many}, поступивших в продажу, {k} {bad}. Найдите вероятность того, что случайно выбранный {one} {good}.'
        sol = (f'Из ${n}$ изделий без дефекта ${n}-{k}={n - k}$. $$P=\\frac{{{n - k}}}{{{n}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        n = rng.choice([20, 25, 40, 50, 80, 100, 125, 200, 250, 400, 500, 1000, 2000])
        k = rng.randint(1, max(2, n // 8))
        return {'k': k, 'n': n, 'item': rng.randint(0, 3)}


class Tickets(Prob):
    """Сборник билетов: k из n с вопросом по теме → достанется / не достанется"""
    code = '4.tickets'
    patterns = [r'В сборнике билетов по (\w+) (?:всего )?(\d+) билет\w*, в (\w+) из них встречается вопрос по теме «([^»]+)»\. '
                r'Найдите вероятность того, что в случайно выбранном на экзамене билете школьнику (\*\*не достанется\*\*|не достанется|достанется)']

    SUBJECTS = [('математике', 'Логарифмы'), ('физике', 'Оптика'), ('химии', 'Углеводороды'), ('истории', 'Древняя Русь'),
                ('географии', 'Климат'), ('биологии', 'Клетка'), ('информатике', 'Алгоритмы'), ('литературе', 'Серебряный век')]

    def parse(self, m, task):
        return {'subj': m.group(1), 'n': int(m.group(2)), 'k': _int(m.group(3)), 'theme': m.group(4),
                'neg': m.group(5).strip('*').startswith('не ')}

    def solve(self, p):
        q = Fraction(p['k'], p['n'])
        return 1 - q if p['neg'] else q

    def build(self, p):
        n, k, neg = p['n'], p['k'], p['neg']
        cond = (f'В сборнике билетов по {p["subj"]} всего {n} билетов, в {k} из них встречается вопрос по теме «{p["theme"]}». '
                f'Найдите вероятность того, что в случайно выбранном на экзамене билете школьнику {"не достанется" if neg else "достанется"} '
                f'вопрос по теме «{p["theme"]}».')
        fav = n - k if neg else k
        sol = _classic(fav, n, 'билеты без этой темы' if neg else 'билеты с этой темой', 'число билетов')
        return cond, sol

    def sample(self, rng):
        subj, theme = rng.choice(self.SUBJECTS)
        n = rng.choice([20, 25, 40, 50, 60, 80, 100])
        return {'subj': subj, 'n': n, 'k': rng.randint(2, n - 2), 'theme': theme, 'neg': rng.random() < 0.5}


class Countries(Prob):
    """Спортсмены/учёные из нескольких стран, порядок — жребий: вероятность, что k-м выступит представитель страны"""
    code = '4.order'
    patterns = [r'(?P<intro>В соревнованиях по толканию ядра участвуют спортсмены из \w+ стран|На конференцию приехали учёные из \w+ стран|'
                r'В чемпионате по гимнастике участвуют (?P<total>\d+) спортсменок|На чемпионате по прыжкам в воду выступают (?P<total2>\d+) спортсменов)'
                r'(?P<rest>.*?)Найдите вероятность того, что (?P<q>.+?)\.\s*$']

    def parse(self, m, task):
        rest = m.group('rest')
        groups = [(int(a), b) for a, b in re.findall(r'(\d+) (?:\w+ )?из ([А-ЯЁ]\w+)', rest)]
        total = int(m.group('total') or m.group('total2') or 0) or sum(a for a, _ in groups)
        q = m.group('q')
        cm = re.search(r'из ([А-ЯЁ]\w+)\s*$', q) or re.search(r'из ([А-ЯЁ]\w+)', q)
        if not cm:
            return None
        country = cm.group(1)
        counts = dict((c, a) for a, c in groups)
        if country in counts:
            fav = counts[country]
        else:
            om = re.search(r'остальные\s*(?:—\s*)?из ([А-ЯЁ]\w+)', rest)
            if not om or om.group(1) != country:
                return None
            fav = total - sum(counts.values())
        kind = 'sport' if 'спортсмен' in m.group('intro') else 'science'
        return {'kind': kind, 'total': total, 'fav': fav, 'country': country, 'text': m.group(0)}

    def solve(self, p):
        return Fraction(p['fav'], p['total'])

    def build(self, p):
        total, fav = p['total'], p['fav']
        if 'text' in p:
            cond = p['text']
        else:
            pos = ORDINALS[p['pos'] - 1]
            listing = ', '.join(f'{n} из {c}' for c, n in p['groups'])
            if p['kind'] == 'science':
                cond = (f'На конференцию приехали учёные из {COUNT_WORDS[len(p["groups"])]} стран: {listing}. Каждый из них делает '
                        f'на конференции один доклад. Порядок докладов определяется жеребьёвкой. Найдите вероятность того, что '
                        f'{pos} окажется доклад учёного из {p["country"]}.')
            else:
                cond = (f'В соревнованиях по прыжкам в длину участвуют спортсмены из {COUNT_WORDS[len(p["groups"])]} стран: {listing}. '
                        f'Порядок, в котором выступают спортсмены, определяется жребием. Найдите вероятность того, что спортсмен, '
                        f'выступающий {pos}, окажется из {p["country"]}.')
        sol = (f'Номер выступления не влияет на вероятность: на любое место с равными шансами попадает каждый из ${total}$ участников. '
               f'Из них {fav} — из {p["country"]}. $$P=\\frac{{{fav}}}{{{total}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    COUNTRIES = ['России', 'Китая', 'Франции', 'Германии', 'Италии', 'Испании', 'Бразилии', 'Канады', 'Японии', 'Норвегии', 'Сербии', 'Чехии']

    def sample(self, rng):
        k = rng.choice([3, 3, 4])
        names = rng.sample(self.COUNTRIES, k)
        counts = [rng.randint(2, 15) for _ in range(k)]
        total = sum(counts)
        i = rng.randrange(k)
        groups = list(zip(names, counts))
        return {'kind': rng.choice(['sport', 'science']), 'total': total, 'fav': counts[i], 'country': names[i],
                'groups': groups, 'pos': rng.randint(1, min(12, total))}


class Rooms(Prob):
    """Олимпиада в нескольких аудиториях: вероятность попасть в запасную"""
    code = '4.rooms'
    patterns = [r'На олимпиаде по (\w+) (\d+) участник\w* разместили в (\w+) аудитори\w+\. В первых (\w+) удалось разместить по (\d+) человек']

    def parse(self, m, task):
        return {'subj': m.group(1), 'n': int(m.group(2)), 'first': _int(m.group(4)), 'per': int(m.group(5))}

    def solve(self, p):
        rest = p['n'] - p['first'] * p['per']
        if rest <= 0:
            raise ValueError('запасная аудитория пуста')
        return Fraction(rest, p['n'])

    def build(self, p):
        n, first, per = p['n'], p['first'], p['per']
        rooms = first + 1
        rooms_word = {3: 'трёх', 4: 'четырёх', 5: 'пяти'}[rooms]
        first_word = {2: 'двух', 3: 'трёх', 4: 'четырёх'}[first]
        cond = (f'На олимпиаде по {p["subj"]} {n} участников разместили в {rooms_word} аудиториях. В первых {first_word} удалось разместить '
                f'по {per} человек, оставшихся перевели в запасную аудиторию в другом корпусе. Найдите вероятность того, что случайно '
                f'выбранный участник писал олимпиаду в запасной аудитории.')
        rest = n - first * per
        sol = (f'В запасной аудитории ${n}-{first}\\cdot {per}={rest}$ человек. $$P=\\frac{{{rest}}}{{{n}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        first = rng.choice([2, 3, 4])
        per = rng.choice([50, 60, 80, 100, 110, 120, 150])
        n = rng.choice([200, 250, 300, 400, 500, 600, 750, 1000])
        return {'subj': rng.choice(['математике', 'физике', 'химии', 'биологии', 'информатике']), 'n': n, 'first': first, 'per': per}


class Lottery(Prob):
    """Жребий из нескольких человек: выберут конкретного / попадёт в первый рейс"""
    code = '4.lottery'
    patterns = [r'В группе туристов (\d+) человек\. С помощью жребия они выбирают (\w+) человек',
                r'В группе туристов (\d+) человек\. Их вертолётом доставляют в труднодоступный район, перевозя по (\d+) человека? за рейс']

    def parse(self, m, task):
        return {'n': int(m.group(1)), 'k': _int(m.group(2)), 'kind': 'heli' if 'вертолёт' in m.group(0) else 'shop'}

    def solve(self, p):
        return Fraction(p['k'], p['n'])

    def build(self, p):
        n, k = p['n'], p['k']
        if p['kind'] == 'heli':
            cond = (f'В группе туристов {n} человек. Их вертолётом доставляют в труднодоступный район, перевозя по {k} человека за рейс. '
                    f'Порядок, в котором вертолёт перевозит туристов, случаен. Найдите вероятность того, что турист В., входящий в состав '
                    f'группы, полетит первым рейсом вертолёта.')
            sol = (f'В первом рейсе ${k}$ мест из ${n}$, и турист В. с равными шансами занимает любое из ${n}$ мест в общей очереди. '
                   f'$$P=\\frac{{{k}}}{{{n}}}={tex_num(self.solve(p))}.$$')
        else:
            cond = (f'В группе туристов {n} человек. С помощью жребия они выбирают {PEOPLE_WORDS.get(k, f"{k} человек")}, которые должны идти '
                    f'в село в магазин за продуктами. Какова вероятность того, что турист Д., входящий в состав группы, пойдёт в магазин?')
            sol = (f'Жребий выбирает ${k}$ человек из ${n}$, у каждого туриста одинаковые шансы. $$P=\\frac{{{k}}}{{{n}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        kind = rng.choice(['heli', 'shop'])
        k = rng.choice([2, 3, 4]) if kind == 'heli' else rng.choice([2, 3, 4, 5, 6])
        n = k * rng.randint(3, 10) if kind == 'heli' else rng.choice([10, 12, 15, 16, 20, 24, 25, 30])
        return {'n': n, 'k': k, 'kind': kind}


class Complement(Prob):
    """Противоположное событие: P(ниже) = p → P(не ниже) = 1 - p"""
    code = '4.complement'
    patterns = [r'температура тела здорового человека окажется ниже чем .*?, равна (\d+,\d+)\.']

    def parse(self, m, task):
        return {'p': Fraction(m.group(1).replace(',', '.'))}

    def solve(self, p):
        return 1 - p['p']

    def build(self, p):
        t = p.get('t', '36{,}8')
        cond = (f'Вероятность того, что в случайный момент времени температура тела здорового человека окажется ниже чем ${t}^\\circ C$, '
                f'равна {dec(p["p"])}. Найдите вероятность того, что в случайный момент времени у здорового человека температура '
                f'окажется ${t}^\\circ C$ или выше.')
        sol = (f'События «ниже ${t}^\\circ$» и «${t}^\\circ$ или выше» противоположны, сумма их вероятностей равна 1: '
               f'$$P=1-{tex_num(p["p"])}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        return {'p': Fraction(rng.randint(51, 97), 100), 't': rng.choice(['36{,}8', '36{,}9', '37', '36{,}7'])}


class Festival(Prob):
    """Конкурс в несколько дней: вероятность выступить в заданный день"""
    code = '4.festival'
    patterns = [r'Конкурс исполнителей проводится в (\d+) дн\w+\. Всего заявлено (\d+) выступлений.*?В первый день запланировано (\d+) выступлений, '
                r'остальные распределены поровну между оставшимися днями\..*?состоится во? (\w+) день']

    DAYS = {'второй': 2, 'третий': 3, 'четвёртый': 4, 'пятый': 5, 'последний': -1}

    def parse(self, m, task):
        return {'days': int(m.group(1)), 'n': int(m.group(2)), 'first': int(m.group(3)), 'day': self.DAYS.get(m.group(4), 0)}

    def solve(self, p):
        per = Fraction(p['n'] - p['first'], p['days'] - 1)
        if per.denominator != 1:
            raise ValueError('не делится поровну')
        return Fraction(p['first'], p['n']) if p['day'] == 1 else per / p['n']

    def build(self, p):
        days, n, first = p['days'], p['n'], p['first']
        per = (n - first) // (days - 1)
        word = {2: 'второй', 3: 'третий', 4: 'четвёртый', 5: 'пятый'}[p['day']]
        cond = (f'Конкурс исполнителей проводится в {days} дня. Всего заявлено {n} выступлений: по одному от каждой страны, участвующей '
                f'в конкурсе. Исполнитель из России участвует в конкурсе. В первый день запланировано {first} выступлений, остальные '
                f'распределены поровну между оставшимися днями. Порядок выступлений определяется жеребьёвкой. Какова вероятность того, '
                f'что выступление исполнителя из России состоится {"во" if word == "второй" else "в"} {word} день конкурса?').replace(' дня.', f' {"дня" if days < 5 else "дней"}.')
        sol = (f'На каждый день, кроме первого, приходится $\\frac{{{n}-{first}}}{{{days - 1}}}={per}$ выступлений. Исполнитель с равными '
               f'шансами получает любой из ${n}$ номеров, поэтому $$P=\\frac{{{per}}}{{{n}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        days = rng.choice([3, 4, 5])
        per = rng.choice([5, 8, 10, 12, 15, 20])
        first = rng.choice([10, 12, 16, 20, 24, 30])
        n = first + per * (days - 1)
        return {'days': days, 'n': n, 'first': first, 'day': rng.randint(2, days)}


class Names(Prob):
    """Жребий среди детей: начнёт мальчик/девочка"""
    code = '4.names'
    patterns = [r'([А-ЯЁ][а-яё]+(?:, [А-ЯЁ][а-яё]+)+ и [А-ЯЁ][а-яё]+) бросили жребий — кому начинать игру\. Найдите вероятность того, что начинать игру должен будет (мальчик|девочка)']

    BOYS = {'Дима', 'Марат', 'Петя', 'Коля', 'Саша', 'Миша', 'Ваня', 'Егор', 'Артём', 'Лёша', 'Гриша', 'Андрей', 'Олег'}
    GIRLS = ['Надя', 'Света', 'Оля', 'Катя', 'Аня', 'Маша', 'Вера', 'Лена', 'Юля', 'Даша', 'Зоя']

    def parse(self, m, task):
        names = re.split(r', | и ', m.group(1))
        return {'names': names, 'who': m.group(2)}

    def solve(self, p):
        boys = sum(1 for n in p['names'] if n in self.BOYS)
        fav = boys if p['who'] == 'мальчик' else len(p['names']) - boys
        return Fraction(fav, len(p['names']))

    def build(self, p):
        names = p['names']
        listing = ', '.join(names[:-1]) + ' и ' + names[-1]
        boys = [n for n in names if n in self.BOYS]
        cond = f'{listing} бросили жребий — кому начинать игру. Найдите вероятность того, что начинать игру должен будет {p["who"]}.'
        fav = len(boys) if p['who'] == 'мальчик' else len(names) - len(boys)
        sol = _classic(fav, len(names), 'мальчики' if p['who'] == 'мальчик' else 'девочки', 'детей')
        return cond, sol

    def sample(self, rng):
        b, g = rng.randint(1, 4), rng.randint(1, 4)
        names = rng.sample(sorted(self.BOYS), b) + rng.sample(self.GIRLS, g)
        rng.shuffle(names)
        return {'names': names, 'who': rng.choice(['мальчик', 'девочка'])}


class TwoCoins(Prob):
    """Монету бросают дважды/трижды: решка ровно k раз, орёл ни разу"""
    code = '4.coins'
    patterns = [r'симметричную монету бросают (дважды|трижды)\. Найдите вероятность того, что (решка|орёл) (выпадет ровно (\w+) раза?|не выпадет ни разу)']

    WORDS = {'один': 1, 'два': 2, 'три': 3}

    def parse(self, m, task):
        n = 2 if m.group(1) == 'дважды' else 3
        k = 0 if 'ни разу' in m.group(3) else self.WORDS[m.group(4)]
        return {'n': n, 'side': m.group(2), 'k': k}

    def solve(self, p):
        from math import comb
        return Fraction(comb(p['n'], p['k']), 2 ** p['n'])

    def build(self, p):
        from math import comb
        n, k, side = p['n'], p['k'], p['side']
        times = 'дважды' if n == 2 else 'трижды'
        event = 'не выпадет ни разу' if k == 0 else f'выпадет ровно {["", "один", "два", "три"][k]} раз' + ('а' if k in (2, 3) else '')
        cond = f'В случайном эксперименте симметричную монету бросают {times}. Найдите вероятность того, что {side} {event}.'
        letter = 'Р' if side == 'решка' else 'О'
        other = 'О' if letter == 'Р' else 'Р'
        outcomes = [''.join(x) for x in __import__('itertools').product([letter, other], repeat=n)]
        good = [o for o in outcomes if o.count(letter) == k]
        sol = (f'Все исходы: {", ".join(outcomes)} — их ${2 ** n}$, они равновозможны. Благоприятные: {", ".join(good)} — ${len(good)}$. '
               f'$$P=\\frac{{{len(good)}}}{{{2 ** n}}}={tex_num(self.solve(p))}.$$')
        return cond, sol

    def sample(self, rng):
        n = rng.choice([2, 3])
        return {'n': n, 'side': rng.choice(['решка', 'орёл']), 'k': rng.randint(0, n - 1)}


TEMPLATES = [Defects(), Tickets(), Countries(), Rooms(), Lottery(), Complement(), Festival(), Names(), TwoCoins()]
EXTRA = []
