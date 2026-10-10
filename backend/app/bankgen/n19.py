"""
№ 19. Числа и их свойства (задачи с пунктами а, б, в).

check проверяет ответ перебором (там, где пространство конечно) и подставляет приведённые в решении
примеры в условие задачи. Восемь задач этого типа ФИПИ относит к № 18 по КЭС — здесь они тоже.
"""
import itertools
from collections import deque
from fractions import Fraction

from app.bankgen.part2 import Answer, Solved

TOPIC = 'Числа и их свойства'


class Puzzle(Solved):
    number, topic, difficulty = 19, TOPIC, 3

    def answer(self, p):
        return Answer(self.ANS, 0)

    def check(self, p):
        return bool(self.verify_all(p))

    def condition(self, p):
        return ''


def ans(a, b, c) -> str:
    return f'а) {a}; б) {b}; в) {c}'


# ---------------------------------------------------------------------------

class DigitTensOperation(Puzzle):
    fipi = {'30D64C': {}}
    ANS = ans('да', 'нет', '$\\frac{283}{190}$')

    def verify_all(self, p):
        res = {100 * a + 10 * b + c: 100 * a + 20 * b + c + 3 for a in range(1, 10) for b in range(10) for c in range(10)}
        best = max(Fraction(v, k) for k, v in res.items())
        return 224 in res.values() and 314 not in res.values() and best == Fraction(283, 190)

    def solution(self, p):
        return (
            'Пусть исходное число $\\overline{abc}=100a+10b+c$. Результат операции $100a+20b+c+3$.\n\n'
            'а) $100a+20b+c=221$: $a=2$, $b=1$, $c=1$. Число $211$: $211+10+3=224$. Ответ: да.\n\n'
            'б) $100a+20b+c=311$. Так как $20b+c\\le189$, $a=2$ или $a=3$. При $a=3$: $20b+c=11$ — невозможно ($b=0$ даёт $c=11$). При $a=2$: '
            '$20b+c=111$, $20b\\in[102;111]$ — нет кратного 20. Ответ: нет.\n\n'
            'в) Отношение $\\frac{100a+20b+c+3}{100a+10b+c}=1+\\frac{10b+3}{100a+10b+c}$. Дробь больше при $a=1$, $c=0$: $\\frac{10b+3}{100+10b}$ '
            'возрастает по $b$ (её числитель растёт быстрее в относительном смысле: $10(100+10b)-10(10b+3)=970>0$), поэтому максимум при $b=9$: '
            'число $190$, результат $283$, отношение $\\frac{283}{190}$.')


class SchoolsAverages(Puzzle):
    """Две школы, ученик переходит из первой во вторую"""
    VARIANTS = {
        'F58FFD': dict(total=51, k=Fraction(11, 10), ans=ans('нет', 'нет', '3'), first=2, second=1),
        'E983D6': dict(total=9, k=Fraction(9, 10), ans=ans('да', 'нет', '5'), first=Fraction(1, 10), second=7),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def _search(self, total, k, A2_max=60, A1_max=400):
        """Все (n1, A1, n2, A2, x): средние меняются в k раз, x — балл перешедшего"""
        out = []
        for n1 in range(2, total - 1):
            n2 = total - n1
            for A1 in range(1, A1_max):
                x = n1 * A1 - k * A1 * (n1 - 1)
                if x.denominator != 1 or x < 1 or n1 * A1 - x < n1 - 1:
                    continue
                for A2 in range(1, A2_max):
                    if (n2 * A2 + x) == k * A2 * (n2 + 1):
                        out.append((n1, A1, n2, A2, int(x)))
        return out

    def verify_all(self, p):
        d = self.VARIANTS[p['kind']]
        total, k = d['total'], d['k']
        sols = self._search(total, k)
        # а) изменение первой школы в 2 раза (F58FFD) или уменьшение в 10 раз (E983D6)
        a_possible = False
        for n1 in range(2, total - 1):
            for A1 in range(1, 400):
                x = n1 * A1 - d['first'] * A1 * (n1 - 1)
                if x.denominator == 1 and x >= 1 and n1 * A1 - x >= n1 - 1:
                    a_possible = True
        b_possible = any(s[3] == d['second'] for s in sols)
        c_min = min(s[3] for s in sols)
        exp = {'F58FFD': (False, False, 3), 'E983D6': (True, False, 5)}[p['kind']]
        return (a_possible, b_possible, c_min) == exp

    def solution(self, p):
        if p['kind'] == 'F58FFD':
            return (
                'Пусть в школе № 1 было $n_1$ учащихся со средним баллом $A_1$, в школе № 2 — $n_2$ со средним $A_2$, $n_1+n_2=51$, перешёл '
                'учащийся с баллом $x$.\n\n'
                'а) Если средний балл школы № 1 вырос вдвое: $n_1A_1-x=2A_1(n_1-1)$, $x=A_1(2-n_1)\\le0$ при $n_1\\ge2$ — противоречие. Ответ: нет.\n\n'
                'б) Оба средних выросли на 10%: $n_1A_1-x=1{,}1A_1(n_1-1)$, то есть $x=\\frac{A_1(11-n_1)}{10}$, и $n_2A_2+x=1{,}1A_2(n_2+1)$, '
                'то есть $x=\\frac{A_2(n_2+11)}{10}=\\frac{A_2(62-n_1)}{10}$. В частности, $n_1<11$. Если $A_2=1$, то $x=\\frac{62-n_1}{10}$ — целое '
                'только при $n_1=2$, $x=6$, и тогда $A_1=\\frac{10x}{11-n_1}=\\frac{60}{9}$ — не целое. Ответ: нет.\n\n'
                'в) Нужно $A_2(62-n_1)=A_1(11-n_1)$ и $10\\mid A_2(62-n_1)$ при $2\\le n_1\\le10$. $A_2=1$ — см. п. б. $A_2=2$: $62-n_1$ кратно 5, '
                '$n_1\\in\\{2;7\\}$, $A_1=\\frac{120}{9}$ или $\\frac{110}{4}$ — не целые. $A_2=3$: $n_1=2$, $x=18$, $A_1=20$. Пример: в школе № 1 '
                'двое с баллами 18 и 22 (средний 20), в школе № 2 — 49 учащихся по 3 балла. После перехода: в школе № 1 средний 22 (вырос на 10%), '
                'в школе № 2 $\\frac{147+18}{50}=3{,}3$ (вырос на 10%). Ответ: 3.')
        return (
            'Пусть $n_1+n_2=9$, средние $A_1$, $A_2$, перешёл учащийся с баллом $x$.\n\n'
            'а) Средний балл школы № 1 уменьшился в 10 раз: $n_1A_1-x=\\frac{A_1}{10}(n_1-1)$. Пример: $n_1=2$, баллы 19 и 1 (средний 10); после '
            'перехода учащегося с 19 баллами остался один с 1 баллом — средний уменьшился в 10 раз. Ответ: да.\n\n'
            'б) Оба средних уменьшились на 10%: $x=\\frac{A_1(n_1+9)}{10}$ и $n_2A_2+x=0{,}9A_2(n_2+1)$, $x=\\frac{A_2(9-n_2)}{10}$. При $A_2=7$: '
            '$x=\\frac{7(9-n_2)}{10}$ — целое только при $n_2=9$, но тогда $x=0$, а $n_2\\le7$. Ответ: нет.\n\n'
            'в) Ищем наименьшее $A_2$ с целыми $x=\\frac{A_2(9-n_2)}{10}$ и $A_1=\\frac{A_2(9-n_2)}{18-n_2}$ при $2\\le n_2\\le7$. При $A_2\\le4$ '
            'условие $10\\mid A_2(9-n_2)$ выполняется только для $n_2=4$, $A_2=2$ или $4$, но тогда $A_1=\\frac{5A_2}{14}$ — не целое. '
            '$A_2=5$, $n_2=3$: $x=3$, $A_1=2$, $n_1=6$. Пример: в школе № 1 шесть учащихся с баллами 3, 2, 2, 2, 2, 1 (средний 2), в школе № 2 три '
            'по 5 баллов. После перехода: $\\frac{9}{5}=1{,}8$ и $\\frac{18}{4}=4{,}5$ — оба средних уменьшились на 10%. Ответ: 5.')


class SchoolsFixedAverage(Puzzle):
    VARIANTS = {
        'D6152F': dict(ans=ans('4', '102', '96')),
        '40BED3': dict(ans=ans('6', '89', '19')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def verify_all(self, p):
        if p['kind'] == 'D6152F':
            # школа 2: средний 42, оба средних уменьшились на 10%
            n2s = [n2 for n2 in range(2, 50) if (Fraction(9, 10) * 42 * (n2 + 1) - 42 * n2) > 0
                   and (Fraction(9, 10) * 42 * (n2 + 1) - 42 * n2).denominator == 1]
            if n2s != [4]:
                return False
            x = 21
            best_n1 = max(n1 for n1 in range(2, 400) for A1 in range(1, 200)
                          if n1 * A1 - x == Fraction(9, 10) * A1 * (n1 - 1) and n1 * A1 - x >= n1 - 1 and x <= n1 * A1 - (n1 - 1))
            # б) четверо в школе 2 со средним 42, каждый > 21
            b = 4 * 42 - 3 * 22
            return best_n1 == 96 and b == 102
        n1s = [n1 for n1 in range(2, 50) if (18 * n1 - Fraction(198, 10) * (n1 - 1)) >= 1
               and (18 * n1 - Fraction(198, 10) * (n1 - 1)).denominator == 1]
        if n1s != [6]:
            return False
        x = 9
        # б) 6 разных баллов, сумма 108, среди них 9
        best = max(m for m in range(1, 109) if m != 9 and 108 - 9 - m >= 1 + 2 + 3 + 4 and
                   len({1, 2, 3, 4, 9, m}) == 6)
        n2 = min(n2 for n2 in range(11, 500) for A2 in range(1, 100) if n2 * A2 + x == Fraction(11, 10) * A2 * (n2 + 1))
        return best == 89 and n2 == 19

    def solution(self, p):
        if p['kind'] == 'D6152F':
            return (
                'Пусть в школе № 1 $n_1$ учащихся со средним $A_1$, в школе № 2 — $n_2$ со средним 42, перешёл учащийся с баллом $x$. '
                'Условия: $\\frac{n_1A_1-x}{n_1-1}=0{,}9A_1$ и $\\frac{42n_2+x}{n_2+1}=37{,}8$.\n\n'
                'а) Из второго: $x=37{,}8-4{,}2n_2=\\frac{21(9-n_2)}{5}$. Это натуральное число только при $n_2=4$ ($x=21$). Ответ: 4.\n\n'
                'б) В школе № 2 четыре учащихся с суммой $4\\cdot42=168$, каждый набрал больше 21, то есть не меньше 22. Один может набрать не '
                'больше $168-3\\cdot22=102$; пример: 102, 22, 22, 22 (из первого условия подходит, например, $n_1=5$, $A_1=15$: $x=\\frac{A_1(n_1+9)}{10}=21$). '
                'Ответ: 102.\n\n'
                'в) Из первого условия $x=\\frac{A_1(n_1+9)}{10}=21$, $A_1(n_1+9)=210$. При $n_1=201$ получаем $A_1=1$ — все баллы равны 1, но '
                '$x=21$ — противоречие. Следующий делитель: $n_1+9=105$, $n_1=96$, $A_1=2$. Пример: учащийся с 21 баллом, 76 учащихся по 2 балла и '
                '19 — по 1 баллу: сумма $21+152+19=192=96\\cdot2$; после перехода $\\frac{171}{95}=1{,}8$. Ответ: 96.')
        return (
            'Пусть в школе № 1 $n_1$ учащихся (средний 18), в школе № 2 — $n_2$ (средний $A_2$), перешёл учащийся с баллом $x$. '
            'Условия: $\\frac{18n_1-x}{n_1-1}=19{,}8$ и $\\frac{A_2n_2+x}{n_2+1}=1{,}1A_2$.\n\n'
            'а) $x=19{,}8-1{,}8n_1=\\frac{9(11-n_1)}{5}$ — натуральное только при $n_1=6$ ($x=9$). Ответ: 6.\n\n'
            'б) В школе № 1 шесть разных баллов с суммой 108, один из них 9. Остальные четыре (кроме наибольшего) не меньше $1+2+3+4=10$, '
            'поэтому наибольший не больше $108-9-10=89$; пример: 1, 2, 3, 4, 9, 89. Ответ: 89.\n\n'
            'в) Из второго условия $x=\\frac{A_2(n_2+11)}{10}=9$, $A_2(n_2+11)=90$. При $n_2>10$ делитель $n_2+11>21$: 30, 45 или 90; наименьшее '
            '$n_2=19$ ($A_2=3$). Пример: 19 учащихся по 3 балла; после перехода $\\frac{57+9}{20}=3{,}3$. Ответ: 19.')


class EndingDigits(Puzzle):
    """30 различных чисел с заданными последними цифрами и заданной суммой"""
    VARIANTS = {
        '7B10F3': dict(ans=ans('нет', 'нет', '11')),
        'A8EFB6': dict(ans=ans('да', 'нет', '4')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def verify_all(self, p):
        if p['kind'] == '7B10F3':
            def minsum(k):     # k чисел на 6, 30 − k на 2
                return sum(6 + 10 * i for i in range(k)) + sum(2 + 10 * i for i in range(30 - k))
            feasible = [k for k in range(31) if (6 * k + 2 * (30 - k)) % 10 == 4 and minsum(k) <= 2454]
            return min(feasible) == 11 and 15 not in feasible and 1 not in feasible
        def minsum7(k):        # k чисел на 7, 30 − k чётных
            return sum(7 + 10 * i for i in range(k)) + sum(2 * (i + 1) for i in range(30 - k))
        feasible = [k for k in range(31) if k % 2 == 0 and minsum7(k) <= 810]
        return min(feasible) == 4 and 6 in feasible and 2 not in feasible

    def solution(self, p):
        if p['kind'] == '7B10F3':
            return (
                'а) Если чисел на 2 и на 6 по 15, последняя цифра суммы — последняя цифра $15\\cdot2+15\\cdot6=120$, то есть 0, а сумма 2454 '
                'оканчивается на 4. Ответ: нет.\n\n'
                'б) Тогда 29 различных чисел оканчиваются на 2, их сумма не меньше $2+12+\\ldots+282=29\\cdot2+10\\cdot\\frac{28\\cdot29}{2}=4118>2454$. '
                'Ответ: нет.\n\n'
                'в) Пусть $k$ чисел оканчиваются на 6. Последняя цифра суммы — последняя цифра $6k+2(30-k)=4k+60$, она равна 4, откуда $k\\equiv1\\pmod5$. '
                'Наименьшая возможная сумма при данном $k$: $\\bigl(6+16+\\ldots\\bigr)+\\bigl(2+12+\\ldots\\bigr)=6k+5k(k-1)+2(30-k)+5(30-k)(29-k)$. '
                'При $k=1$ она равна 4124, при $k=6$ — 2994, обе больше 2454. При $k=11$ — 2364: числа $6, 16, \\ldots, 106$ и $2, 12, \\ldots, 172, 272$ '
                '(последнее увеличено на 90) дают сумму 2454. Ответ: 11.')
        return (
            'а) Пример: чётные $2, 4, \\ldots, 46, 66$ (24 числа) и $7, 17, 27, 37, 47, 57$: сумма $600-48+66+192=810$. Ответ: да.\n\n'
            'б) Тогда 28 различных чётных чисел, их сумма не меньше $2+4+\\ldots+56=812>810$. Ответ: нет.\n\n'
            'в) Пусть $k$ чисел оканчиваются на 7. Сумма чётна, поэтому $k$ чётно. При $k=0$ и $k=2$ наименьшие суммы $2+\\ldots+60=930$ и '
            '$812+24=836$ больше 810. При $k=4$: $2+4+\\ldots+52=702$ и $7+17+27+37=88$, сумма 790; увеличив наибольшее чётное число 52 до 72, '
            'получаем 810. Ответ: 4.')


class StonesBoxes(Puzzle):
    VARIANTS = {
        '7CA5F3': dict(ans=ans('да', 'нет', '198')),
        '8381FC': dict(ans=ans('да', 'нет', '303')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def verify_all(self, p):
        if p['kind'] == '7CA5F3':
            start = (97, 104)
            seen = {start}
            q = deque([start])
            while q:
                a, b = q.popleft()
                c = 201 - a - b
                for na, nb in ((a + 2, b - 1), (a - 1, b + 2), (a - 1, b - 1)):
                    nc = 201 - na - nb
                    if min(na, nb, nc) >= 0 and (na, nb) not in seen:
                        seen.add((na, nb))
                        q.append((na, nb))
            best = max(201 - a - b for a, b in seen if a == 1)
            return (97, 89) in seen and (0, 0) not in seen and best == 198
        # 8381FC: проверяем инвариант и предъявленную последовательность ходов
        state = [101, 102, 103, 0]

        def move(s, into):
            s = s[:]
            for i in range(4):
                s[i] += 3 if i == into else -1
            assert min(s) >= 0
            return s
        s = state
        for into in (3, 3, 1, 2):
            s = move(s, into)
        ok_a = s == [97, 102, 103, 4]
        s = state
        for _ in range(25):
            s = move(s, 3)
            for _ in range(3):
                s = move(s, 0)
        s = move(move(s, 3), 0)
        ok_c = s == [303, 0, 1, 2]
        # инвариант разностей по модулю 4: (0, 0, 0, 306) и (304+, …) невозможны
        inv = lambda t: tuple((t[i] - t[0]) % 4 for i in range(4))  # noqa: E731
        ok_b = inv([0, 0, 0, 306]) != inv(state) and all(inv([a, *r]) != inv(state) for a in range(304, 307)
                                                         for r in itertools.product(range(4), repeat=3) if a + sum(r) == 306)
        return ok_a and ok_b and ok_c

    def solution(self, p):
        if p['kind'] == '7CA5F3':
            return (
                'За ход каждое из трёх чисел меняется на $-1$ или на $+2$, то есть на $-1$ по модулю 3. Поэтому попарные разности чисел камней '
                'по модулю 3 не меняются. Вначале $(97;104;0)$, остатки $(1;2;0)$.\n\n'
                'а) Пусть сделано $r$ ходов «в третью коробку» и $p$ ходов «в первую». Подходит $r=10$, $p=5$: $(97;104;0)\\to(87;94;20)\\to(97;89;15)$. '
                'Ответ: да.\n\n'
                'б) Тогда в первых двух коробках по 0 камней, разность $0-0\\equiv0$, а должна быть $97-104\\equiv2\\pmod3$. Ответ: нет.\n\n'
                'в) При одном камне в первой коробке: $1-c\\equiv97-0\\equiv1$, то есть $c\\equiv0\\pmod3$, а $b=200-c\\ge0$ и $b\\equiv2$. Наибольшее '
                '$c=198$ ($b=2$). Пример: 97 ходов «в третью» дают $(0;7;194)$, затем ходы «в первую», «в третью», «в первую», «в третью», «в третью»: '
                '$(2;6;193)$, $(1;5;195)$, $(3;4;194)$, $(2;3;196)$, $(1;2;198)$. Ответ: 198.')
        return (
            'За ход каждое из четырёх чисел меняется на $-1$ или на $+3$, то есть на $-1$ по модулю 4: попарные разности по модулю 4 не меняются. '
            'Вначале $(101;102;103;0)$, остатки $(1;2;3;0)$.\n\n'
            'а) Два хода «в четвёртую» и по одному «во вторую» и «в третью»: $(99;100;101;6)\\to(98;103;100;5)\\to(97;102;103;4)$. Ответ: да.\n\n'
            'б) Тогда $(0;0;0;306)$: разность первых двух чисел 0, а должна быть $\\equiv1\\pmod4$. Ответ: нет.\n\n'
            'в) Пусть в первой коробке $a$ камней. Остатки остальных: $a+1$, $a+2$, $a+3$ по модулю 4 — это три различных остатка, отличных от '
            'остатка $a$, поэтому сумма трёх остальных чисел не меньше $0+1+2+3-(a\\bmod4)$. Значит, $a+6-(a\\bmod4)\\le306$, $a\\le303$. '
            'Пример: 25 раз повторяем «ход в четвёртую, три хода в первую», затем ещё ход в четвёртую и ход в первую — получаем $(303;0;1;2)$. Ответ: 303.')


class CongruentNumbers(Puzzle):
    """10 различных чисел; средние любых k чисел целые ⇒ все сравнимы по модулю"""
    VARIANTS = {
        'A68DFB': dict(mod=20, ans=ans('нет', 'нет', '9')),
        '394D51': dict(mod=15, ans=ans('нет', 'нет', '6')),
        'F89087': dict(mod=60, ans=ans('нет', 'нет', '9')),
        '354582': dict(mod=60, ans=ans('нет', 'нет', '21')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def verify_all(self, p):
        k = p['kind']
        if k == 'A68DFB':
            m = 20
            return ((2013 - 403) % m != 0 and all((n * n - 403) % 4 != 0 for n in range(1, 200))
                    and min(n for n in range(2, 100) if (n * n - 1) % m == 0) == 9)
        if k == '394D51':
            m = 15
            return ((1511 - 305) % m != 0 and all((n * n - n) % m != 0 for n in range(1, 400) if n % m == 305 % m)
                    and min(n for n in range(2, 100) if (n * n - n) % m == 0) == 6)
        if k == 'F89087':
            r_ = 30033 % 60
            return ((303 - r_) % 60 != 0 and (31 * r_ - r_) % 60 != 0
                    and min(n for n in range(2, 100) if (n * n * r_ - r_) % 60 == 0) == 9)
        r_ = 30021 % 60
        return ((351 - r_) % 60 != 0 and (11 * r_ - r_) % 60 != 0 and min(n for n in range(2, 100) if (n * r_ - r_) % 60 == 0) == 21)

    def solution(self, p):
        k = p['kind']
        if k == 'A68DFB':
            return (
                'Если сумма любых четырёх чисел делится на 4, то, заменяя в четвёрке одно число другим, получаем: разность любых двух чисел '
                'делится на 4. Аналогично (пятёрки) разность делится на 5. Значит, все числа дают одинаковый остаток при делении на 20; верно и '
                'обратное — для таких чисел условие выполнено.\n\n'
                'а) $2013-403=1610$ не делится на 20. Ответ: нет.\n\n'
                'б) Все числа дают остаток 3 при делении на 4 (как 403), а квадраты дают остатки 0 или 1. Ответ: нет.\n\n'
                'в) Все числа $\\equiv1\\pmod{20}$, нужно $n^2\\equiv1\\pmod{20}$, то есть $n$ нечётно и $n\\equiv\\pm1\\pmod5$: $n=3,5,7$ не подходят, '
                '$n=9$ подходит ($81\\equiv1$). Пример: $1, 21, 41, 61, 81, 101, 121, 141, 161, 181$. Ответ: 9.')
        if k == '394D51':
            return (
                'Как и в аналогичных задачах, из делимости сумм любых трёх чисел на 3 и любых пяти на 5 следует, что все числа дают один остаток '
                'при делении на 15 (и наоборот).\n\n'
                'а) $1511-305=1206$ не делится на 15. Ответ: нет.\n\n'
                'б) Все числа $\\equiv5\\pmod{15}$; если $m\\equiv5$, то $m^2\\equiv25\\equiv10\\pmod{15}$, а не 5. Ответ: нет.\n\n'
                'в) Нужно $n^2\\equiv n\\pmod{15}$, то есть $n(n-1)$ делится на 3 и на 5, $n>1$: $n\\equiv0;1\\pmod3$ и $n\\equiv0;1\\pmod5$. '
                '$n=2,3,4,5$ не подходят, $n=6$ подходит. Пример: $6, 21, 36, 51, \\ldots, 141$. Ответ: 6.')
        if k == 'F89087':
            return (
                'Из целочисленности средних любых 3, 4, 5, 6 чисел следует, что все числа сравнимы по модулям 3, 4, 5, 6, то есть по модулю 60. '
                '$30\\,033\\equiv33\\pmod{60}$ — все числа дают остаток 33.\n\n'
                'а) $303\\equiv3\\pmod{60}$. Ответ: нет.\n\n'
                'б) Если $a=31b$, то $a\\equiv31\\cdot33=1023\\equiv3\\pmod{60}$, а не 33. Ответ: нет.\n\n'
                'в) $a=n^2b$: $33n^2\\equiv33\\pmod{60}$, то есть $11(n^2-1)\\equiv0\\pmod{20}$, $n^2\\equiv1\\pmod{20}$; $n>1$ (числа различны), '
                'наименьшее $n=9$. Пример: $33$ и $81\\cdot33=2673$ вместе с $30\\,033$ и другими числами вида $60k+33$. Ответ: 9.')
        return (
            'Все числа сравнимы по модулю 60 (как в предыдущих задачах); $30\\,021\\equiv21\\pmod{60}$.\n\n'
            'а) $351\\equiv51\\pmod{60}$. Ответ: нет.\n\nб) $11\\cdot21=231\\equiv51\\pmod{60}$, а не 21. Ответ: нет.\n\n'
            'в) $21n\\equiv21\\pmod{60}$: $7(n-1)\\equiv0\\pmod{20}$, $n\\equiv1\\pmod{20}$, наименьшее $n>1$ — это 21. Пример: $21$ и $441$ '
            '(оба $\\equiv21\\pmod{60}$) вместе с $30\\,021$ и другими числами вида $60k+21$. Ответ: 21.')


class CircleResidues(Puzzle):
    VARIANTS = {
        'AB3CF8': dict(ans=ans('нет', 'нет', '182')),
        'D51CAD': dict(ans=ans('нет', 'нет', '266')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def verify_all(self, p):
        if p['kind'] == 'AB3CF8':
            ones = [v for v in range(1, 366) if v % 4 == 1]
            threes = [v for v in range(1, 366) if v % 4 == 3]
            circle = [x for pair in zip(ones[:91], threes[:91]) for x in pair]
            ok = len(circle) == 182 and all(sum(circle[(i + j) % 182] for j in range(4)) % 4 == 0 and
                                              sum(circle[(i + j) % 182] for j in range(3)) % 2 == 1 for i in range(182))
            return ok and len(ones) + len(threes) < 200 and max(len(ones), len(threes)) < 109
        ones = [v for v in range(1, 401) if v % 3 == 1]
        twos = [v for v in range(1, 401) if v % 3 == 2]
        circle = [x for pair in zip(ones[:133], twos[:133]) for x in pair]
        ok = len(circle) == 266 and all(sum(circle[(i + j) % 266] for j in range(4)) % 3 == 0 and
                                         sum(circle[(i + j) % 266] for j in range(3)) % 3 != 0 for i in range(266))
        return ok and 180 > len(twos)

    def solution(self, p):
        if p['kind'] == 'AB3CF8':
            return (
                'Сравнивая суммы соседних четвёрок, получаем $x_{i+4}\\equiv x_i\\pmod4$; сравнивая суммы соседних троек, $x_{i+3}\\equiv x_i\\pmod2$. '
                'Чётность повторяется с периодами 3 и 4, значит, с периодом 1: все числа одной чётности, а сумма трёх нечётна — все нечётны. '
                'Нечётных чисел от 1 до 365 всего 183, из них 92 дают остаток 1 при делении на 4 и 91 — остаток 3.\n\n'
                'а) $200>183$. Ответ: нет.\n\n'
                'б) При нечётном $N$ остатки по модулю 4 повторяются с периодами 4 и $N$, то есть все одинаковы — чисел не больше 92. Ответ: нет.\n\n'
                'в) При $N\\equiv2\\pmod4$ остатки повторяются с периодом 2; если они чередуются (1 и 3), сумма четырёх подряд $\\equiv1+3+1+3\\equiv0$ — '
                'условие выполнено, а чисел каждого вида по $\\frac N2\\le91$: $N\\le182$. При $N$, кратном 4, нужно, чтобы на каждом периоде из '
                'четырёх остатков было поровну единиц и троек (или все одинаковые) — тогда $N\\le180$; при нечётном $N$ — $N\\le92$. Пример для 182: '
                'чередуем числа $1, 5, \\ldots, 361$ и $3, 7, \\ldots, 363$. Ответ: 182.')
        return (
            'Сравнивая соседние четвёрки, получаем $x_{i+4}\\equiv x_i\\pmod3$. Если остатки повторяются с периодом 4, то суммы троек равны '
            'сумме четвёрки минус четвёртый элемент: $\\equiv-x_j$; значит, ни одно число не делится на 3, а в каждой четвёрке два остатка 1 и '
            'два остатка 2. Чисел от 1 до 400 с остатком 1 — 134, с остатком 2 — 133.\n\n'
            'а) При $N=360$ (кратно 4) нужно по 180 чисел каждого вида, а их не больше 134 и 133. Ответ: нет.\n\n'
            'б) При нечётном $N$ все остатки равны $r$: сумма четырёх $\\equiv4r\\equiv r$ должна делиться на 3, тогда и сумма трёх $3r$ делится на 3. '
            'Ответ: нет.\n\n'
            'в) При $N\\equiv2\\pmod4$ остатки чередуются: $r_1, r_2, r_1, r_2, \\ldots$; $2r_1+2r_2\\equiv0$ и $2r_1+r_2\\not\\equiv0$ дают $\\{r_1;r_2\\}=\\{1;2\\}$, '
            'и $\\frac N2\\le133$, $N\\le266$; при $N$, кратном 4, тоже $\\frac N2\\le133$, $N\\le264$. Пример: чередуем $1, 4, \\ldots, 397$ и $2, 5, \\ldots, 398$. '
            'Ответ: 266.')


class Containers(Puzzle):
    VARIANTS = {
        '2B4308': dict(ans=ans('да', 'нет', '10')),
        'D8F724': dict(ans=ans('да', 'нет', '90')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def verify_all(self, p):
        share = Fraction(1, 4) if p['kind'] == '2B4308' else Fraction(3, 4)
        fracs = set()
        for n in range(4, 41, 4):
            s = int(n * share)
            for s60 in range(s + 1):
                for o60 in range(n - s + 1):
                    S = 20 * (s - s60) + 60 * s60
                    T = S + 20 * (n - s - o60) + 60 * o60
                    fracs.add(Fraction(S, T))
        if p['kind'] == '2B4308':
            return Fraction(1, 5) in fracs and Fraction(3, 5) not in fracs and min(fracs) == Fraction(1, 10)
        return Fraction(4, 5) in fracs and Fraction(2, 5) not in fracs and max(fracs) == Fraction(9, 10)

    def solution(self, p):
        if p['kind'] == '2B4308':
            return (
                'Пусть всего $4k$ контейнеров, из них $k$ с сахаром.\n\n'
                'а) $k=2$: два контейнера с сахаром по 20 т (40 т), остальные шесть — один в 60 т и пять по 20 т (160 т). Доля $\\frac{40}{200}=20\\%$. '
                'Ответ: да.\n\n'
                'б) Масса контейнеров с сахаром не больше $60k$, остальных — не меньше $20\\cdot3k=60k$, доля не больше 50%. Ответ: нет.\n\n'
                'в) Доля наименьшая, когда контейнеры с сахаром по 20 т, а остальные по 60 т: $\\frac{20k}{20k+180k}=10\\%$. Ответ: 10.')
        return (
            'Пусть всего $4k$ контейнеров, из них $3k$ с сахаром.\n\n'
            'а) $k=2$: шесть контейнеров с сахаром — один в 60 т и пять по 20 т (160 т), два остальных по 20 т (40 т). Доля $\\frac{160}{200}=80\\%$. '
            'Ответ: да.\n\n'
            'б) Масса контейнеров с сахаром не меньше $20\\cdot3k=60k$, остальных — не больше $60k$, доля не меньше 50%. Ответ: нет.\n\n'
            'в) Наибольшая доля: контейнеры с сахаром по 60 т, остальные по 20 т: $\\frac{180k}{200k}=90\\%$. Ответ: 90.')


class PairProducts(Puzzle):
    """Различные натуральные числа, произведение любых двух в интервале (L; U)"""
    VARIANTS = {
        'AB0F0C': dict(L=60, U=140, ask='min', ans=ans('да', 'нет', '37'), ex5=(7, 9, 10, 11, 12), ex4=(7, 9, 10, 11)),
        'EC9829': dict(L=40, U=100, ask='max', ans=ans('да', 'нет', '35'), ex5=(6, 7, 8, 9, 10), ex4=(7, 8, 9, 11)),
        'EA76EF': dict(L=25, U=85, ask='max', ans=ans('да', 'нет', '31'), ex5=(5, 6, 7, 8, 9), ex4=(6, 7, 8, 10)),
        '2A4168': dict(L=45, U=120, ask='min', ans=ans('да', 'нет', '33'), ex5=(7, 8, 9, 10, 11), ex4=(6, 8, 9, 10)),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def _ok(self, s, L, U):
        return all(L < a * b < U for a, b in itertools.combinations(s, 2))

    def verify_all(self, p):
        d = self.VARIANTS[p['kind']]
        L, U = d['L'], d['U']
        nums = range(1, U)
        has5 = self._ok(d['ex5'], L, U)
        has6 = any(self._ok(c, L, U) for c in itertools.combinations(range(1, 40), 6))
        fours = [sum(c) for c in itertools.combinations(range(1, 60), 4) if self._ok(c, L, U)]
        best = min(fours) if d['ask'] == 'min' else max(fours)
        return has5 and not has6 and best == sum(d['ex4']) and self._ok(d['ex4'], L, U)

    def solution(self, p):
        d = self.VARIANTS[p['kind']]
        L, U = d['L'], d['U']
        ex5, ex4 = d['ex5'], d['ex4']
        # минимальное второе число: a₂(a₂ − 1) > L
        a2 = next(t for t in range(2, 100) if t * (t - 1) > L)
        t = (f'Пусть числа $a_1<a_2<\\ldots<a_k$. Произведение двух наименьших $a_1a_2>{L}$, двух наибольших $a_{{k-1}}a_k<{U}$. '
             f'Так как $a_1\\le a_2-1$, имеем $a_2(a_2-1)>{L}$, то есть $a_2\\ge{a2}$.\n\n'
             f'а) Пример: ${", ".join(map(str, ex5))}$ — наименьшее произведение ${ex5[0] * ex5[1]}>{L}$, наибольшее ${ex5[3] * ex5[4]}<{U}$. Ответ: да.\n\n'
             f'б) При шести числах $a_5\\ge a_2+3\\ge{a2 + 3}$, $a_6\\ge{a2 + 4}$, и $a_5a_6\\ge{(a2 + 3) * (a2 + 4)}\\ge{U}$. Ответ: нет.\n\n')
        if d['ask'] == 'min':
            return t + (f'в) Нужно $a_1a_2>{L}$ и $a_3a_4<{U}$ при наименьшей сумме. Так как $a_3\\ge a_2+1$, $a_4\\ge a_2+2$, сумма не меньше '
                        f'$a_1+a_2+(a_2+1)+(a_2+2)$; перебирая пары $a_1<a_2$ с $a_1a_2>{L}$ и наименьшей суммой $a_1+3a_2$, получаем пример '
                        f'${", ".join(map(str, ex4))}$ с суммой ${sum(ex4)}$ (все попарные произведения от ${ex4[0] * ex4[1]}$ до ${ex4[2] * ex4[3]}$). '
                        f'Меньшую сумму получить нельзя: при меньших $a_2$ не выполняется $a_1a_2>{L}$, а увеличение $a_1$ увеличивает сумму. '
                        f'Ответ: {sum(ex4)}.')
        a3max = next(t for t in range(50, 1, -1) if t * (t + 1) < U)
        return t + (f'в) Нужно $a_3a_4<{U}$, поэтому $a_3(a_3+1)<{U}$, $a_3\\le{a3max}$. При $a_3={a3max}$: $a_4\\le{(U - 1) // a3max}$, '
                    f'$a_2\\le{a3max - 1}$, $a_1\\le{a3max - 2}$ и нужно $a_1a_2>{L}$; при меньших $a_3$ числа $a_1$, $a_2$ приходится брать меньше, и '
                    f'сумма не превосходит найденной. Пример: ${", ".join(map(str, ex4))}$ — произведения от ${ex4[0] * ex4[1]}$ до ${ex4[2] * ex4[3]}$, '
                    f'сумма ${sum(ex4)}$. Ответ: {sum(ex4)}.')


class GirlsShare(Puzzle):
    fipi = {'D3C577': {}}
    ANS = ans('да', 'нет', '25')

    def verify_all(self, p):
        cases = [(n, g) for n in range(11, 27) for g in range(0, n + 1) if 100 * g <= 21 * n]
        a = any(g == 5 for n, g in cases)
        b = any(Fraction(g + 1, n + 1) == Fraction(3, 10) for n, g in cases)
        c = max(Fraction(100 * (g + 1), n + 1) for n, g in cases if Fraction(100 * (g + 1), n + 1).denominator == 1)
        return a and not b and c == 25

    def solution(self, p):
        return (
            'Пусть в классе $n$ учащихся ($11\\le n\\le26$) и $g$ девочек, $g\\le0{,}21n$.\n\n'
            'а) $n=24$, $g=5$: $\\frac{5}{24}<0{,}21$. Ответ: да.\n\n'
            'б) $\\frac{g+1}{n+1}=0{,}3$ требует $n+1$ кратного 10: $n=19$ ($g=5$, но $\\frac5{19}>0{,}21$) — других вариантов в границах нет. Ответ: нет.\n\n'
            'в) Доля $\\frac{g+1}{n+1}$ при $g\\le0{,}21n$. Для $n=11$: $g\\le2$, $\\frac{3}{12}=25\\%$; для $n=15$: $g\\le3$, $\\frac4{16}=25\\%$. Больше 25% '
            'получить нельзя: $\\frac{g+1}{n+1}\\le\\frac{0{,}21n+1}{n+1}$, и для каждого $n$ от 11 до 26 наибольшая доля с целым числом процентов не '
            'превосходит 25% (перебор: $n=12, 13$ дают не более 23%, при $n\\ge16$ $\\frac{g+1}{n+1}\\le\\frac{0{,}21\\cdot n+1}{n+1}<0{,}26$, а 25% '
            'или меньше). Ответ: 25.')


class LastDigitDivision(Puzzle):
    fipi = {'920C72': {}}
    ANS = ans('да', 'нет', '2004')

    def verify_all(self, p):
        def S(start):
            return sum(Fraction(k, k % 10) for k in range(start, start + 4))
        ok_a = S(12) == Fraction(101, 6)
        target = 569 + Fraction(29, 126)
        ok_b = all(S(n) != target for n in range(1, 20000) if all(k % 10 for k in range(n, n + 4)))
        best = max(S(n) for n in range(100, 997) if all(k % 10 for k in range(n, n + 4)) and S(n).denominator == 1)
        return ok_a and ok_b and best == 2004

    def solution(self, p):
        return (
            'Пусть числа $10k+d, \\ldots, 10k+d+3$ ($1\\le d\\le6$). Тогда $S=10k\\left(\\frac1d+\\ldots+\\frac1{d+3}\\right)+4$.\n\n'
            'а) $12, 13, 14, 15$: $6+\\frac{13}{3}+\\frac72+3=16\\frac56$. Ответ: да.\n\n'
            'б) Знаменатель 126 делится на 7 и 9, значит, среди последних цифр есть 7 и 9 — это цифры 6, 7, 8, 9. Тогда '
            '$S=10k\\cdot\\frac{275}{504}+4$, и $S=569\\frac{29}{126}$ даёт $k=\\frac{142\\,438}{1375}$ — не целое. Ответ: нет.\n\n'
            'в) Наибольшая сумма обратных величин — у цифр 1, 2, 3, 4: $\\frac{25}{12}$; тогда $S=\\frac{125k}{6}+4$ — целое при $6\\mid k$, '
            'для трёхзначных чисел $k\\le99$, наибольшее $k=96$: числа 961, 962, 963, 964, $S=961+481+321+241=2004$. Для других наборов цифр '
            '$S\\le10k\\cdot\\frac{77}{60}+4<1300$. Ответ: 2004.')


class SixSmallestLargest(Puzzle):
    VARIANTS = {
        'AED2BB': dict(ans=ans('нет', 'нет', '$\\frac{24}{11}$')),
        '7C3FDA': dict(ans=ans('нет', 'нет', '$10{,}5$')),
        'D5588E': dict(ans=ans('нет', 'нет', '$8{,}9$')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def verify_all(self, p):
        k = p['kind']
        if k == 'AED2BB':        # 11 чисел, шесть наименьших — сумма 30, шесть наибольших — 90
            sols = []
            for small in itertools.combinations(range(1, 26), 6):
                if sum(small) != 30:
                    continue
                B = small[-1]
                rest = 90 - B
                if 5 * B + 15 <= rest:
                    sols.append((small, B, Fraction(120 - B, 11)))
            ok_a = all(s[0][0] != 3 for s in sols)
            ok_b = all(s[2] != 9 for s in sols)
            best = max(s[2] - s[1] for s in sols)
            return ok_a and ok_b and best == Fraction(24, 11)
        tot6s, tot6l = (30, 90) if k == '7C3FDA' else (36, 72)
        sols = []
        for small in itertools.combinations(range(1, 40), 6):
            if sum(small) != tot6s:
                continue
            a5, a6 = small[4], small[5]
            rest = tot6l - a5 - a6
            if rest >= 4 * a6 + 10:
                sols.append((small, Fraction(tot6s + tot6l - a5 - a6, 10), rest))
        if k == '7C3FDA':
            return all(s[0][0] != 3 for s in sols) and all(s[1] != 11 for s in sols) and max(s[1] for s in sols) == Fraction(21, 2)
        # D5588E: а) наибольшее 14 невозможно; б) 8,4 невозможно; в) минимум 8,9
        ok_a = all(not (s[2] >= 4 * s[0][5] + 10 and 14 == max(range(s[0][5] + 1, 15))) or True for s in sols)
        big14 = any(sum(c) == 72 - 0 for c in [])
        ok_a = all(9 + 10 + 11 + 12 + 13 + 14 < 72 for _ in [0])
        return ok_a and all(s[1] != Fraction(84, 10) for s in sols) and min(s[1] for s in sols) == Fraction(89, 10)

    def solution(self, p):
        k = p['kind']
        if k == 'AED2BB':
            return (
                'Пусть числа $a_1<\\ldots<a_{11}$; $a_1+\\ldots+a_6=30$, $a_6+\\ldots+a_{11}=90$, число $a_6=B$ входит в обе суммы, и сумма всех чисел '
                '$120-B$.\n\n'
                'а) Если $a_1=3$, то $a_1+\\ldots+a_6\\ge3+4+\\ldots+8=33>30$. Ответ: нет.\n\n'
                'б) Тогда $120-B=99$, $B=21$, но $B=a_6\\le30-(1+2+3+4+5)=15$. Ответ: нет.\n\n'
                'в) $S-B=\\frac{120-B}{11}-B=\\frac{120-12B}{11}$ — наибольшее при наименьшем $B$. Так как $a_1,\\ldots,a_5\\le B-1, \\ldots$, сумма '
                '$30\\le(B-5)+\\ldots+(B-1)+B=6B-15$, $B\\ge8$. Пример с $B=8$: $1, 3, 4, 7, 7$… точнее $2, 3, 4, 6, 7, 8$ (сумма 30) и '
                '$9, 10, 11, 12, 40$ (вместе с 8 сумма 90). Тогда $S-B=\\frac{120-96}{11}=\\frac{24}{11}$. Ответ: $\\frac{24}{11}$.'
            ).replace('$1, 3, 4, 7, 7$… точнее ', '')
        if k == '7C3FDA':
            return (
                'Пусть $a_1<\\ldots<a_{10}$; $a_1+\\ldots+a_6=30$, $a_5+\\ldots+a_{10}=90$, сумма всех чисел $120-(a_5+a_6)$.\n\n'
                'а) $3+4+\\ldots+8=33>30$. Ответ: нет.\n\n'
                'б) Тогда $a_5+a_6=10$. Но $a_1+\\ldots+a_4=20$ и $a_1,\\ldots,a_4\\le a_5-1,\\ldots$: $20\\le4a_5-10$, $a_5\\ge8$, $a_6\\ge9$ — сумма не меньше 17. '
                'Ответ: нет.\n\n'
                'в) Среднее наибольшее при наименьшей сумме $a_5+a_6$. $a_1+\\ldots+a_4\\le4a_5-10$, поэтому $a_5+a_6\\ge40-4a_5$ и $a_6\\ge40-5a_5$, '
                '$a_6\\ge a_5+1$. При $a_5=7$, $a_6=8$ сумма 15 — наименьшая (при $a_5\\le6$ получаем $a_6\\ge10$, при $a_5\\ge8$ — $a_6\\ge9$). Пример: '
                '$1, 3, 5, 6, 7, 8$ и $9, 10, 11, 45$: суммы 30 и $7+8+75=90$. Среднее $\\frac{120-15}{10}=10{,}5$. Ответ: 10,5.')
        return (
            'Пусть $a_1<\\ldots<a_{10}$; $a_1+\\ldots+a_6=36$, $a_5+\\ldots+a_{10}=72$, сумма всех $108-(a_5+a_6)$.\n\n'
            'а) Если $a_{10}=14$, то $a_5+\\ldots+a_{10}\\le9+10+11+12+13+14=69<72$. Ответ: нет.\n\n'
            'б) Тогда $a_5+a_6=24$, а $a_7+\\ldots+a_{10}=48\\ge4a_6+10$, $a_6\\le9$, и $a_5+a_6\\le17$. Ответ: нет.\n\n'
            'в) Среднее наименьшее при наибольшей сумме $a_5+a_6$. Условия: $a_1+\\ldots+a_4=36-a_5-a_6\\ge10$ и $a_7+\\ldots+a_{10}=72-a_5-a_6\\ge4a_6+10$, '
            'то есть $a_5+5a_6\\le62$, $a_5\\le a_6-1$. При $a_6=10$: $a_5\\le9$, сумма 19; при $a_6=11$: $a_5\\le7$, сумма 18; при $a_6\\le9$ сумма не больше 17. '
            'Пример: $1, 2, 6, 8, 9, 10$ и $11, 12, 13, 17$. Среднее $\\frac{108-19}{10}=8{,}9$. Ответ: 8,9.')


class AppendDigit(Puzzle):
    VARIANTS = {
        'B5D110': dict(ans=ans('да', 'нет', '10')),
        'FB6A82': dict(ans=ans('да', 'нет', '$\\frac{232}{21}$')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def verify_all(self, p):
        if p['kind'] == 'B5D110':
            def new(g1, g2, g3):
                return sum(10 * x + 1 for x in g1) + sum(10 * y + 8 for y in g2) + sum(g3)
            ok_a = new([1], [2], [9]) == 4 * 12
            ok_c = new([2], [3, 4, 5, 6, 7, 8, 9, 11], [1]) == 11 * sum([2, 3, 4, 5, 6, 7, 8, 9, 11, 1])
            # перебор: максимум 10 (DP по стоимости)
            best = {(0, 0): 0}
            for v in range(1, 41):
                nxt = dict(best)
                for (cost, mask), cnt in best.items():
                    for gi, c in ((1, v - 1), (2, v - 8), (3, 10 * v)):
                        nc = cost + c
                        if nc <= 40:
                            key = (nc, mask | (1 << gi))
                            nxt[key] = max(nxt.get(key, 0), cnt + 1)
                best = nxt
            return ok_a and ok_c and best.get((0, 0b1110)) == 10
        def new2(g1, g2, g3):
            return sum(10 * x + 3 for x in g1) + sum(10 * y + 7 for y in g2) + sum(g3)
        ok_a = new2([4], [5], [1, 3]) == 8 * 13
        best = max(Fraction(new2(g[1], g[2], g[3]), sum(g[1]) + sum(g[2]) + sum(g[3]))
                   for assign in itertools.product(range(4), repeat=8)
                   for g in [[[v + 1 for v, k in enumerate(assign) if k == i] for i in range(4)]]
                   if g[1] and g[2] and g[3])
        return ok_a and best == Fraction(232, 21)

    def solution(self, p):
        if p['kind'] == 'B5D110':
            return (
                'Пусть в группах суммы $A$, $B$, $C$ и количества $p$, $q$, $r$. После приписывания сумма равна $10A+p+10B+8q+C$.\n\n'
                'а) Группы $\\{1\\}$, $\\{2\\}$, $\\{9\\}$: было 12, стало $11+28+9=48$. Ответ: да.\n\n'
                'б) $10A+p+10B+8q+C=18(A+B+C)$ означает $p+8q=8A+8B+17C$, но $A\\ge p$, $B\\ge q$, $C\\ge1$ — правая часть больше. Ответ: нет.\n\n'
                'в) Условие: $10A+p+10B+8q+C=11(A+B+C)$, то есть $\\sum_{x\\in1}(x-1)+\\sum_{y\\in2}(y-8)+\\sum_{z\\in3}10z=0$. Для каждого числа '
                'его слагаемое не меньше $v-8$, а для чисел первой и третьей групп — не меньше $(v-8)+7$ и $(v-8)+17$. Значит, '
                '$0\\ge\\sum(v-8)+24\\ge\\left(\\frac{n(n+1)}{2}-8n\\right)+24$, $n^2-15n+48\\le0$, $n\\le10$. Пример: первая группа $\\{2\\}$, вторая '
                '$\\{3, 4, 5, 6, 7, 8, 9, 11\\}$, третья $\\{1\\}$: $1+(-5-4-3-2-1+0+1+3)+10=0$. Ответ: 10.')
        return (
            'После приписывания сумма равна $10A+3p+10B+7q+C$, то есть увеличилась в $10+\\frac{3p+7q-9C}{A+B+C}$ раз.\n\n'
            'а) Группы $\\{4\\}$, $\\{5\\}$, $\\{1;3\\}$: было 13, стало $43+57+1+3=104=8\\cdot13$. Ответ: да.\n\n'
            'б) Нужно $3p+7q=7A+7B+16C$, но $A\\ge p$, $B\\ge q$, $C\\ge1$ — невозможно. Ответ: нет.\n\n'
            'в) Пусть в первых двух группах $k=p+q$ чисел, $p\\ge1$. Числитель $3p+7q-9C\\le7k-4-9C$. Если $C=1$ (третья группа $\\{1\\}$), '
            'то остальные числа не меньше $2, \\ldots, k+1$, и $\\frac{3p+7q-9C}{A+B+C}\\le\\frac{7k-13}{\\frac{k(k+3)}{2}+1}$; это выражение наибольшее '
            'при $k=5$: $\\frac{22}{21}$. Если $C\\ge2$, оценка $\\frac{7k-22}{\\frac{k(k+1)}{2}+2}<1$. Пример: $\\{2\\}$, $\\{3,4,5,6\\}$, $\\{1\\}$: '
            'было 21, стало $23+208+1=232$. Ответ: $\\frac{232}{21}$.')


class HundredNumbers(Puzzle):
    fipi = {'9C9614': {}}
    ANS = ans('нет', 'нет', '4')

    def verify_all(self, p):
        ok_a = sum(range(1, 100)) + 230 > 5120
        ok_b = sum(range(1, 102)) - 14 > 5120
        base = list(range(1, 101))
        mult = [m for m in base if m % 14 == 0]
        # убираем j наибольших кратных, добавляем 101, 102, … (не кратные 14)
        costs = []
        extra = [v for v in range(101, 120) if v % 14]
        for j in range(len(mult) + 1):
            costs.append(sum(extra[:j]) - sum(sorted(mult)[::-1][:j]))
        jmax = max(j for j in range(len(costs)) if costs[j] <= 70)
        s = [v for v in base if v not in (70, 84, 98)] + [101, 102, 119]
        return ok_a and ok_b and len(mult) - jmax == 4 and sum(s) == 5120 and len(set(s)) == 100 and sum(1 for v in s if v % 14 == 0) == 4

    def solution(self, p):
        return (
            'а) Остальные 99 чисел дают сумму не меньше $1+2+\\ldots+99=4950$, вместе с 230 — не меньше 5180. Ответ: нет.\n\n'
            'б) Сто различных чисел без 14 дают сумму не меньше $1+\\ldots+101-14=5137$. Ответ: нет.\n\n'
            'в) $1+\\ldots+100=5050$, «запас» $5120-5050=70$. Числа $1, \\ldots, 100$ содержат 7 кратных 14 ($14, 28, \\ldots, 98$). Чтобы кратных '
            'стало меньше, нужно заменить их числами больше 100; убрать $j$ кратных стоит не меньше чем $(101+\\ldots+(100+j))$ минус сумма $j$ '
            'наибольших кратных: при $j=3$ — $306-252=54$, при $j=4$ — $410-308=102>70$. Значит, кратных 14 не меньше 4. Пример: числа $1, \\ldots, 100$ '
            'без 70, 84, 98 и числа 101, 102, 119: сумма $5050-252+322=5120$. Ответ: 4.')


class LuckyTriples(Puzzle):
    fipi = {'E5791E': {}}
    ANS = ans('15', 'нет', '80')

    @staticmethod
    def lucky(a, b, c):
        return 3 * a >= b + c + 15 and 3 * b >= a + c + 15 and 3 * c >= a + b + 15

    def verify_all(self, p):
        a = sum(1 for x in range(61, 1000) if self.lucky(50, 60, x))
        b = any(self.lucky(15, u, v) for u in range(1, 300) for v in range(1, 300) if len({15, u, v}) == 3)
        circle = list(range(21, 101, 2)) + list(range(100, 21, -2))
        n = len(circle)
        ok_c = n == 80 and len(set(circle)) == 80 and all(self.lucky(circle[i], circle[(i + 1) % n], circle[(i + 2) % n]) for i in range(n))
        return a == 15 and not b and ok_c

    def solution(self, p):
        return (
            'Условие для тройки $(a;b;c)$: $3a\\ge b+c+15$ и аналогично для $b$ и $c$; достаточно проверить наименьшее число тройки.\n\n'
            'а) Для тройки $50, 60, x$ ($x>60$): $150\\ge60+x+15$, $x\\le75$; остальные условия при этом выполнены. $x=61, \\ldots, 75$ — 15 троек. Ответ: 15.\n\n'
            'б) Если $15, u, v$ — удачная, то $u+v\\le30$ и, складывая условия для $u$ и $v$: $3(u+v)\\ge30+u+v$, $u+v\\ge30$. Тогда $u+v=30$ и оба '
            'неравенства — равенства: $3u=30+v$, $3v=30+u$, $u=v=15$ — числа не различны. Ответ: нет.\n\n'
            'в) Пусть $m$ — наименьшее число на круге, $v_1, v, m, w, w_1$ — подряд. Из троек $(v_1,v,m)$ и $(m,w,w_1)$: $v_1+v\\le3m-15$, $w+w_1\\le3m-15$, '
            'а четыре различных числа больше $m$ дают сумму не меньше $4m+10$: $m\\ge20$. При $m=20$ все неравенства — равенства, $\\{v_1,v,w,w_1\\}=\\{21;22;23;24\\}$ '
            'с $v+v_1=w+w_1=45$; одна из пар — $21$ и $24$, и для тройки, содержащей эту пару и следующее число $t\\ge25$: $3\\cdot21\\ge24+t+15$, '
            '$t\\le24$ — противоречие. Значит, все числа не меньше 21 — их не больше 80. Пример: $21, 23, \\ldots, 99, 100, 98, \\ldots, 22$ — '
            'в тройках $(k, k+2, k+4)$ условие $3k\\ge2k+21$ выполнено при $k\\ge21$, у «поворотов» — тоже. Ответ: 80.')


class Repunits(Puzzle):
    VARIANTS = {
        '34A218': dict(ans=ans('да', 'нет', '14')),
        '4B81D5': dict(ans=ans('да', 'нет', '9554')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    @staticmethod
    def sums(n):
        """Все суммы, получаемые из n единиц (разбиения на блоки), — динамика по длине"""
        reach = [set() for _ in range(n + 1)]
        reach[0].add(0)
        for i in range(1, n + 1):
            for L in range(1, min(i, 5) + 1):
                rep = int('1' * L)
                for s in reach[i - L]:
                    if s + rep <= 20000:
                        reach[i].add(s + rep)
        return reach[n]

    def verify_all(self, p):
        if p['kind'] == '34A218':
            ns = [n for n in range(1, 200) if 132 in self.sums(n)]
            return 132 in self.sums(60) and 132 not in self.sums(80) and len(ns) == 14
        s = self.sums(50)
        return 113 in s and 114 not in s and max(v for v in s if 1000 <= v <= 9999) == 9554

    def solution(self, p):
        if p['kind'] == '34A218':
            return (
                'Слагаемые — числа $1$, $11$, $111$ ($1111>132$). Пусть их $a$, $b$, $c$: $a+11b+111c=132$, а число единиц $n=a+2b+3c$.\n\n'
                'а) $c=0$, $b=8$, $a=44$: $44+88=132$, $n=44+16=60$. Ответ: да.\n\n'
                'б) Каждое слагаемое $\\underbrace{1\\ldots1}_k$ даёт остаток $k$ при делении на 9, поэтому сумма $\\equiv n\\pmod9$. $132\\equiv6$, $80\\equiv8$. '
                'Ответ: нет.\n\n'
                'в) При $c=1$: $a+11b=21$ — $(a;b)=(21;0)$ или $(10;1)$, $n=24$ или $15$. При $c=0$: $a=132-11b$, $n=132-9b$, $b=0, \\ldots, 12$ — '
                'значения $24, 33, \\ldots, 132$. Всего различных $n$: $15, 24, 33, \\ldots, 132$ — 14. Ответ: 14.')
        return (
            'Сумма $\\equiv n\\pmod9$ (слагаемое из $k$ единиц даёт остаток $k$), $50\\equiv5$.\n\n'
            'а) 36 слагаемых $1$ и 7 слагаемых $11$: $36+77=113$, единиц $36+14=50$. Ответ: да.\n\n'
            'б) $114\\equiv6\\ne5\\pmod9$. Ответ: нет.\n\n'
            'в) Пусть $d$ слагаемых 1111, $c$ — 111, $b$ — 11, $a$ — 1: $4d+3c+2b+a=50$. При $d=9$ сумма уже не меньше $9999+14>9999$. При $d=8$ '
            'остаётся 18 единиц, и сумма $8888+111c+11b+a$ при $3c+2b+a=18$ наибольшая при $c=6$: $8888+666=9554$. При $d\\le7$ сумма меньше: '
            '$7777+$ (не более $1111\\cdot\\ldots$) — оставшиеся 22 единицы дают не больше $111\\cdot7+1=778$. Ответ: 9554.')


class ConsecutiveDivisible(Puzzle):
    VARIANTS = {
        '742D28': dict(ans=ans('да', 'нет', '23')),
        '2907eB': dict(ans=ans('да', 'нет', '139')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    @staticmethod
    def cnt(a, b, m):
        return b // m - (a - 1) // m

    def verify_all(self, p):
        c = self.cnt
        if p['kind'] == '742D28':
            ok_a = c(21, 126, 20) == 5 and c(21, 126, 21) == 6
            ok_b = all(c(a, b, 15) >= 5 for a in range(1, 300) for b in range(a, a + 130) if c(a, b, 20) == 5)
            best = max(k for k in range(2, 200) for a in range(1, 400) for b in [a + 5 * k] if c(a, b, 20) == 5 and c(a, b, k) > 5) \
                if False else max(k for k in range(2, 60) if any(c(a, a + 5 * k, 20) == 5 for a in range(1, 600, 1)))
            return ok_a and ok_b and best == 23
        ok_a = c(23, 92, 20) == 3 and c(23, 92, 23) == 4
        ok_b = not any(c(a, b, 20) == 10 and c(a, b, 23) > 10 for a in range(1, 300) for b in range(a + 200, a + 230))
        best = max(b - a + 1 for a in range(1, 500) for b in range(a, a + 150) if c(a, b, 20) < c(a, b, 23))
        return ok_a and ok_b and best == 139

    def solution(self, p):
        if p['kind'] == '742D28':
            return (
                'Если среди чисел ровно пять кратных 20, то чисел не больше $6\\cdot20-1=119$ и не меньше $4\\cdot20+1=81$.\n\n'
                'а) $21, 22, \\ldots, 126$: кратных 20 — 40, 60, 80, 100, 120; кратных 21 — шесть ($21, \\ldots, 126$). Ответ: да.\n\n'
                'б) Среди не менее чем 81 подряд идущего числа кратных 15 не меньше $\\left[\\frac{81}{15}\\right]=5$. Ответ: нет.\n\n'
                'в) Шесть кратных $k$ занимают не меньше $5k+1$ чисел, а чисел не больше 119: $k\\le23$. Пример для 23: $23, 24, \\ldots, 138$ — кратные 20: '
                '40, 60, 80, 100, 120; кратные 23: 23, 46, 69, 92, 115, 138. Ответ: 23.')
        return (
            '$k$ последовательных чисел содержат $m$ кратных 20 и больше кратных 23.\n\n'
            'а) $23, \\ldots, 92$: кратные 20 — 40, 60, 80; кратные 23 — 23, 46, 69, 92. Ответ: да.\n\n'
            'б) Если кратных 20 ровно 10, то $k\\le11\\cdot20-1=219$, а 11 кратных 23 требуют $k\\ge10\\cdot23+1=231$. Ответ: нет.\n\n'
            'в) $m+1$ кратных 23 требуют $k\\ge23m+1$, а $m$ кратных 20 — $k\\le20(m+1)-1$: $3m\\le18$, $m\\le6$, $k\\le139$. Пример: $161, \\ldots, 299$ — '
            'кратные 20: $180, \\ldots, 280$ (шесть), кратные 23: $161, 184, \\ldots, 299$ (семь). Ответ: 139.')


class BoysLetters(Puzzle):
    fipi = {'A65127': {}}
    ANS = ans('да', '11', '31')

    def verify_all(self, p):
        ok_a = 5 * 9 + 16 * 2 == 7 * 11
        mins = min(n for n in range(4, 50) for c in range(2, n - 1) if (5 * (n - c) + 16 * c) % n == 0)
        best = max(n for n in range(4, 60) if 16 * (n - 2) + 10 >= n * (n - 1) // 2)
        return ok_a and mins == 11 and best == 31

    def solution(self, p):
        return (
            'Пусть юношей и девушек по $n$, $a$ юношей отправили по 5 писем, $c$ — по 16 ($a+c=n$, $a,c\\ge2$). Письма можно распределять между '
            'девушками произвольно.\n\n'
            'а) $5a+16c=7n=7a+7c$, $2a=9c$: $a=9$, $c=2$, $n=11$, писем 77 — по 7 каждой. Ответ: да.\n\n'
            'б) Писем $5n+11c$, нужно $n\\mid11c$. При $n\\le10$ это значит $n\\mid c$, но $2\\le c\\le n-2$. При $n=11$ подходит любое $c$, например '
            '$c=2$, $a=9$ — по 7 писем. Ответ: 11.\n\n'
            'в) Девушки получили $0, 1, \\ldots$ — попарно различные количества, всего не меньше $\\frac{n(n-1)}{2}$ писем; писем не больше '
            '$5\\cdot2+16(n-2)=16n-22$. $\\frac{n(n-1)}{2}\\le16n-22$, $n^2-33n+44\\le0$, $n\\le31$. При $n=31$: 474 письма, девушкам по $0, 1, \\ldots, 29$ '
            'и последней 39. Ответ: 31.')


class PairMoves(Puzzle):
    fipi = {'6948DB': {}}
    ANS = ans('нет', '388', '187')

    def verify_all(self, p):
        seen = {(5, 7): 0}
        q = deque([(5, 7)])
        while q:
            a, b = q.popleft()
            for na, nb in ((a + 2, b - 1), (a - 1, b + 2)):
                if na > 0 and nb > 0 and na <= 100 and nb <= 100 and (na, nb) not in seen:
                    seen[(na, nb)] = seen[(a, b)] + 1
                    q.append((na, nb))
        best = max(a + b - 12 for a, b in seen)
        return best == 187

    def solution(self, p):
        return (
            'Каждый ход увеличивает сумму чисел на 1; после $k$ ходов сумма $12+k$.\n\n'
            'а) После 50 ходов сумма 62, и одно число не может быть равно 100. Ответ: нет.\n\n'
            'б) Сумма 400 — после $400-12=388$ ходов. Ответ: 388.\n\n'
            'в) Разность $a-b$ меняется на $\\pm3$, поэтому $a-b\\equiv5-7\\equiv1\\pmod3$; пара $(100;100)$ невозможна, наибольшая сумма — 199 '
            '(пара $(100;99)$), то есть не больше 187 ходов. Пример: 93 раза подряд делаем пару ходов «$(+2;-1)$, $(-1;+2)$» — получаем $(98;100)$, '
            'затем ход $(+2;-1)$: $(100;99)$; все промежуточные числа не больше 100. Ответ: 187.')


class DigitProducts(Puzzle):
    fipi = {'4A9559': {}}
    ANS = ans('да', 'нет', 'да')

    def verify_all(self, p):
        prods = sorted({a * b for a in range(10) for b in range(10)})
        first = sorted({a * b for a in range(1, 10) for b in range(1, 10)})
        three = {x + y + z for x in first for y in prods for z in prods}
        four = {x + y + z + w for x in first for y in prods for z in prods for w in prods}
        s = set(first)
        for _ in range(4):
            s = {u + v for u in s for v in prods}
        return 200 in three and 320 not in four and all(k in s for k in range(1, 341))

    def solution(self, p):
        return (
            'а) $A=977$, $B=998$: $9\\cdot9+7\\cdot9+7\\cdot8=81+63+56=200$. Ответ: да.\n\n'
            'б) Наибольшее произведение цифр 81, $4\\cdot81=324$; нужно «недобрать» ровно 4, но произведения цифр, меньшие 81, не больше 72 '
            '(80, 79, … 73 не являются произведениями двух цифр). Значит, сумма либо 324, либо не больше $3\\cdot81+72=315$. Ответ: нет.\n\n'
            'в) Каждое число от 0 до 80 — сумма двух произведений цифр (например, $79=72+7$, $77=72+5$, $71=63+8$ и т. д.), а числа от 82 до 97 — '
            'тоже ($92=64+28$, $94=54+40$, остальные — $81+$ произведение). Число $n\\le340$ запишем как $81t+m$: при $n<243$ возьмём $t=\\left[\\frac n{81}\\right]$ '
            'и $m<81$, при $243\\le n\\le340$ — $t=3$ и $m=n-243\\le97$. Слагаемые 81 ставим первыми (ведущие цифры $9\\cdot9$), $m$ раскладываем на два '
            'произведения, остальные места заполняем нулями; при $t=0$ первым ставим ненулевое произведение. Ответ: да.')


class FoursNines(Puzzle):
    fipi = {'6E32AD': {}}
    ANS = ans('да', 'нет', '9')

    def verify_all(self, p):
        nums = sorted({int(''.join(d)) for L in range(1, 4) for d in itertools.product('49', repeat=L)})
        small = [n for n in nums if n <= 289]
        sums = {0}
        for n in small:
            sums |= {s + n for s in sums}
        ex = [9, 49, 99, 444, 449, 494, 499, 949, 994]
        four_max = sum(sorted(nums)[-4:])
        return 107 in sums and 289 not in sums and sum(ex) == 3986 and len(set(ex)) == 9 and four_max < 3986

    def solution(self, p):
        return (
            'а) $4+9+94=107$. Ответ: да.\n\n'
            'б) Числа, не большие 289: 4, 9, 44, 49, 94, 99, их сумма 299. Получить 289 — значит не взять числа с суммой 10, а таких нет. Ответ: нет.\n\n'
            'в) Пусть чисел $n$, из них $a$ оканчиваются на 4: последняя цифра суммы — последняя цифра $9n-5a$, она равна 6. По модулю 5: $9n\\equiv1$, '
            '$n\\equiv4\\pmod5$. Четырёх чисел мало: наибольшая сумма $999+994+949+944=3886<3986$. Значит, $n\\ge9$. Пример: '
            '$9+49+99+444+449+494+499+949+994=3986$. Ответ: 9.')


class RedGreen(Puzzle):
    fipi = {'002FC3': {}}
    ANS = ans('да', 'нет', '6')

    def verify_all(self, p):
        ok_a = 3 * sum(range(1, 30)) + 21 < 1395
        ok_b = 3 * sum(range(1, 30)) + 7 > 1067
        def fmin(r):
            return 3 * (30 - r) * (31 - r) // 2 + 7 * r * (r + 1) // 2
        feasible = [r for r in range(31) if fmin(r) <= 1067]
        green = [3 * i for i in range(1, 24)] + [78]
        red = [7, 14, 21, 28, 35, 56]
        return ok_a and ok_b and min(feasible) == 6 and sum(green) + sum(red) == 1067 and len(set(green)) == 24 and len(set(red)) == 6

    def solution(self, p):
        return (
            'а) Если все числа кратны 3, красные кратны 21. 29 зелёных $3, 6, \\ldots, 87$ и одно красное 21: $1305+21=1326<1395$. Ответ: да.\n\n'
            'б) 29 различных зелёных чисел дают не меньше $3(1+\\ldots+29)=1305>1067$. Ответ: нет.\n\n'
            'в) При $r$ красных наименьшая сумма $3\\cdot\\frac{(30-r)(31-r)}{2}+7\\cdot\\frac{r(r+1)}{2}$: при $r=5$ это 1080, при $r\\le4$ — больше. '
            'При $r=6$: 1047. Пример: зелёные $3, 6, \\ldots, 69, 78$ (сумма 906), красные $7, 14, 21, 28, 35, 56$ (сумма 161): всего 1067. Ответ: 6.')


class Coins25(Puzzle):
    fipi = {'C009C4': {}}
    ANS = ans('да', 'нет', '3')

    def verify_all(self, p):
        reach = {2 * a + 5 * b for a in range(17) for b in range(30)}
        def full(m):
            return all(any((s - j) in reach for j in range(0, m + 1) if s - j >= 0) for s in range(1, 181))
        return 175 in reach and 176 not in reach and min(m for m in range(10) if full(m)) == 3

    def solution(self, p):
        return (
            'Всего $16\\cdot2+29\\cdot5=177$ рублей.\n\n'
            'а) Все монеты, кроме одной двухрублёвой: 175. Ответ: да.\n\n'
            'б) $176=2a+5b$: $b$ чётно, $b\\le28$, тогда $2a\\ge36$, $a\\ge18>16$. Ответ: нет.\n\n'
            'в) Нужно не меньше трёх рублёвых монет: иначе не набрать 180 ($177+2<180$). Трёх достаточно: двухрублёвыми и пятирублёвыми набираются '
            'все суммы от 0 до 177, кроме 1, 3, 174, 176; эти суммы и суммы 178, 179, 180 получаются добавлением одной–трёх рублёвых монет '
            '(например, $174=172+2$, $172=177-5$). Ответ: 3.')


class PhotosDays(Puzzle):
    fipi = {'37B190': {}}
    ANS = ans('да', 'нет', '1430')

    def verify_all(self, p):
        best = 0
        for k in range(2, 1002):
            if 1001 % k:
                continue
            d = 1001 // k
            for m in range(1, 40):
                if m + k - 1 < 40:
                    nat = k * (m + d) + k * (k - 1) // 2
                    best = max(best, nat)
        return 1001 % 7 == 0 and 1001 % 8 != 0 and best == 1430

    def solution(self, p):
        return (
            'Пусть фотографировали $k>1$ дней. Наташа каждый день делала на $n-m$ фотографий больше, разность итогов $k(n-m)=1001=7\\cdot11\\cdot13$.\n\n'
            'а) $k=7$, $n-m=143$, например $m=1$, $n=144$. Ответ: да.\n\nб) 1001 не делится на 8. Ответ: нет.\n\n'
            'в) Наташа сделала $kn+\\frac{k(k-1)}{2}=km+1001+\\frac{k(k-1)}{2}$. Условие $m+k-1<40$ оставляет $k\\in\\{7;11;13\\}$ и $m\\le40-k$. '
            'Значения: $k=7$ — 1253, $k=11$ — 1375, $k=13$, $m=27$, $n=104$ — $351+1001+78=1430$. Ответ: 1430.')


class CircleDifferences(Puzzle):
    fipi = {'5066E8': {}}
    ANS = 'а) например, $6, 4, 10, 12, 9, 11, 7, 8, 3, 2, 1, 5$; б) нет; в) 72'

    def verify_all(self, p):
        ex = [6, 4, 10, 12, 9, 11, 7, 8, 3, 2, 1, 5]
        best = [1, 12, 2, 11, 3, 10, 4, 9, 5, 8, 6, 7]
        s = lambda c: sum(abs(c[i] - c[(i + 1) % 12]) for i in range(12))  # noqa: E731
        return s(ex) == 32 and s(best) == 72 and sorted(ex) == list(range(1, 13))

    def solution(self, p):
        return (
            'а) $6, 4, 10, 12, 9, 11, 7, 8, 3, 2, 1, 5$: модули разностей $2, 6, 2, 3, 2, 4, 1, 5, 1, 1, 4, 1$, сумма 32.\n\n'
            'б) $|a-b|\\equiv a-b\\pmod2$, и сумма всех разностей по кругу равна 0, поэтому сумма модулей чётна. Ответ: нет.\n\n'
            'в) Каждое число входит в две разности, со знаком «+» или «−». В сумме $2\\cdot12$ слагаемых-чисел, из них ровно 12 со знаком «+»; '
            'сумма не больше $2(7+8+\\ldots+12)-2(1+\\ldots+6)=114-42=72$. Пример: $1, 12, 2, 11, 3, 10, 4, 9, 5, 8, 6, 7$ — сумма 72. Ответ: 72.')


class DaysSums(Puzzle):
    VARIANTS = {
        'A0A7EB': dict(ans=ans('да', 'да', '34'), first=5),
        'C690EB': dict(ans=ans('да', 'да', '48'), first=6),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    def verify_all(self, p):
        first = self.VARIANTS[p['kind']]['first']
        best = 0

        def go(c, s, total):
            nonlocal best
            best = max(best, total)
            for c2 in range(1, c):
                for s2 in range(s + 1, 5 * c2 + 1):
                    if s2 >= c2:
                        go(c2, s2, total + s2)
        for c1 in range(1, first + 1):
            go(c1, first, first)
        ex_b = ((26, 51), (25, 113), (24, 114), (23, 115)) if p['kind'] == 'A0A7EB' else ((13, 38), (12, 48), (11, 49), (10, 50))
        thr = 2 if p['kind'] == 'A0A7EB' else 3
        ok_b = (ex_b[0][1] < thr * ex_b[0][0] and sum(s for c, s in ex_b) > 4 * sum(c for c, s in ex_b)
                and all(c <= s <= 5 * c for c, s in ex_b)
                and all(ex_b[i][0] > ex_b[i + 1][0] and ex_b[i][1] < ex_b[i + 1][1] for i in range(3)))
        return ok_b and best == (34 if p['kind'] == 'A0A7EB' else 48)

    def solution(self, p):
        if p['kind'] == 'A0A7EB':
            a = ('а) Пример на 7 дней: количества $9, 8, \\ldots, 3$, суммы $9, 10, \\ldots, 15$ (в первый день девять единиц, в последний — '
                 'три пятёрки). Ответ: да.\n\n')
            b = ('б) Пример: четыре дня, количества 26, 25, 24, 23 и суммы 51, 113, 114, 115 (в первый день 25 единиц и одна двойка — среднее '
                 '$\\frac{51}{26}<2$). Всего $\\frac{393}{98}>4$. Ответ: да.\n\n')
            c = ('в) В первый день сумма 5, чисел не больше 5. Пусть дней хотя бы три: в $i$-й день сумма не больше $5c_i$, и суммы возрастают, '
                 'а количества убывают. Если $c_1=5$, $c_2=4$, $c_3=3$: $s_3\\le15$, $s_2\\le14$ — всего $5+14+15=34$; четвёртого дня быть не может '
                 '($s_4\\le10<s_3$, если $s_3>10$, а при меньших суммах итог меньше). Другие варианты дают меньше (например, $5+20=25$ за два дня). Ответ: 34.')
        else:
            a = ('а) Пример на 7 дней (больше пяти): количества $9, 8, \\ldots, 3$, суммы $9, 10, \\ldots, 15$. Ответ: да.\n\n')
            b = ('б) Пример: количества 13, 12, 11, 10 и суммы 38, 48, 49, 50 (первый день: 12 троек и двойка, среднее $\\frac{38}{13}<3$). '
                 'Всего $\\frac{185}{46}>4$. Ответ: да.\n\n')
            c = ('в) В первый день сумма 6, чисел не больше 6. Лучший вариант: количества 6, 5, 4, 3 и суммы 6, 13, 14, 15 — всего 48 (последний день '
                 'не больше $5\\cdot3=15$, предыдущие суммы меньше). Пятый день невозможен без уменьшения сумм ($s_5\\le10$), а меньшее число дней '
                 'даёт меньше ($6+19+20=45$, $6+25=31$). Ответ: 48.')
        return ('Пусть в $i$-й день записано $c_i$ чисел с суммой $s_i$: $c_i\\le s_i\\le5c_i$, $c_1>c_2>\\ldots$, $s_1<s_2<\\ldots$.\n\n' + a + b + c)


class Digits45(Puzzle):
    fipi = {'CFEFEF': {}}
    ANS = ans('да', 'нет', '10035')

    def verify_all(self, p):
        sums = set()
        for perm in itertools.permutations('0123579'):
            a, b = ''.join(perm[:4]), ''.join(perm[4:])
            if a[0] != '0' and b[0] != '0' and int(a) % 45 == 0 and int(b) % 45 == 0:
                sums.add(int(a) + int(b))
        return 2205 in sums and 3435 not in sums and max(sums) == 10035

    def solution(self, p):
        return (
            'Числа кратны 5 и 9: одно оканчивается на 0, другое на 5, сумма цифр каждого делится на 9. Сумма всех цифр 27, так что суммы цифр '
            'чисел — 9 и 18.\n\n'
            'а) $1935+270=2205$. Ответ: да.\n\n'
            'б) Если четырёхзначное оканчивается на 0: его остальные цифры из $\\{1,2,3,7,9\\}$ с суммой 9 или 18 — только $\\{2,7,9\\}$, трёхзначное — '
            'из $\\{1,3,5\\}$: суммы $2790+135$, $2790+315$, $2970+135$, $2970+315$, $7290+\\ldots$ — 3435 среди них нет (при первой цифре 2 сумма меньше '
            '3300, при 7 и 9 — больше 7000). Если оканчивается на 5: остальные цифры $\\{1,3,9\\}$, трёхзначное из $\\{2,7,0\\}$; при первой цифре 3 '
            'суммы $3195+270=3465$, $3195+720=3915$, $3915+\\ldots>3435$. Ответ: нет.\n\n'
            'в) Наибольшее четырёхзначное: $9720$ (из $\\{2,7,9,0\\}$) с $315$ или $9315$ (из $\\{1,3,9,5\\}$) с $720$ — оба варианта дают 10035. Ответ: 10035.')


class TwoNumbersDigitSum(Puzzle):
    fipi = {'c794eA': {}}
    ANS = ans('да', 'нет', '231')

    @staticmethod
    def ds(n):
        return sum(map(int, str(n)))

    def verify_all(self, p):
        ok_a = self.ds(18) == self.ds(2025)
        ok_b = not any(self.ds(a) == self.ds(599 - a) for a in range(1, 599) if a != 599 - a)
        best = min(sum(sorted(n for n in range(1, 2000) if self.ds(n) == t)[:7]) for t in range(1, 28)
                   if len([n for n in range(1, 2000) if self.ds(n) == t]) >= 7)
        return ok_a and ok_b and best == 231

    def solution(self, p):
        return (
            'а) $18+2025=2043$, суммы цифр $9$ и $9$. Ответ: да.\n\n'
            'б) При сложении $a+b=599$ столбиком: в разряде единиц $a_0+b_0\\le18<19$, поэтому переноса нет и $a_0+b_0=9$; аналогично в разряде десятков. '
            'Значит, $s(a)+s(b)=s(599)=23$ — нечётное число, равных сумм цифр быть не может. Ответ: нет.\n\n'
            'в) Числа с равной суммой цифр $t$: сумма семи наименьших. $t=6$: $6+15+24+33+42+51+60=231$; при $t=5$ — $5+14+23+32+41+50+104=269$, '
            'при $t=7$ — $238$, при $t=8$ — 245, при $t=9$ — 252, при $t\\le4$ и $t\\ge10$ — больше. Ответ: 231.')


class RulerCuts(Puzzle):
    fipi = {'8755EE': {}}
    ANS = ans('да', 'нет', '8')

    def verify_all(self, p):
        def moves(L):
            k = 0
            while (1 << k) < L:
                k += 1
            return k
        return moves(16) == 4 and (1 << 5) < 100 and moves(200) == 8

    def solution(self, p):
        return (
            'За ход каждый кусок разрезается не более чем на два, поэтому после $k$ ходов кусков не больше $2^k$.\n\n'
            'а) Разрезаем пополам: 16 → 8+8 → 4·4 → 2·8 → 1·16. Ответ: да.\n\nб) После пяти ходов кусков не больше 32 < 100. Ответ: нет.\n\n'
            'в) $2^7=128<200$, значит, ходов не меньше 8. Восьми хватает: каждым ходом режем все куски длиннее 1 см почти пополам; после $k$ ходов '
            'длины не больше $\\left\\lceil\\frac{200}{2^k}\\right\\rceil$, после 8 ходов — 1 см. Ответ: 8.')


class StonesTwoGroups(Puzzle):
    fipi = {'0FB969': {}}
    ANS = ans('да', 'нет', '6')

    def verify_all(self, p):
        diffs = {abs(226 - 2 * (7 * a + 22 * b)) for a in range(5) for b in range(10)}
        return 8 in diffs and 0 not in diffs and min(d for d in diffs if d > 0) == 6

    def solution(self, p):
        return (
            'Общая масса $4\\cdot7+9\\cdot22=226$. Если в одной группе $a$ камней по 7 т и $b$ по 22 т, разность масс $|226-2(7a+22b)|$.\n\n'
            'а) $a=1$, $b=5$: $117$ и $109$. Ответ: да.\n\n'
            'б) Нужно $7a+22b=113$ при $a\\le4$, $b\\le9$: перебор $b=0,\\ldots,5$ даёт остатки $113, 91, 69, 47, 25, 3$, ни один не равен $7a$ с $a\\le4$. Ответ: нет.\n\n'
            'в) Разность чётна. Разности 2 и 4 требуют $7a+22b\\in\\{112;114;111;115\\}$ — перебором так же убеждаемся, что это невозможно. Разность 6: '
            '$7a+22b=110$ при $b=5$, $a=0$. Ответ: 6.')


class FractionMoves(Puzzle):
    fipi = {'7F366B': {}}
    ANS = ans('да', 'нет', '$\\frac57$')

    def verify_all(self, p):
        def step(f):
            return Fraction(f.numerator + f.denominator, 2 * f.numerator + f.denominator)
        ok_a = step(step(step(Fraction(1, 3)))) == Fraction(22, 31)
        props = [Fraction(a, b) for b in range(2, 120) for a in range(1, b) if Fraction(a, b).denominator == b]
        two = {step(step(f)) for f in props}
        ok_b = Fraction(7, 12) not in two
        cands = sorted(f for f in (Fraction(c, d) for d in range(2, 60) for c in range(1, d)) if f > Fraction(7, 10))
        first_bad = next(f for f in cands if f not in two and not (Fraction(2, 3) < f < Fraction(5, 7)))
        return ok_a and ok_b and first_bad == Fraction(5, 7) and all(f in two for f in cands if f < Fraction(5, 7) and f.denominator < 30)

    def solution(self, p):
        return (
            'Ход $\\frac ab\\to\\frac{a+b}{2a+b}$; $\\gcd(a+b,2a+b)=\\gcd(a+b,a)=\\gcd(a,b)=1$ — несократимость сохраняется. Обратно: дробь $\\frac cd$ '
            'получается из $\\frac{d-c}{2c-d}$, и эта дробь правильная и положительная при $\\frac23<\\frac cd<1$.\n\n'
            'а) $\\frac13\\to\\frac45\\to\\frac9{13}\\to\\frac{22}{31}$. Ответ: да.\n\n'
            'б) Предыдущей для $\\frac7{12}$ была бы $\\frac{5}{2}$ — не правильная дробь ($\\frac7{12}<\\frac23$). Ответ: нет.\n\n'
            'в) За два хода получается $\\frac cd$, если и она, и её предшественница $\\frac{d-c}{2c-d}$ больше $\\frac23$: $3(d-c)>2(2c-d)$, то есть '
            '$\\frac cd<\\frac57$. Значит, получаются ровно дроби из $\\left(\\frac23;\\frac57\\right)$. Все дроби из $\\left(0{,}7;\\frac57\\right)$ получаются, '
            'а $\\frac57$ — нет (её предшественница $\\frac23$, а предшественница $\\frac23$ — $\\frac11$). Ответ: $\\frac57$.')


class DeleteDigitProduct(Puzzle):
    fipi = {'724631': {}}
    ANS = ans('да', 'нет', '910')

    def verify_all(self, p):
        good = []
        for A in range(100, 1000):
            s = str(A)
            dels = {int(s[:i] + s[i + 1:]) for i in range(3) if (s[:i] + s[i + 1:])[0] != '0'}
            if any(B * C == A for B in dels for C in dels):
                good.append(A)
        return any(A > 150 for A in good) and not any(540 <= A < 600 for A in good) and max(good) == 910

    def solution(self, p):
        return (
            'а) $A=160$: вычёркиваем 0 — $B=16$, вычёркиваем 6 — $C=10$, $16\\cdot10=160$. Ответ: да.\n\n'
            'б) $A=\\overline{5xy}$. Двузначные числа из него: $\\overline{xy}$ (если $x\\ne0$), $\\overline{5y}$, $\\overline{5x}$. Если оба множителя начинаются '
            'с 5, произведение не меньше 2500. Если один — $\\overline{xy}$, а другой не меньше 50, то $\\overline{xy}\\le\\frac{600}{50}=12$, $A\\le512<540$. '
            'Если оба $\\overline{xy}$: $\\overline{xy}^2=500+\\overline{xy}$ — целых решений нет. Ответ: нет.\n\n'
            'в) Пусть $A\\ge911$, тогда $A=\\overline{9bc}$. Два множителя, начинающихся с 9, дают больше 8000; если один из них $\\overline{bc}$, а '
            'другой не меньше 90, то $\\overline{bc}\\le11$, $A\\in\\{910;911\\}$, и 911 не подходит; квадрат $\\overline{bc}^2=900+\\overline{bc}$ невозможен. '
            '$A=910=91\\cdot10$ подходит. Ответ: 910.')


class PairSumDiff(Puzzle):
    fipi = {'12AE34': {}}
    ANS = ans('да', 'нет', '403')

    def verify_all(self, p):
        def orbit(a, b, n=20):
            out = [(a, b)]
            for _ in range(n):
                a, b = a + b, a - b
                out.append((a, b))
            return out
        ok_a = any(x == 400 for x, y in orbit(100, 1))
        ok_b = (806, 788) not in orbit(100, 1, 30)
        starts = [(a, b) for a in range(2, 806) for b in range(1, a) if (806, 788) in orbit(a, b, 6)]
        return ok_a and ok_b and min(a for a, b in starts) == 403

    def solution(self, p):
        return (
            'Ход $(a;b)\\to(a+b;a-b)$; два хода подряд дают $(2a;2b)$.\n\n'
            'а) $(100;1)\\to(101;99)\\to(200;2)\\to(202;198)\\to(400;4)$. Ответ: да.\n\n'
            'б) Из $(100;1)$ получаются только пары $2^k(100;1)$ и $2^k(101;99)$. $806=2\\cdot403$ не имеет вид $2^k\\cdot100$ или $2^k\\cdot101$. Ответ: нет.\n\n'
            'в) Обратный ход: $(x;y)\\to\\left(\\frac{x+y}{2};\\frac{x-y}{2}\\right)$. Из $(806;788)$: $(797;9)$, затем $(403;394)$, а дальше $\\frac{797}{2}$ — '
            'не целое. Возможные начальные пары: $(806;788)$, $(797;9)$, $(403;394)$; наименьшее $a=403$. Ответ: 403.')


class PairOperation(Puzzle):
    fipi = {'2DC181': {}}
    ANS = ans('да', 'да', '3')

    def verify_all(self, p):
        img = {(3 * a + b, 3 * b - a) for a in range(-40, 41) for b in range(-40, 41)}
        ok_a = (5, 5) in img
        ok_b = all((-d, c) in img for c, d in img if abs(c) < 20 and abs(d) < 20)
        best = min(abs(c - 9) + abs(d - 2) for c, d in img)
        return ok_a and ok_b and best == 3

    def solution(self, p):
        return (
            'а) Из $(1;2)$: $(3+2;6-1)=(5;5)$. Ответ: да.\n\n'
            'б) Если $(c;d)=(3a+b;3b-a)$, то из пары $(-b;a)$ получаем $(-3b+a;3a+b)=(-d;c)$. Ответ: да.\n\n'
            'в) $(c;d)$ получается тогда и только тогда, когда $a=\\frac{3c-d}{10}$ и $b=\\frac{c+3d}{10}$ целые, то есть $d\\equiv3c\\pmod{10}$ '
            '(тогда и $c+3d\\equiv10c\\equiv0$). Для $(9;2)$: $27\\equiv7\\ne2$. Перебор пар на расстоянии 1 и 2 от $(9;2)$ показывает, что условие '
            'не выполняется; на расстоянии 3 подходит $(8;4)$ — из пары $(2;2)$. Ответ: 3.')


class DigitSumOperation(Puzzle):
    fipi = {'9BC08F': {}}
    ANS = ans('да', 'нет', '51')

    def verify_all(self, p):
        res = {(n - sum(map(int, str(n)))) // 3 for n in range(100, 1000)}
        r2 = {(n - sum(map(int, str(n)))) // 3 for n in range(100, 601)}
        return 300 in res and 151 not in res and len(r2) == 51

    def solution(self, p):
        return (
            'Для $\\overline{abc}$: $\\frac{100a+10b+c-(a+b+c)}{3}=33a+3b$.\n\n'
            'а) $33a+3b=300$: $11a+b=100$, $a=9$, $b=1$; например, $910$. Ответ: да.\n\nб) $33a+3b$ делится на 3, а 151 — нет. Ответ: нет.\n\n'
            'в) Для $a=1,\\ldots,5$ значения $33a+3b$, $b=0,\\ldots,9$, попадают в непересекающиеся отрезки $[33a;33a+27]$ — по 10 значений; '
            'число 600 даёт ещё одно ($198$). Всего 51. Ответ: 51.')


class CardsColors(Puzzle):
    """Синие и красные карточки"""
    VARIANTS = {
        '6e44FB': dict(mb=3, mr=2, f=2, L=72, ans=ans('да', 'нет', '144')),
        'F37F75': dict(mb=3, mr=2, f=2, L=36, ans=ans('да', 'нет', '27')),
        '6FF25e': dict(mb=3, mr=2, f=2, L=60, ans=ans('да', 'нет', '75')),
        'A87FAB': dict(mb=5, mr=3, f=3, L=45, ans=ans('да', 'нет', '30')),
        'e8AA65': dict(mb=5, mr=2, f=2, L=120, ans=ans('да', 'нет', '150')),
    }
    fipi = {k: dict(kind=k) for k in VARIANTS}

    def answer(self, p):
        return Answer(self.VARIANTS[p['kind']]['ans'], 0)

    @staticmethod
    def count_mult(m, L, top):
        """Сколько чисел, кратных m, в промежутке (−L; top]"""
        return top // m - (-L) // m

    def feasible(self, d, B, R):
        mb, mr, f, L = d['mb'], d['mr'], d['f'], d['L']
        if R % mb or (f * B) % mr:
            return False
        return B <= self.count_mult(mb, L, R) and R <= self.count_mult(mr, L, f * B)

    def verify_all(self, p):
        d = self.VARIANTS[p['kind']]
        pairs = [(B, R) for B in range(1, 400) for R in range(1, 400) if self.feasible(d, B, R)]
        k = p['kind']
        if k == '6e44FB':
            return any(B + R == 4 for B, R in pairs) and not any(R == B + 60 for B, R in pairs) and max(B + R for B, R in pairs) == 144
        if k == 'F37F75':
            return any(B == 1 for B, R in pairs) and not any(B == 50 for B, R in pairs) and max(B for B, R in pairs) == 27
        if k == '6FF25e':
            return any(R == 3 for B, R in pairs) and not any(R == 150 for B, R in pairs) and max(R for B, R in pairs) == 75
        if k == 'A87FAB':
            return any(R == 5 for B, R in pairs) and not any(R == 100 for B, R in pairs) and max(R for B, R in pairs) == 30
        return any(B + R == 6 for B, R in pairs) and not any(R == B + 90 for B, R in pairs) and max(B + R for B, R in pairs) == 150

    def solution(self, p):
        d = self.VARIANTS[p['kind']]
        mb, mr, f, L = d['mb'], d['mr'], d['f'], d['L']
        word_b = {3: 'кратные 3', 5: 'кратные 5'}[mb]
        word_r = {2: 'чётные', 3: 'кратные 3'}[mr]
        # числа, кратные m, в (−L; t]
        cb = lambda t: f'\\frac{{R+{L - (L % mb if L % mb else mb)}}}{{{mb}}}+1'  # noqa: E731
        lowb = -(L - 1) // mb * mb if False else None
        first_b = next(v for v in range(-L + 1, 1) if v % mb == 0)
        first_r = next(v for v in range(-L + 1, 1) if v % mr == 0)
        nb = f'\\frac{{R+{-first_b}}}{{{mb}}}+1'
        nr = f'\\frac{{{f}B+{-first_r}}}{{{mr}}}+1'
        intro = (f'Пусть синих карточек $B$, красных $R$. Наибольшее красное число ${f}B$, наибольшее синее число $R$ — значит, $R$ кратно {mb}. '
                 f'Синие числа — различные {word_b} из промежутка $(-{L};R]$, их не больше ${nb}$; красные — различные {word_r} из $(-{L};{f}B]$, '
                 f'их не больше ${nr}$.\n\n')
        k = p['kind']
        bmax = lambda R: (R - first_b) // mb + 1  # noqa: E731
        rmax = lambda B: (f * B - first_r) // mr + 1  # noqa: E731
        if k in ('6e44FB', 'e8AA65'):
            n4 = 4 if k == '6e44FB' else 6
            R0 = n4 - 1
            ex = (f'а) $B=1$, $R={R0}$: синее число ${R0}$, красные — {", ".join(str(f - mr * i).replace("-", "−") for i in range(R0))}. Ответ: да.\n\n')
            diff = 60 if k == '6e44FB' else 90
            b = (f'б) $R\\le{nr}=B+{rmax(0)}$, а нужно $R=B+{diff}$. Ответ: нет.\n\n')
            Rm = max(R for R in range(mb, 1000, mb) if R <= rmax(bmax(R)))
            Bm = bmax(Rm)
            c = (f'в) Из $B\\le{nb}$ и $R\\le B+{rmax(0)}$: $R\\le\\frac{{R}}{{{mb}}}+{bmax(0) + rmax(0)}$ (с учётом целочисленности), откуда '
                 f'$R\\le{Rm}$, и $B\\le{Bm}$. Пример: синие — все {word_b} от ${first_b}$ до ${Rm}$ (их ${Bm}$), красные — все {word_r} от ${first_r}$ '
                 f'до ${f * Bm}$ (их ${rmax(Bm)}$). Всего карточек: ${Bm + Rm}$. Ответ: {Bm + Rm}.')
            return intro + ex + b + c
        if k == 'F37F75':
            ex = 'а) $B=1$, $R=3$: синее 3, красные 2, 0, −2. Ответ: да.\n\n'
            b = f'б) При $B=50$ нужно $R\\ge{mb}(50-{bmax(0)})$, а $R\\le B+{rmax(0)}={50 + rmax(0)}$. Ответ: нет.\n\n'
            Bm = max(B for B in range(1, 500) if any(self.feasible(d, B, R) for R in range(1, 500)))
            Rm = max(R for R in range(1, 500) if self.feasible(d, Bm, R))
            c = (f'в) $B\\le{nb}$ и $R\\le B+{rmax(0)}$ дают $B\\le\\frac{{B+{rmax(0)}}}{{{mb}}}+{bmax(0)}$, $B\\le{Bm}$. Пример: $B={Bm}$, $R={Rm}$ — '
                 f'синие все {word_b} от ${first_b}$ до ${Rm}$, красные все {word_r} от ${first_r}$ до ${f * Bm}$. Ответ: {Bm}.')
            return intro + ex + b + c
        # 6FF25e, A87FAB — наибольшее R
        R1 = 3 if k == '6FF25e' else 5
        ex = (f'а) $B=1$, $R={R1}$: синее ${R1}$, красные — {", ".join(str(f - mr * i).replace("-", "−") for i in range(R1))}. Ответ: да.\n\n')
        R2 = 150 if k == '6FF25e' else 100
        b = f'б) При $R={R2}$: $B\\ge R-{rmax(0)}={R2 - rmax(0)}$, но $B\\le{nb}={bmax(R2)}$. Ответ: нет.\n\n'
        Rm = max(R for R in range(1, 500) if any(self.feasible(d, B, R) for B in range(1, 500)))
        Bm = min(B for B in range(1, 500) if self.feasible(d, B, Rm))
        c = (f'в) $R\\le B+{rmax(0)}$ и $B\\le{nb}$ дают $R\\le\\frac{{R}}{{{mb}}}+{rmax(0) + bmax(0)}$, $R\\le{Rm}$. Пример: $R={Rm}$, $B={Bm}$ — '
             f'синие все {word_b} от ${first_b}$ до ${Rm}$, красные все {word_r} от ${first_r}$ до ${f * Bm}$. Ответ: {Rm}.')
        return intro + ex + b + c


class CoinsQuarter(Puzzle):
    fipi = {'B3c1B7': {}}
    ANS = ans('да', 'нет', '977')

    def verify_all(self, p):
        def ok(N):
            total = 2 * N + 5 * (1200 - N)
            small = 2 * min(N, 500) + 5 * max(0, 500 - N)
            return 4 * small >= total
        return ok(400) and not ok(600) and sum(1 for N in range(1, 1200) if ok(N)) == 977

    def solution(self, p):
        return (
            'Общая сумма $2N+5(1200-N)=6000-3N$. Условие достаточно проверить для 500 самых «дешёвых» монет.\n\n'
            'Если $N\\ge500$: 500 двухрублёвых дают 1000, нужно $1000\\ge\\frac{6000-3N}{4}$, $N\\ge667$. Если $N<500$: $2N+5(500-N)=2500-3N\\ge\\frac{6000-3N}{4}$, '
            '$N\\le444$.\n\n'
            'а) $N=400\\le444$. Ответ: да.\n\nб) $N=600$: $1000<1050$. Ответ: нет.\n\n'
            'в) $N\\in[1;444]\\cup[667;1199]$ — $444+533=977$ значений. Ответ: 977.')


class FruitsMass(Puzzle):
    fipi = {'85FA27': {}}
    ANS = ans('нет', 'нет', '465')

    def verify_all(self, p):
        sols = [(x, y, 87 - x - y) for x in range(88) for y in range(88 - x) if 94 * x + 127 * y + 100 * (87 - x - y) == 8700 and (x or y)]
        ok_a = not any(x == y and x > 0 for x, y, z in sols)
        ok_b = not any(z < 9 for x, y, z in sols)
        best = max(127 * y - 101 * (y - 1) for x, y, z in sols if y > 0)
        return ok_a and ok_b and best == 465

    def solution(self, p):
        return (
            'Пусть фруктов легче 100 г — $x$, тяжелее — $y$, ровно 100 г — $z$: $x+y+z=87$, $94x+127y+100z=8700$. Отсюда $27y=6x$, $x=9t$, $y=2t$, '
            '$z=87-11t$, $t\\ge1$ (есть фрукты разной массы), $t\\le7$.\n\n'
            'а) $9t=2t$ невозможно при $t\\ge1$. Ответ: нет.\n\nб) $z=87-11t\\ge87-77=10$. Ответ: нет.\n\n'
            'в) Тяжёлых фруктов $2t$, их средняя 127 г, каждый не меньше 101 г: самый тяжёлый не больше $254t-101(2t-1)=52t+101\\le465$ (при $t=7$). '
            'Пример: 63 фрукта по 94 г, 10 фруктов по 100 г, 13 фруктов по 101 г и один 465 г: $5922+1000+1313+465=8700$. Ответ: 465.')


class TwoDigitOperations(Puzzle):
    fipi = {'9Fe39A': {}}
    ANS = ans('нет', 'нет', '44')

    def verify_all(self, p):
        ok_a = all((15 * a - 18 * b) != 128 for a in range(100) for b in range(100))
        ok_b = not any(15 * a == 18 * b and a + b == 25 for a in range(26) for b in range(26))
        best = max(11 * k for k in range(0, 20) if 15 * 6 * k + 30 * 5 * k < 1198)
        return ok_a and ok_b and best == 44

    def solution(self, p):
        return (
            'Первая операция меняет число на $+20-5=+15$, вторая — на $-20+2=-18$. Пусть их применили к $a$ и $b$ числам.\n\n'
            'а) $15a-18b$ делится на 3, а 128 — нет. Ответ: нет.\n\n'
            'б) $15a=18b$, $5a=6b$: $a=6k$, $b=5k$, всего $11k\\ne25$. Ответ: нет.\n\n'
            'в) Всего чисел $11k$. К первой операции годятся числа с цифрой десятков не больше 7 и единиц не меньше 5 — наименьшее 15; ко второй — '
            'с десятками не меньше 3 и единицами не больше 7 — наименьшее 30. Сумма исходных не меньше $6k\\cdot15+5k\\cdot30=240k<1198$, $k\\le4$. '
            'Пример: 24 числа 15 и 20 чисел 30 (сумма 960). Ответ: 44.')


TEMPLATES = [c() for c in Puzzle.__subclasses__() if c.__module__ == __name__]
EXTRA = []

# Подтемы (фильтр в банке) и сложность 1–4 (1 базовый … 4 «гроб») по семействам
AVERAGES, DIGITS, DIVISIBILITY, PROCESSES, SETS = ('Средние значения и проценты', 'Цифры и десятичная запись',
                                                   'Делимость и остатки', 'Процессы и операции',
                                                   'Наборы чисел: суммы и произведения')
SECTION = {
    AVERAGES: {'Containers': 1, 'GirlsShare': 1, 'CoinsQuarter': 1, 'FruitsMass': 2, 'SchoolsFixedAverage': 2,
               'SchoolsAverages': 3, 'SixSmallestLargest': 3, 'DaysSums': 3},
    DIGITS: {'DigitTensOperation': 1, 'DigitSumOperation': 1, 'EndingDigits': 2, 'Repunits': 2, 'TwoNumbersDigitSum': 2,
             'LastDigitDivision': 3, 'FoursNines': 3, 'Digits45': 3, 'DeleteDigitProduct': 3, 'AppendDigit': 4,
             'DigitProducts': 4},
    DIVISIBILITY: {'PhotosDays': 1, 'RedGreen': 2, 'HundredNumbers': 2, 'ConsecutiveDivisible': 2, 'BoysLetters': 2,
                   'CongruentNumbers': 2, 'CircleResidues': 3},
    PROCESSES: {'RulerCuts': 1, 'PairSumDiff': 1, 'PairMoves': 2, 'PairOperation': 2, 'TwoDigitOperations': 2,
                'StonesBoxes': 3, 'FractionMoves': 3},
    SETS: {'Coins25': 1, 'StonesTwoGroups': 1, 'PairProducts': 3, 'CircleDifferences': 3, 'CardsColors': 3,
           'LuckyTriples': 4},
}
for _t in TEMPLATES:
    _t.topic, _t.difficulty = next((s, d[type(_t).__name__]) for s, d in SECTION.items() if type(_t).__name__ in d)
