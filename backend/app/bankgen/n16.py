"""
№ 16. Экономические задачи: кредиты и вклады.

Каждый сюжет считает ответ своей формулой и сверяет его с общим движком схем (credit.Scheme),
который ничего не знает о сюжете: только начисление процентов, платежи и остатки. Расхождение — ошибка разбора.
"""
import math
import random
import re
from fractions import Fraction

import sympy as sp

from app.bankgen.core import Rendered, Template, compact, dec, nice_number, tex_num
from app.bankgen.credit import Scheme

F = Fraction
NUM = r'(\d[\d ]*(?:[,.]\d+)?)'


def _n(s: str) -> Fraction:
    return Fraction(s.replace(' ', '').replace(' ', '').replace(',', '.'))


def _rub(v, unit: str) -> str:
    """Число с разделителем тысяч: 1 234 567"""
    v = F(v)
    s = dec(v)
    whole, _, frac_part = s.partition(',')
    neg = whole.startswith('-')
    whole = f'{int(whole.lstrip("-")):,}'.replace(',', ' ')
    return ('-' if neg else '') + whole + (',' + frac_part if frac_part else '') + (f' {unit}' if unit else '')


def _mult(unit: str) -> int:
    return {'млн': 10 ** 6, 'тыс': 1000, '': 1}[unit]


def _unit_of(s: str) -> str:
    return 'млн' if 'млн' in s else 'тыс' if 'тыс' in s else ''


YEARS_WORD = {2: 'два', 3: 'три', 4: 'четыре', 5: 'пять', 6: 'шесть', 10: 'десять'}
YEARS_GEN = {2: 'двумя', 3: 'тремя', 4: 'четырьмя', 5: 'пятью'}


class Credit(Template):
    number = 16
    topic = 'Кредиты'
    detailed = True
    difficulty = 2

    def render(self, p):
        cond, sol = self.build(p)
        return Rendered(cond, sol + f'\n\n**Ответ:** {self.shown(p, self.value(p))}.')

    def shown(self, p, ans) -> str:
        return dec(ans)

    def solve(self, p):
        v = self.value(p)
        check = self.engine(p)
        if check is not None and abs(float(check) - float(v)) > 1e-6 * max(1, abs(float(v))):
            raise ValueError(f'движок схем не согласен: {check} ≠ {v}')
        return {'accepted': [dec(v)], 'display': self.shown(p, v)}

    def value(self, p):
        raise NotImplementedError

    def engine(self, p):
        return None

    def nice(self, answer):
        v = F(answer['accepted'][0].replace(',', '.'))
        return nice_number(v, 2, limit=10 ** 9) and v > 0


# ---------------------------------------------------------------------------
# 1. Долг уменьшается на p % несколько лет, затем гасится. Известны два из S, r, total — найти третье
# ---------------------------------------------------------------------------

class PercentDecrease(Credit):
    topic, code = 'Кредиты с заданным графиком долга', '16.decrease-pct'
    patterns = [r'кредит на (\w+) года? в размере (?:\$S\$|(\d[\d ]*(?:,\d+)?)) (млн|тыс)\.? рублей.*?увеличивается на (?:\$r\$|(\d+)) ?% .*?'
                r'долг должен быть на (\d+) ?% меньше долга на июль предыдущего года.*?'
                r'(?:сумма всех платежей после полного погашения кредита будет равна (\d[\d ]*) тыс\. рублей\. Найдите \$(r|S)\$|Сколько тыс\. рублей составит сумма всех платежей)']

    WORDS = {'три': 3, 'четыре': 4, 'пять': 5, 'два': 2}

    def parse(self, m, task):
        n = self.WORDS[m.group(1)]
        unit = m.group(3)
        S = _n(m.group(2)) * _mult(unit) / 1000 if m.group(2) else None   # всё в тыс. рублей
        rate = _n(m.group(4)) if m.group(4) else None
        dec_ = _n(m.group(5))
        total = _n(m.group(6)) if m.group(6) else None
        ask = m.group(7) or 'total'
        return {'n': n, 'S': S, 'r': rate, 'k': 1 - dec_ / 100, 'total': total, 'ask': ask}

    def _sum_debts(self, p):
        k, n = p['k'], p['n']
        return sum(k ** i for i in range(n))     # D0 + … + D_{n−1} в долях S

    def value(self, p):
        sd = self._sum_debts(p)
        if p['ask'] == 'r':
            return (p['total'] - p['S']) / p['S'] / sd * 100
        if p['ask'] == 'S':
            return p['total'] / (1 + p['r'] / 100 * sd)
        return p['S'] * (1 + p['r'] / 100 * sd)

    def engine(self, p):
        n, k = p['n'], p['k']
        debts = ['S'] + [f'{k ** i}*S' for i in range(1, n)] + ['0']
        S = p['S'] if p['S'] is not None else 'S'
        rate = p['r'] if p['r'] is not None else 'r'
        eqs = [f'total = {p["total"]}'] if p['total'] is not None else []
        ask = {'r': 'r', 'S': 'S', 'total': 'total'}[p['ask']]
        return Scheme(n=n, rate=rate, S=S, debts=debts, equations=eqs).solve(ask)[0]

    def build(self, p):
        n, k = p['n'], p['k']
        pct = int((1 - k) * 100)
        years = ', '.join(str(2029 + i) for i in range(n - 1))
        s_txt = f'{_rub(p["S"], "тыс. рублей")}' if p['S'] is not None else '$S$ тыс. рублей'
        r_txt = f'{dec(p["r"])} %' if p['r'] is not None else '$r$ %'
        head = (f'В июле 2028 года планируется взять в банке кредит на {YEARS_WORD[n]} {"года" if n < 5 else "лет"} в размере {s_txt}. '
                f'Условия его возврата таковы:\n\n— каждый январь долг увеличивается на {r_txt} по сравнению с концом предыдущего года;\n\n'
                f'— с февраля по июнь каждого года необходимо выплатить одним платежом часть долга;\n\n'
                f'— в июле {years} годов долг должен быть на {pct} % меньше долга на июль предыдущего года;\n\n'
                f'— к июлю {2028 + n} года долг должен быть выплачен полностью.\n\n')
        if p['ask'] == 'total':
            cond = head + 'Сколько тыс. рублей составит сумма всех платежей после полного погашения кредита?'
        else:
            cond = head + (f'Известно, что сумма всех платежей после полного погашения кредита будет равна {_rub(p["total"], "тыс. рублей")}. '
                           f'Найдите ${p["ask"]}$.')
        debts = ', '.join(f'{tex_num(k ** i)}S' if i else 'S' for i in range(n))
        sd = self._sum_debts(p)
        sol = (f'Пусть сумма кредита $S$ тыс. рублей, $q=1+\\frac{{r}}{{100}}$. Каждый год долг уменьшается в ${tex_num(1 / k)}$ раза: '
               f'по июлям он равен ${debts}$, а в июле {2028 + n} года — $0$.\n\n'
               f'Платёж года равен долгу после начисления процентов минус новый долг. Сумма всех платежей — это кредит плюс все начисленные '
               f'проценты: $$\\text{{сумма}}=S+\\frac{{r}}{{100}}\\left({debts}\\right)=S\\left(1+\\frac{{r}}{{100}}\\cdot {tex_num(sd)}\\right).$$\n\n')
        v = self.value(p)
        if p['ask'] == 'r':
            sol += (f'Подставим $S={tex_num(p["S"])}$ и сумму ${tex_num(p["total"])}$: $${tex_num(p["S"])}\\left(1+\\frac{{r}}{{100}}\\cdot {tex_num(sd)}\\right)'
                    f'={tex_num(p["total"])},$$ откуда $r={tex_num(v)}$.')
        elif p['ask'] == 'S':
            sol += (f'При $r={tex_num(p["r"])}$: $$S\\cdot\\left(1+{tex_num(p["r"] / 100)}\\cdot {tex_num(sd)}\\right)=S\\cdot {tex_num(1 + p["r"] / 100 * sd)}'
                    f'={tex_num(p["total"])},$$ откуда $S={tex_num(v)}$.')
        else:
            sol += (f'$$\\text{{сумма}}={tex_num(p["S"])}\\cdot\\left(1+{tex_num(p["r"] / 100)}\\cdot {tex_num(sd)}\\right)={tex_num(v)}.$$')
        return cond, sol

    def sample(self, rng):
        n = rng.choice([3, 3, 4])
        pct = rng.choice([10, 20, 25, 30, 40, 50, 60, 70, 75, 80])
        rate = F(rng.choice([10, 12, 15, 20, 25, 30]))
        S = F(rng.choice([1000, 1200, 1500, 2000, 2400, 2500, 3000, 4000, 5000, 6000, 8000, 10000, 12000]))
        k = 1 - F(pct, 100)
        p = {'n': n, 'S': S, 'r': rate, 'k': k, 'total': None, 'ask': 'total'}
        total = self.value(p)
        ask = rng.choice(['r', 'S', 'total'])
        if ask == 'r':
            return {**p, 'r': None, 'total': total, 'ask': 'r'}
        if ask == 'S':
            return {**p, 'S': None, 'total': total, 'ask': 'S'}
        return p


# ---------------------------------------------------------------------------
# 2. Дифференцированные платежи по месяцам: сумма платежей за календарный год / r / сумма кредита
# ---------------------------------------------------------------------------

class MonthlyEqual(Credit):
    topic, code = 'Дифференцированные платежи', '16.monthly-year'
    patterns = [r'15 декабря (\d{4}) года планируется взять кредит в банке на сумму (?:\*A\*|\$A\$|(\d+)) млн рублей на (\d+) месяц\w*\..*?'
                r'долг возрастает на (?:\*r\*|\$r\$|(\d+)) (?:%|процент\w*).*?(?:Чему равна общая сумма платежей в (\d{4}) году|'
                r'Чему равно \*?(r|A)\*?, если общая сумма платежей в (\d{4}) году составит (\d[\d ]*) тыс\. рублей)']

    def parse(self, m, task):
        y0, S, N, rate = int(m.group(1)), (_n(m.group(2)) * 1000 if m.group(2) else None), int(m.group(3)), (_n(m.group(4)) if m.group(4) else None)
        if m.group(5):
            return {'y0': y0, 'S': S, 'N': N, 'r': rate, 'year': int(m.group(5)), 'ask': 'year-total', 'total': None}
        return {'y0': y0, 'S': S, 'N': N, 'r': rate, 'year': int(m.group(7)), 'ask': m.group(6), 'total': _n(m.group(8))}

    def _months(self, p):
        """Номера платежей (1…N), попадающих в календарный год"""
        start = (p['year'] - p['y0'] - 1) * 12 + 1
        return list(range(start, start + 12))

    def _year_sum(self, S, rate, p):
        N = p['N']
        d = S / N
        # платёж k: d + r/100 · D_{k−1}, D_{k−1} = S − (k−1)d
        return sum(d + rate / 100 * (S - (k - 1) * d) for k in self._months(p))

    def value(self, p):
        if p['ask'] == 'year-total':
            return self._year_sum(p['S'], p['r'], p)
        ms = self._months(p)
        N = p['N']
        if p['ask'] == 'r':
            S = p['S']
            d = S / N
            base = 12 * d
            per_r = sum((S - (k - 1) * d) for k in ms) / 100
            return (p['total'] - base) / per_r
        # A: сумма линейна по S
        unit = self._year_sum(F(1), p['r'], p)
        return p['total'] / unit / 1000      # в млн рублей

    def engine(self, p):
        N = p['N']
        S = p['S'] if p['ask'] != 'A' else 'S'
        debts = ['S'] + [f'S*{N - k}/{N}' for k in range(1, N + 1)]
        rate = p['r'] if p['r'] is not None else 'r'
        ms = self._months(p)
        expr = '+'.join(f'p{k}' for k in ms)
        if p['ask'] == 'year-total':
            return Scheme(n=N, rate=rate, S=S, debts=debts).solve(expr)[0]
        sol = Scheme(n=N, rate=rate, S=S, debts=debts, equations=[f'{expr} = {p["total"]}']).solve('r' if p['ask'] == 'r' else 'S')[0]
        return sol if p['ask'] == 'r' else sol / 1000

    def shown(self, p, v):
        if p['ask'] == 'year-total':
            return _rub(v, 'тыс. рублей')
        if p['ask'] == 'A':
            return dec(v)
        return dec(v)

    def build(self, p):
        N, y0, year = p['N'], p['y0'], p['year']
        end = y0 + N // 12
        S_txt = f'{dec(p["S"] / 1000)} млн рублей' if p['S'] is not None else '$A$ млн рублей'
        r_txt = f'{dec(p["r"])} %' if p['r'] is not None else '$r$ процентов'
        head = (f'15 декабря {y0} года планируется взять кредит в банке на сумму {S_txt} на {N} месяцев. Условия его возврата таковы:\n\n'
                f'— 1-го числа каждого месяца долг возрастает на {r_txt} по сравнению с концом предыдущего месяца;\n\n'
                f'— со 2-го по 14-е число каждого месяца необходимо одним платежом оплатить часть долга;\n\n'
                f'— 15-го числа каждого месяца долг должен быть на одну и ту же величину меньше долга на 15-е число предыдущего месяца;\n\n'
                f'— к 15 декабря {end} года кредит должен быть полностью погашен.\n\n')
        if p['ask'] == 'year-total':
            cond = head + f'Чему равна общая сумма платежей в {year} году?'
        else:
            cond = head + f'Чему равно ${p["ask"]}$, если общая сумма платежей в {year} году составит {_rub(p["total"], "тыс. рублей")}?'
        ms = self._months(p)
        a, b = ms[0], ms[-1]
        sol = (f'Пусть сумма кредита $S$ (в тыс. рублей). Долг уменьшается равномерно, каждый месяц на $\\frac{{S}}{{{N}}}$: перед $k$-м платежом '
               f'он равен $S\\cdot\\frac{{{N}-k+1}}{{{N}}}$. Платёж $k$-го месяца — это $\\frac{{S}}{{{N}}}$ плюс проценты на текущий долг: '
               f'$$p_k=\\frac{{S}}{{{N}}}+\\frac{{r}}{{100}}\\cdot S\\cdot\\frac{{{N}-k+1}}{{{N}}}.$$\n\n'
               f'В {year} году вносятся платежи с ${a}$-го по ${b}$-й. Их сумма: $$\\frac{{12S}}{{{N}}}+\\frac{{r}}{{100}}\\cdot\\frac{{S}}{{{N}}}'
               f'\\left({N - a + 1}+{N - a}+\\ldots+{N - b + 1}\\right)=\\frac{{12S}}{{{N}}}+\\frac{{r}}{{100}}\\cdot\\frac{{S}}{{{N}}}\\cdot {sum(N - k + 1 for k in ms)}.$$\n\n')
        v = self.value(p)
        if p['ask'] == 'year-total':
            sol += f'При $S={tex_num(p["S"])}$, $r={tex_num(p["r"])}$ получаем ${tex_num(v)}$ тыс. рублей.'
        elif p['ask'] == 'r':
            sol += f'При $S={tex_num(p["S"])}$ сумма равна ${tex_num(p["total"])}$, откуда $r={tex_num(v)}$.'
        else:
            sol += f'При $r={tex_num(p["r"])}$ сумма равна ${tex_num(p["total"])}$ тыс. рублей, откуда $S={tex_num(v * 1000)}$ тыс. рублей, то есть $A={tex_num(v)}$.'
        return cond, sol

    def sample(self, rng):
        years = rng.choice([2, 3, 4, 5, 6])
        N = 12 * years
        y0 = rng.choice([2026, 2027])
        S = F(rng.choice([6, 9, 12, 18, 24, 27, 36, 48, 60, 72])) * 1000
        rate = F(rng.choice([1, 2, 3]))
        year = y0 + rng.randint(1, years)
        p = {'y0': y0, 'S': S, 'N': N, 'r': rate, 'year': year, 'ask': 'year-total', 'total': None}
        total = self.value(p)
        ask = rng.choice(['year-total', 'r', 'A'])
        if ask == 'r':
            return {**p, 'r': None, 'ask': 'r', 'total': total}
        if ask == 'A':
            return {**p, 'S': None, 'ask': 'A', 'total': total}
        return p


# ---------------------------------------------------------------------------
# 3. Аннуитет: n равных платежей
# ---------------------------------------------------------------------------

class Annuity(Credit):
    topic, code = 'Аннуитетные платежи', '16.annuity'
    patterns = [r'увеличивается на (\d+) ?% по сравнению с концом предыдущего года.*?полностью погашен (\w+) равными платежами.*?'
                r'(?:(?:общая сумма (?:платежей|выплат) после полного погашения кредита (?:должна быть )?на (\d[\d ]*) рубл\w+ больше)|'
                r'(?:банку будет выплачено|общая сумма платежей составит) (\d[\d ]*) рубл)',
                r'(?P<given>кредит в банке на сумму (\d[\d ]*) рублей\..*?увеличивается на (\d+) ?%.*?Сколько рублей (?:составит общая сумма платежей|будет выплачено банку), если известно, что кредит будет полностью погашен (\w+) равными платежами)']

    WORDS = {'двумя': 2, 'тремя': 3, 'четырьмя': 4, 'пятью': 5}

    def parse(self, m, task):
        text = m.group(0)
        if m.groupdict().get('given'):
            return {'S': _n(m.group(2)), 'r': _n(m.group(3)), 'n': self.WORDS[m.group(4)], 'ask': 'total'}
        rate, n = _n(m.group(1)), self.WORDS[m.group(2)]
        ask_total = 'Сколько рублей будет выплачено' in task['condition']
        if m.group(3):
            return {'r': rate, 'n': n, 'over': _n(m.group(3)), 'ask': 'total' if ask_total else 'S'}
        return {'r': rate, 'n': n, 'total': _n(m.group(4)), 'ask': 'S'}

    def _coef(self, p):
        """Платёж x на 1 рубль кредита: x = S·q^n(q−1)/(q^n−1)"""
        q = 1 + p['r'] / 100
        n = p['n']
        return q ** n * (q - 1) / (q ** n - 1)

    def value(self, p):
        c, n = self._coef(p), p['n']
        if 'S' in p and p.get('S') is not None:
            return n * c * p['S']
        if 'over' in p:
            S = p['over'] / (n * c - 1)
            return n * c * S if p['ask'] == 'total' else S
        return p['total'] / (n * c)

    def engine(self, p):
        n = p['n']
        sch = Scheme(n=n, rate=p['r'], S='S', payments=['x'] * n, debts=[None] * n + ['0'],
                     equations=[f'total = {p["S"] * self._coef(p) * n}'] if p.get('S') is not None else
                     ([f'total - S = {p["over"]}'] if 'over' in p else [f'total = {p["total"]}']))
        ask = 'total' if p['ask'] == 'total' else 'S'
        return sch.solve(ask)[0]

    def build(self, p):
        n, rate = p['n'], p['r']
        q = 1 + rate / 100
        head = (f'В июле 2026 года планируется взять кредит в банке на {"сумму " + _rub(p["S"], "рублей") if p.get("S") is not None else "некоторую сумму"}. '
                f'Условия его возврата таковы:\n\n— каждый январь долг увеличивается на {dec(rate)} % по сравнению с концом предыдущего года;\n\n'
                f'— с февраля по июнь каждого года необходимо выплатить одним платежом часть долга.\n\n')
        if p.get('S') is not None:
            cond = head + f'Сколько рублей составит общая сумма платежей, если кредит будет полностью погашен {YEARS_GEN[n]} равными платежами (то есть за {YEARS_WORD[n]} года)?'
        elif 'over' in p:
            what = 'Сколько рублей будет выплачено банку' if p['ask'] == 'total' else 'Сколько рублей планируется взять в банке'
            cond = head + (f'{what}, если известно, что кредит будет полностью погашен {YEARS_GEN[n]} равными платежами (то есть за {YEARS_WORD[n]} года) '
                           f'и общая сумма платежей после полного погашения кредита на {_rub(p["over"], "рублей")} больше суммы, взятой в кредит?')
        else:
            cond = head + (f'Сколько рублей планируется взять в банке, если известно, что кредит будет полностью погашен {YEARS_GEN[n]} равными платежами '
                           f'(то есть за {YEARS_WORD[n]} года) и банку будет выплачено {_rub(p["total"], "рублей")}?')
        cond = cond.replace('за четыре года года', 'за четыре года').replace('за пять года', 'за пять лет')
        qt = tex_num(q)
        chain = '+'.join(f'{qt}^{{{k}}}' if k > 1 else (qt if k == 1 else '1') for k in range(n - 1, -1, -1))
        sol = (f'Пусть кредит $S$ рублей, ежегодный платёж $x$, $q={qt}$. После последнего платежа долг равен нулю: '
               f'$$S\\cdot {qt}^{{{n}}}-x\\left({chain}\\right)=0,\\qquad x=\\frac{{S\\cdot {qt}^{{{n}}}}}{{{chain}}}=S\\cdot {tex_num(self._coef(p))}.$$\n\n'
               f'Всего выплачено ${n}x=S\\cdot {tex_num(n * self._coef(p))}$. ')
        v = self.value(p)
        if p.get('S') is not None:
            sol += f'При $S={tex_num(p["S"])}$ это ${tex_num(v)}$ рублей.'
        elif 'over' in p:
            S = p['over'] / (n * self._coef(p) - 1)
            sol += (f'Переплата $S\\cdot {tex_num(n * self._coef(p) - 1)}={tex_num(p["over"])}$, откуда $S={tex_num(S)}$'
                    + (f', а выплачено ${tex_num(v)}$ рублей.' if p['ask'] == 'total' else '.'))
        else:
            sol += f'$S\\cdot {tex_num(n * self._coef(p))}={tex_num(p["total"])}$, откуда $S={tex_num(v)}$.'
        return cond, sol

    def shown(self, p, v):
        return _rub(v, '')

    def sample(self, rng):
        n = rng.choice([2, 3, 4])
        rate = F(rng.choice([10, 20, 25, 50]))
        q = 1 + rate / 100
        # платёж — целое: S = x·(q^n − 1)/(q^n(q − 1))
        x = rng.choice([10, 20, 25, 50, 100]) * q.denominator ** n * rng.randint(1, 9) * 10
        S = x * (q ** n - 1) / (q ** n * (q - 1))
        if S.denominator != 1:
            return None
        kind = rng.choice(['S', 'over', 'total'])
        if kind == 'S':
            return {'S': S, 'r': rate, 'n': n, 'ask': 'total'}
        if kind == 'over':
            return {'r': rate, 'n': n, 'over': n * x - S, 'ask': rng.choice(['total', 'S'])}
        return {'r': rate, 'n': n, 'total': n * x, 'ask': 'S'}


# ---------------------------------------------------------------------------
# 4. Два года равные платежи, третий — последний
# ---------------------------------------------------------------------------

class TwoEqual(Credit):
    topic, code = 'Кредиты с заданным графиком долга', '16.two-equal'
    patterns = [r'кредит на три года(?: в размере (\d[\d ]*) тыс\. рублей)?\..*?возрастать на (\d+) ?%.*?платежи в 2027 и (?:в )?2028 годах должны быть '
                r'(равными|по (\d[\d ]*(?:,\d+)?) тыс\. рублей).*?(?:платёж в 2029 году (?:составит|будет равен) (\d[\d ]*(?:,\d+)?) тыс\. рублей|'
                r'сумма всех платежей после полного погашения кредита (?:будет )?равна (\d[\d ]*(?:,\d+)?) тыс\. рублей)\.\s*(.*)$']

    def parse(self, m, task):
        q = m.group(7)
        ask = ('p1' if 'платёж 2027' in q else 'p3' if 'платёж 2029' in q else 'S' if 'Какую сумму' in q else 'total')
        return {'S': _n(m.group(1)) if m.group(1) else None, 'r': _n(m.group(2)), 'x': _n(m.group(4)) if m.group(4) else None,
                'p3': _n(m.group(5)) if m.group(5) else None, 'total': _n(m.group(6)) if m.group(6) else None, 'ask': ask}

    def _solve_all(self, p):
        q = 1 + p['r'] / 100
        S, x, p3, total = p['S'], p['x'], p['p3'], p['total']
        Ss, xs = sp.symbols('S x')
        S_ = Ss if S is None else sp.nsimplify(S)
        x_ = xs if x is None else sp.nsimplify(x)
        qq = sp.nsimplify(q)
        D2 = qq * (qq * S_ - x_) - x_
        P3 = qq * D2
        eqs = []
        if p3 is not None:
            eqs.append(sp.Eq(P3, sp.nsimplify(p3)))
        if total is not None:
            eqs.append(sp.Eq(2 * x_ + P3, sp.nsimplify(total)))
        unknowns = [v for v in (Ss, xs) if v in set().union(*[e.free_symbols for e in eqs])]
        sol = sp.solve(eqs, unknowns, dict=True)[0] if eqs and unknowns else {}
        S_v, x_v = S_.subs(sol), x_.subs(sol)
        P3_v = P3.subs(sol)
        return F(str(S_v)), F(str(x_v)), F(str(sp.nsimplify(P3_v)))

    def value(self, p):
        S, x, p3 = self._solve_all(p)
        return {'p1': x * 1000, 'p3': p3 * 1000, 'S': S, 'total': 2 * x + p3}[p['ask']]

    def engine(self, p):
        S, x, p3 = self._solve_all(p)
        sch = Scheme(n=3, rate=p['r'], S=S, payments=[x, x, None], debts=[None, None, None, '0'])
        v = sch.solve('p3')[0]
        return {'p1': x * 1000, 'p3': F(str(v)) * 1000, 'S': S, 'total': 2 * x + F(str(v))}[p['ask']]

    def shown(self, p, v):
        return _rub(v, '') if p['ask'] in ('p1', 'p3') else dec(v)

    def build(self, p):
        S, x, p3 = self._solve_all(p)
        r = p['r']
        q = 1 + r / 100
        head = (f'В июле 2026 года планируется взять кредит на три года{" в размере " + _rub(p["S"], "тыс. рублей") if p["S"] is not None else ""}. '
                f'Условия его возврата таковы:\n\n— каждый январь долг будет возрастать на {dec(r)} % по сравнению с концом предыдущего года;\n\n'
                f'— с февраля по июнь каждого года необходимо выплатить одним платежом часть долга;\n\n'
                f'— платежи в 2027 и 2028 годах должны быть {"равными" if p["x"] is None else "по " + _rub(p["x"], "тыс. рублей")};\n\n'
                f'— к июлю 2029 года долг должен быть выплачен полностью.\n\n')
        known = (f'Известно, что платёж в 2029 году составит {dec(p["p3"])} тыс. рублей. ' if p['p3'] is not None
                 else f'Известно, что сумма всех платежей после полного погашения кредита будет равна {dec(p["total"])} тыс. рублей. ')
        ask = {'p1': 'Сколько рублей составит платёж 2027 года?', 'p3': 'Сколько рублей составит платёж 2029 года?',
               'S': 'Какую сумму планируется взять в кредит?', 'total': 'Найдите сумму всех платежей после полного погашения кредита.'}[p['ask']]
        cond = head + known + ask
        qt = tex_num(q)
        sol = (f'Пусть кредит $S$ тыс. рублей, платежи 2027 и 2028 годов по $x$ тыс. рублей, $q={qt}$. Долг в июле 2027 года $qS-x$, '
               f'в июле 2028 года $q(qS-x)-x$, а платёж 2029 года гасит долг полностью: $$p_3=q\\bigl(q(qS-x)-x\\bigr)={qt}^3S-({qt}^2+{qt})x.$$\n\n')
        sol += f'Из условия получаем $S={tex_num(S)}$, $x={tex_num(x)}$, $p_3={tex_num(p3)}$ (тыс. рублей).'
        return cond, sol

    def sample(self, rng):
        r = F(rng.choice([10, 20, 30]))
        q = 1 + r / 100
        S = F(rng.choice([500, 600, 800, 900, 1000, 1200, 1500]))
        x = F(rng.choice([100, 150, 200, 250, 300, 400, 500]))
        p3 = q * (q * (q * S - x) - x)
        if p3 <= 0:
            return None
        kind = rng.choice(['p1', 'p3', 'S', 'total'])
        if kind == 'p1':
            return {'S': S, 'r': r, 'x': None, 'p3': p3, 'total': None, 'ask': 'p1'}
        if kind == 'p3':
            return {'S': S, 'r': r, 'x': None, 'p3': None, 'total': 2 * x + p3, 'ask': 'p3'}
        if kind == 'S':
            return {'S': None, 'r': r, 'x': x, 'p3': p3, 'total': None, 'ask': 'S'}
        return {'S': S, 'r': r, 'x': None, 'p3': p3, 'total': None, 'ask': 'total'}


# ---------------------------------------------------------------------------
# 5. Дифференцированный по годам: срок по сумме выплат; минимальная ставка по последнему платежу
# ---------------------------------------------------------------------------

class DiffYears(Credit):
    topic, code = 'Дифференцированные платежи', '16.diff-years'
    patterns = [r'на сумму (\d+(?:,\d+)?) млн рублей на некоторый срок \(целое число лет\)\..*?возрастает на (\d+) ?%.*?общая сумма выплат после его полного погашения составит (\d+(?:,\d+)?) млн рублей',
                r'(?P<last>на сумму (\d+) млн рублей на срок (\d+) лет\..*?Найдите наименьшую возможную ставку \$r\$, если известно, что последний платёж будет не менее (\d+(?:,\d+)?) млн рублей)']

    def parse(self, m, task):
        if m.groupdict().get('last'):
            return {'kind': 'min-r', 'S': _n(m.group(2)), 'n': int(m.group(3)), 'last': _n(m.group(4))}
        return {'kind': 'years', 'S': _n(m.group(1)), 'r': _n(m.group(2)), 'total': _n(m.group(3))}

    def value(self, p):
        if p['kind'] == 'years':
            # total = S + r/100 · S(n+1)/2
            return 2 * (p['total'] - p['S']) / (p['S'] * p['r'] / 100) - 1
        # последний платёж: (S/n)(1 + r/100) ≥ last
        return (p['last'] * p['n'] / p['S'] - 1) * 100

    def engine(self, p):
        if p['kind'] == 'years':
            n = int(self.value(p))
            sch = Scheme(n=n, rate=p['r'], S=p['S'], debts=['S'] + [f'S*{n - k}/{n}' for k in range(1, n + 1)])
            total = sch.solve('total')[0]
            return n if abs(float(total) - float(p['total'])) < 1e-9 else -1
        n = p['n']
        sch = Scheme(n=n, rate='r', S=p['S'], debts=['S'] + [f'S*{n - k}/{n}' for k in range(1, n + 1)], equations=[f'p{n} = {p["last"]}'])
        return sch.solve('r')[0]

    def build(self, p):
        if p['kind'] == 'years':
            cond = (f'В июле планируется взять кредит в банке на сумму {dec(p["S"])} млн рублей на некоторый срок (целое число лет). Условия его возврата таковы:\n\n'
                    f'— каждый январь долг возрастает на {dec(p["r"])} % по сравнению с концом предыдущего года;\n\n— с февраля по июнь каждого года необходимо выплатить часть долга;\n\n'
                    f'— в июле каждого года долг должен быть на одну и ту же сумму меньше долга на июль предыдущего года.\n\n'
                    f'На сколько лет планируется взять кредит, если известно, что общая сумма выплат после его полного погашения составит {dec(p["total"])} млн рублей?')
            sol = (f'Пусть срок $n$ лет. Долг каждый год уменьшается на $\\frac{{S}}{{n}}$, по июлям он равен $S,\\ \\frac{{(n-1)S}}{{n}},\\ \\ldots,\\ \\frac{{S}}{{n}}$. '
                   f'Сумма выплат — кредит плюс проценты: $$S+\\frac{{r}}{{100}}\\left(S+\\frac{{(n-1)S}}{{n}}+\\ldots+\\frac{{S}}{{n}}\\right)=S+\\frac{{r}}{{100}}\\cdot\\frac{{S(n+1)}}{{2}}.$$\n\n'
                   f'$${dec(p["S"]).replace(",", "{,}")}+{tex_num(p["r"] / 100)}\\cdot\\frac{{{tex_num(p["S"])}(n+1)}}{{2}}={tex_num(p["total"])},$$ откуда $n={tex_num(self.value(p))}$.')
            return cond, sol
        cond = (f'В июле планируется взять кредит в банке на сумму {dec(p["S"])} млн рублей на срок {p["n"]} лет. Условия возврата таковы:\n\n'
                f'— каждый январь долг возрастает на $r$ % по сравнению с концом предыдущего года;\n\n'
                f'— с февраля по июнь необходимо выплатить часть долга так, чтобы на начало июля каждого года долг уменьшался на одну и ту же сумму по сравнению с предыдущим июлем.\n\n'
                f'Найдите наименьшую возможную ставку $r$, если известно, что последний платёж будет не менее {dec(p["last"])} млн рублей.')
        d = p['S'] / p['n']
        sol = (f'Долг каждый год уменьшается на $\\frac{{{tex_num(p["S"])}}}{{{p["n"]}}}={tex_num(d)}$ млн рублей. Перед последним платежом долг равен ${tex_num(d)}$, '
               f'после начисления процентов — ${tex_num(d)}\\left(1+\\frac{{r}}{{100}}\\right)$; это и есть последний платёж. '
               f'$${tex_num(d)}\\left(1+\\frac{{r}}{{100}}\\right)\\ge {tex_num(p["last"])}\\ \\Rightarrow\\ r\\ge {tex_num(self.value(p))}.$$')
        return cond, sol

    def sample(self, rng):
        if rng.random() < 0.5:
            S = F(rng.choice([2, 4, 5, 6, 8, 10, 12]))
            r = F(rng.choice([10, 20, 25, 30]))
            n = rng.randint(3, 12)
            return {'kind': 'years', 'S': S, 'r': r, 'total': S + r / 100 * S * (n + 1) / 2}
        n = rng.choice([5, 8, 10])
        S = F(rng.choice([5, 6, 7, 8, 10, 12]))
        r = F(rng.choice([5, 10, 12, 15, 17, 20, 25]))
        return {'kind': 'min-r', 'S': S, 'n': n, 'last': S / n * (1 + r / 100)}


# ---------------------------------------------------------------------------
# 6. Проценты три года, затем два равных платежа
# ---------------------------------------------------------------------------

class InterestOnly(Credit):
    topic, code = 'Аннуитетные платежи', '16.interest-only'
    patterns = [r'кредит на пять лет в размере (\d+(?:,\d+)?) (млн|тыс)\.? рублей\..*?возрастает на (?:\$r\$ процентов|(\d+) ?%).*?в июле 2027, 2028 и 2029 годов долг остаётся равным.*?'
                r'(?:Найдите \$r\$, если известно, что долг будет выплачен полностью и общий размер выплат составит (\d+(?:,\d+)?) млн рублей|'
                r'Найдите общую сумму (?:выплат|платежей) за пять лет|На сколько рублей последняя выплата будет больше первой)',
                r'(?P<S>кредит в банке на пять лет в размере \$S\$ тыс\. рублей\..*?возрастает на (\d+) ?%.*?выплаты в 2030 и 2031 годах равны по (\d+) тыс\. рублей.*?Найдите общую сумму выплат)']

    def parse(self, m, task):
        text = task['condition']
        if m.groupdict().get('S'):
            return {'ask': 'total-from-x', 'r': _n(m.group(2)), 'x': _n(m.group(3)), 'unit': 'тыс'}
        unit = m.group(2)
        S = _n(m.group(1))
        if m.group(4):
            return {'ask': 'r', 'S': S, 'total': _n(m.group(4)), 'unit': unit}
        if 'На сколько рублей' in text:
            return {'ask': 'diff', 'S': S, 'r': _n(m.group(3)), 'unit': unit}
        return {'ask': 'total', 'S': S, 'r': _n(m.group(3)), 'unit': unit}

    @staticmethod
    def _x(S, q):
        # D после 3 лет = S; два равных платежа: S q² − x q − x = 0
        return S * q * q / (q + 1)

    def value(self, p):
        if p['ask'] == 'r':
            rr = sp.symbols('rr', positive=True)
            q = 1 + rr / 100
            S, total = sp.nsimplify(p['S']), sp.nsimplify(p['total'])
            sol = [v for v in sp.solve(sp.Eq(3 * S * (q - 1) + 2 * S * q * q / (q + 1), total), rr) if v.is_real and v > 0]
            return F(str(sp.nsimplify(sol[0])))
        if p['ask'] == 'total-from-x':
            q = 1 + p['r'] / 100
            S = p['x'] * (q + 1) / (q * q)
            return 3 * S * (q - 1) + 2 * p['x']
        q = 1 + p['r'] / 100
        S = p['S']
        x = self._x(S, q)
        if p['ask'] == 'total':
            return 3 * S * (q - 1) + 2 * x
        return (x - S * (q - 1)) * _mult(p['unit'])

    def engine(self, p):
        if p['ask'] == 'r':
            sch = Scheme(n=5, rate='r', S=p['S'], debts=['S', 'S', 'S', 'S', None, '0'], payments=[None, None, None, 'x', 'x'],
                         equations=[f'total = {p["total"]}'])
            sol = sch.solve('r')
            return sol[0]
        return None

    def shown(self, p, v):
        return _rub(v, '') if p['ask'] == 'diff' else dec(v)

    def build(self, p):
        unit = {'млн': 'млн рублей', 'тыс': 'тыс. рублей'}[p['unit']]
        if p['ask'] == 'total-from-x':
            cond = (f'В июле 2026 года планируется взять кредит в банке на пять лет в размере $S$ тыс. рублей. Условия его возврата таковы:\n\n'
                    f'— каждый январь долг возрастает на {dec(p["r"])} % по сравнению с концом предыдущего года;\n\n— с февраля по июнь каждого года необходимо выплатить одним платежом часть долга;\n\n'
                    f'— в июле 2027, 2028 и 2029 годов долг остаётся равным $S$ тыс. рублей;\n\n— выплаты в 2030 и 2031 годах равны по {dec(p["x"])} тыс. рублей;\n\n'
                    f'— к июлю 2031 года долг будет выплачен полностью.\n\nНайдите общую сумму выплат за пять лет.')
        else:
            rtxt = '$r$ процентов' if p['ask'] == 'r' else f'{dec(p["r"])} %'
            cond = (f'В июле 2026 года планируется взять кредит на пять лет в размере {dec(p["S"])} {unit}. Условия его возврата таковы:\n\n'
                    f'— каждый январь долг возрастает на {rtxt} по сравнению с концом предыдущего года;\n\n— с февраля по июнь каждого года необходимо выплатить часть долга;\n\n'
                    f'— в июле 2027, 2028 и 2029 годов долг остаётся равным {dec(p["S"])} {unit};\n\n— выплаты в 2030 и 2031 годах равны;\n\n'
                    f'— к июлю 2031 года долг будет выплачен полностью.\n\n')
            cond += {'r': f'Найдите $r$, если известно, что общий размер выплат составит {dec(p.get("total", 0))} {unit}.',
                     'total': 'Найдите общую сумму выплат за пять лет.', 'diff': 'На сколько рублей последняя выплата будет больше первой?'}[p['ask']]
        sol = ('Пусть кредит $S$, $q=1+\\frac{r}{100}$. Первые три года долг не меняется, значит, платёж каждого из них — только проценты: $S(q-1)$. '
               'Затем два равных платежа $x$ гасят долг: $$q(qS-x)-x=0,\\qquad x=\\frac{q^2S}{q+1}.$$ Сумма выплат: $$3S(q-1)+2x.$$\n\n')
        v = self.value(p)
        if p['ask'] == 'r':
            sol += f'Подставляя $S={tex_num(p["S"])}$ и сумму ${tex_num(p["total"])}$, получаем уравнение относительно $q$, откуда $r={tex_num(v)}$.'
        elif p['ask'] == 'total':
            q = 1 + p['r'] / 100
            sol += f'При $S={tex_num(p["S"])}$, $q={tex_num(q)}$: $x={tex_num(self._x(p["S"], q))}$, сумма ${tex_num(v)}$ {unit}.'
        elif p['ask'] == 'total-from-x':
            q = 1 + p['r'] / 100
            S = p['x'] * (q + 1) / (q * q)
            sol += f'Из $x={tex_num(p["x"])}$: $S=\\frac{{x(q+1)}}{{q^2}}={tex_num(S)}$, сумма ${tex_num(v)}$ тыс. рублей.'
        else:
            q = 1 + p['r'] / 100
            x = self._x(p['S'], q)
            sol += f'Первая выплата $S(q-1)={tex_num(p["S"] * (q - 1))}$, последняя $x={tex_num(x)}$ ({unit}); разность ${tex_num(v)}$ рублей.'
        return cond, sol

    def sample(self, rng):
        r = F(rng.choice([10, 20, 25, 30]))
        q = 1 + r / 100
        S = F(rng.choice([1050, 1260, 2100, 2520, 4200, 6300])) if q == F(11, 10) else F(rng.randint(2, 30) * 110)
        x = self._x(S, q)
        if x.denominator != 1:
            return None
        ask = rng.choice(['total', 'diff', 'total-from-x'])
        if ask == 'total-from-x':
            return {'ask': ask, 'r': r, 'x': x, 'unit': 'тыс'}
        return {'ask': ask, 'S': S, 'r': r, 'unit': 'тыс'}


# ---------------------------------------------------------------------------
# 7. Таблица долга в долях S: наибольшее целое S, при котором каждая выплата меньше M
# ---------------------------------------------------------------------------

class TableMaxS(Credit):
    topic, code = 'Кредиты с заданным графиком долга', '16.table'
    patterns = [r'увеличивается на (\d+) ?% по сравнению с концом предыдущего года.*?\| Долг \(в млн рублей\) \|(.+?)\|\s*¶?\s*Найдите наибольшее значение \$S\$, при котором каждая из выплат будет меньше (\d+) млн рублей']

    def parse(self, m, task):
        cells = [c.strip().strip('$') for c in m.group(2).split('|')]
        fr = []
        for c in cells:
            if c in ('S',):
                fr.append(F(1))
            elif c == '0':
                fr.append(F(0))
            else:
                fr.append(_n(c.replace('{,}', ',').rstrip('S')))
        return {'r': _n(m.group(1)), 'fr': fr, 'M': _n(m.group(3))}

    def _coefs(self, p):
        q = 1 + p['r'] / 100
        return [q * a - b for a, b in zip(p['fr'], p['fr'][1:])]

    def value(self, p):
        c = max(self._coefs(p))
        bound = p['M'] / c
        return F(math.ceil(bound) - 1)

    def build(self, p):
        q = 1 + p['r'] / 100
        n = len(p['fr']) - 1
        cells = ' | '.join(('$S$' if a == 1 else '0' if a == 0 else f'${tex_num(a)}S$') for a in p['fr'])
        months = ' | '.join(f'Июль {2026 + i}' for i in range(n + 1))
        cond = (f'В июле 2026 года планируется взять кредит в банке на {YEARS_WORD.get(n, n)} года в размере $S$ млн рублей, где $S$ — **целое** число. '
                f'Условия его возврата таковы:\n\n— каждый январь долг увеличивается на {dec(p["r"])} % по сравнению с концом предыдущего года;\n\n'
                f'— с февраля по июнь каждого года необходимо выплатить одним платежом часть долга;\n\n'
                f'— в июле каждого года долг должен составлять часть кредита в соответствии со следующей таблицей.\n\n'
                f'| Месяц и год | {months} |\n|' + ' --- |' * (n + 2) + f'\n| Долг (в млн рублей) | {cells} |\n\n'
                f'Найдите наибольшее значение $S$, при котором каждая из выплат будет меньше {dec(p["M"])} млн рублей.')
        cs = self._coefs(p)
        lines = '; '.join(f'$p_{i + 1}={tex_num(q)}\\cdot {tex_num(a)}S-{tex_num(b)}S={tex_num(c)}S$'.replace('\\cdot 1S', 'S').replace('-0S', '')
                          for i, (a, b, c) in enumerate(zip(p['fr'], p['fr'][1:], cs)))
        cmax = max(cs)
        sol = (f'Платёж года — долг после начисления процентов минус новый долг: {lines}.\n\n'
               f'Наибольший из платежей — ${tex_num(cmax)}S$. Все выплаты меньше {dec(p["M"])} тогда и только тогда, когда '
               f'$${tex_num(cmax)}S<{tex_num(p["M"])},\\qquad S<{tex_num(p["M"] / cmax)}.$$ Наибольшее целое $S={tex_num(self.value(p))}$.')
        return cond, sol

    def sample(self, rng):
        r = F(rng.choice([10, 15, 20, 25, 30]))
        fr = [F(1), F(rng.choice([6, 7, 8]), 10), F(rng.choice([2, 3, 4, 5]), 10), F(0)]
        M = F(rng.choice([3, 4, 5, 6, 7, 8]))
        p = {'r': r, 'fr': fr, 'M': M}
        return p if (M / max(self._coefs(p))).denominator != 1 else None


# ---------------------------------------------------------------------------
# 8. Ценные бумаги t² и банк: в конце какого года продать
# ---------------------------------------------------------------------------

class Securities(Credit):
    topic, code = 'Оптимальный выбор', '16.securities'
    patterns = [r'стоят \$t\^2\$ тыс\. рублей в конце года \$t\$.*?увеличиваться на (\d+) ?%\. В конце какого года пенсионному фонду следует продать ценные бумаги, чтобы в конце (\w+(?: \w+)?) года']

    YEAR = {'двадцать пятого': 25, 'двадцатого': 20, 'тридцатого': 30}

    def parse(self, m, task):
        word = re.search(r'чтобы в конце (\w+(?: \w+)?) года', task['condition']).group(1)
        return {'r': _n(m.group(1)), 'T': self.YEAR.get(word, 25)}

    def value(self, p):
        q = 1 + p['r'] / 100
        best = max(range(1, p['T'] + 1), key=lambda t: F(t * t) * q ** (p['T'] - t))
        return F(best)

    def build(self, p):
        q = 1 + p['r'] / 100
        t = int(self.value(p))
        cond = (f'Пенсионный фонд владеет ценными бумагами, которые стоят $t^2$ тыс. рублей в конце года $t$ ($t=1;2;\\ldots$). В конце любого года '
                f'пенсионный фонд может продать ценные бумаги и положить деньги на счёт в банке, при этом в конце каждого следующего года сумма на счёте '
                f'будет увеличиваться на {dec(p["r"])}%. В конце какого года пенсионному фонду следует продать ценные бумаги, чтобы в конце {p["T"]}-го '
                f'года сумма на его счёте была наибольшей?')
        sol = (f'Если продать в конце года $t$, к концу года ${p["T"]}$ на счёте будет $t^2\\cdot {tex_num(q)}^{{{p["T"]}-t}}$. Сравним соседние годы: '
               f'продавать на год позже выгодно, пока $$\\frac{{(t+1)^2}}{{t^2}}>{tex_num(q)},\\qquad \\left(1+\\frac{{1}}{{t}}\\right)^2>{tex_num(q)}.$$ '
               f'Левая часть убывает с ростом $t$; неравенство верно при $t\\le {t - 1}$ и неверно при $t={t}$ '
               f'($\\left(1+\\frac{{1}}{{{t}}}\\right)^2={tex_num(F(t + 1, t) ** 2)}<{tex_num(q)}$). Значит, сумма наибольшая при продаже в конце {t}-го года.')
        return cond, sol

    def sample(self, rng):
        return {'r': F(rng.choice([10, 20, 25, 30, 40, 50])), 'T': rng.choice([20, 25, 30])}

    def nice(self, answer):
        v = F(answer['accepted'][0])
        return 1 < v


class GenericScheme(Credit):
    """
    Задание ФИПИ, переписанное вручную в схему кредита (data/fipi/manual.json): периоды, остатки/платежи, уравнения.
    Решение пишется по схеме: остатки, платежи как «долг с процентами минус новый долг», уравнение, ответ.
    """
    topic, code = 'Кредиты', '16.scheme'
    variants = False

    def match(self, task):
        return None

    def _scheme(self, p):
        return Scheme(n=p['n'], rate=p.get('rate', 'r'), S=p.get('S', 'S'), debts=p.get('debts') or [],
                      payments=p.get('payments') or [], equations=p.get('equations', []))

    def value(self, p):
        v = self._scheme(p).solve(p['ask'])[0]
        return F(str(sp.nsimplify(v))) * F(str(p.get('scale', 1)))

    def shown(self, p, v):
        return _rub(v, '') if p.get('scale', 1) != 1 or v >= 10000 else dec(v)

    def build(self, p):
        sch = self._scheme(p)
        debts, pays, q = sch.build()
        val, sol, _, _ = sch.solve(p['ask'])
        unit = p.get('unit', 'тыс. рублей')
        rate = p.get('rate', 'r')
        qt = f'1+\\frac{{r}}{{100}}' if rate == 'r' else tex_num(1 + F(str(rate)) / 100)
        lines = []
        n = p['n']
        show = list(range(1, n + 1)) if n <= 12 else [1, 2, n - 1, n]
        for k in show:
            lines.append(f'$p_{{{k}}}={sp.latex(sp.nsimplify(pays[k - 1]))}$')
        known = ', '.join(f'${sp.latex(sp.Symbol(str(s)))}={sp.latex(v)}$' for s, v in sol.items())
        txt = (f'Пусть $q={qt}$. В каждом периоде долг сначала умножается на $q$, затем вносится платёж $p_k$; остаток $D_k=qD_{{k-1}}-p_k$, '
               f'то есть $p_k=qD_{{k-1}}-D_k$. По условию остатки (в {unit}): '
               + ', '.join(f'$D_{{{k}}}={sp.latex(sp.nsimplify(d))}$' for k, d in enumerate(debts) if n <= 12 or k in (0, 1, n - 1, n)) + '.\n\n'
               f'Платежи: ' + '; '.join(lines) + ('; …' if n > 12 else '') + '.\n\n')
        if p.get('equations'):
            txt += 'Условие: ' + '; '.join(f'${e.replace("total", "p_1+\\ldots+p_{" + str(n) + "}")}$' for e in p['equations']) + '. '
            txt += f'Решая, получаем {known}. ' if known else ''
        txt += f'Искомая величина: ${sp.latex(sp.nsimplify(val))}$' + (f' {unit}' if p.get('scale', 1) == 1 else '') + '.'
        return '', txt


TEMPLATES = [PercentDecrease(), MonthlyEqual(), Annuity(), TwoEqual(), DiffYears(), InterestOnly(), TableMaxS(), Securities(), GenericScheme()]
EXTRA = []
