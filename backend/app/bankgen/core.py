"""
Каркас шаблонов банка.

Шаблон — один прототип задания ЕГЭ («Найдите корень уравнения log_a(x+b)=c»). Он умеет:

    match(task)   — узнать прототип в условии ФИПИ и достать из него числа (params) или вернуть None;
    solve(p)      — ответ (Fraction / int / str);
    render(p)     — своё условие, решение и рисунки для этих чисел;
    sample(rng)   — новые числа, при которых ответ «красивый»;
    verify(p, a)  — независимая проверка ответа (подстановкой, перебором, численно).

Ответ оригинала дополнительно сверяется с проверкой ФИПИ (app/scripts/fipi/oracle.py),
так что шаблон, который неправильно понял условие, сразу виден.
"""
import math
import random
import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable

Params = dict[str, Any]


@dataclass
class Rendered:
    condition: str                       # Markdown + LaTeX; рисунки — ![](figure://<имя>)
    solution: str
    figures: dict[str, str] = field(default_factory=dict)   # имя → SVG


class Template:
    number: int = 0
    topic: str = ''          # название темы в банке
    code: str = ''           # уникальный код прототипа: '6.log.simple'
    difficulty: int = 1      # 1 базовый, 2 средний, 3 сложный, 4 «гроб»
    detailed: bool = False   # вторая часть: ответ не проверяется автоматически
    patterns: list[str] = []  # регулярки по условию ФИПИ
    variants: bool = True     # умеет ли шаблон делать аналоги с новыми числами

    def match(self, task: dict) -> Params | None:
        text = compact(task['condition'])
        for pattern in self.patterns:
            m = re.search(pattern, text, re.S)
            if m:
                try:
                    params = self.parse(m, task)
                except (ValueError, ZeroDivisionError, KeyError, IndexError):
                    return None
                if params is not None:
                    return params
        return None

    def parse(self, m: re.Match, task: dict) -> Params | None:
        raise NotImplementedError

    def solve(self, p: Params):
        raise NotImplementedError

    def render(self, p: Params) -> Rendered:
        raise NotImplementedError

    def sample(self, rng: random.Random) -> Params:
        raise NotImplementedError

    def verify(self, p: Params, answer) -> bool:
        return True

    def nice(self, answer) -> bool:
        return nice_number(answer)

    def generate(self, rng: random.Random, tries: int | None = None) -> tuple[Params, Any]:
        """Числа с красивым и проверенным ответом"""
        tries = tries or (60 if self.detailed else 2000)  # проверка во второй части дорогая (sympy, численный поиск корней)
        for _ in range(tries):
            try:
                p = self.sample(rng)
                if p is None:
                    continue
                answer = self.solve(p)
            except (ValueError, ZeroDivisionError, OverflowError):
                continue
            if answer is not None and self.nice(answer) and self.verify(p, answer):
                return p, answer
        raise RuntimeError(f'{self.code}: не нашлось чисел с красивым ответом')


# ---------------------------------------------------------------------------
# Числа
# ---------------------------------------------------------------------------

def frac(x) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, float):
        return Fraction(x).limit_denominator(10 ** 9)
    return Fraction(x)


def is_finite_decimal(x: Fraction) -> bool:
    d = x.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def decimals(x: Fraction) -> int:
    n = 0
    while x.denominator != 1:
        x *= 10
        n += 1
        if n > 12:
            break
    return n


def nice_number(answer, max_decimals: int = 2, limit: int = 100000) -> bool:
    """Целое или конечная десятичная дробь с не более чем max_decimals знаками, не огромное"""
    if isinstance(answer, str):
        return True
    x = frac(answer)
    return is_finite_decimal(x) and decimals(x) <= max_decimals and abs(x) <= limit


def dec(x, tex: bool = False) -> str:
    """Fraction → «2,5» (в формуле — «2{,}5»)"""
    x = frac(x)
    if x.denominator == 1:
        s = str(x.numerator)
    elif is_finite_decimal(x):
        n = decimals(x)
        s = f'{float(x):.{n}f}'
    else:
        raise ValueError(f'{x} — бесконечная дробь')
    s = s.replace('.', '{,}' if tex else ',')
    return s


def tex_num(x) -> str:
    """Число для формулы: конечную дробь — десятичной, иначе \\frac"""
    x = frac(x)
    if is_finite_decimal(x):
        return dec(x, tex=True)
    sign = '-' if x < 0 else ''
    return f'{sign}\\frac{{{abs(x.numerator)}}}{{{x.denominator}}}'


def tex_frac(x) -> str:
    """Всегда обыкновенной дробью (для выкладок)"""
    x = frac(x)
    if x.denominator == 1:
        return str(x.numerator)
    sign = '-' if x < 0 else ''
    return f'{sign}\\frac{{{abs(x.numerator)}}}{{{x.denominator}}}'


def answer_json(answer) -> dict:
    """{"accepted": [...], "display": "..."} как ждёт app/services/checker.py"""
    if isinstance(answer, str):
        return {'accepted': [answer], 'display': answer}
    s = dec(answer)
    return {'accepted': [s], 'display': s}


def parse_num(s: str) -> Fraction:
    """«2{,}5», «−3», «2,5», «\\frac{1}{4}» → Fraction"""
    s = s.strip().replace('{,}', '.').replace(',', '.').replace('−', '-').replace(' ', '').replace('\\', '\\')
    s = s.replace('\\ ', '').replace('{', '').replace('}', '') if '\\frac' not in s else s
    m = re.fullmatch(r'(-?)\\frac\{?(\d+)\}?\{?(\d+)\}?', s)
    if m:
        return Fraction(int(m.group(2)), int(m.group(3))) * (-1 if m.group(1) else 1)
    return Fraction(s)


NUM = r'-?\d+(?:\{,\}\d+)?'          # число в формуле ФИПИ: 2{,}5
TNUM = r'-?\d+(?:[.,]\d+)?'          # число в тексте: 2,5


def num(s: str) -> Fraction:
    return parse_num(s)


FUNCS = r'log|ln|lg|sin|cos|tg|ctg|operatorname\{tg\}|operatorname\{ctg\}|sqrt'


def compact(text: str) -> str:
    """
    Условие ФИПИ в форму, удобную для регулярок: внутри $...$ без пробелов, \\left/\\right,
    {\\log }_5 → \\log_5, {(\\frac17)} → (\\frac17), \\text{π} → \\pi, \\operatorname{tg} → \\tg.
    Текст вне формул не трогаем.
    """
    def fix(m: re.Match) -> str:
        s = m.group(1)
        s = s.replace('\\left', '').replace('\\right', '').replace('\\displaystyle', '')
        s = re.sub(r'\\text\{(\d*)π\}', r'\1\\pi', s)
        s = s.replace('\\text{π}', '\\pi').replace('π', '\\pi')
        s = re.sub(r'\\operatorname\{(\w+)\}', r'\\\1', s)
        s = s.replace(' ', '')
        s = re.sub(r'\{\\(log|ln|lg|sin|cos|tg|ctg)\}', r'\\\1', s)
        s = re.sub(r'\{(\([^{}]*\))\}', r'\1', s)                 # {(…)} → (…)
        s = re.sub(r'\{(\\frac\{?\d+\}?\{?\d+\}?)\}', r'\1', s)   # {\frac17} → \frac17
        s = re.sub(r'\\frac(\d)(\d)', r'\\frac{\1}{\2}', s)        # \frac17 → \frac{1}{7}
        s = re.sub(r'\\frac(\d|[a-z])\{', r'\\frac{\1}{', s)
        s = re.sub(r'\\frac\{([^{}]*)\}(\d|[a-z])(?![\w{])', r'\\frac{\1}{\2}', s)
        s = re.sub(r'\{(\d+)\}\^', r'\1^', s)                      # {10}^6 → 10^6
        s = s.replace('\\cdot', '·')
        return '$' + s + '$'
    return re.sub(r'\$([^$]*)\$', fix, text)


def lin_parse(s: str, var: str = 'x') -> tuple[Fraction, Fraction]:
    """'x+4', '-4-x', '2x', '15-x', '3x-4', '-x' → (k, b) для k·x + b"""
    s = s.replace('{,}', '.').replace('−', '-')
    k, b = Fraction(0), Fraction(0)
    for sign, body in re.findall(r'([+-]?)([^+-]+)', s):
        mult = -1 if sign == '-' else 1
        if body.endswith(var):
            c = body[:-1]
            k += mult * (Fraction(c) if c else 1)
        else:
            b += mult * Fraction(body)
    return k, b


def lin(k, b, var: str = 'x') -> str:
    """k·x + b → 'kx+b' в LaTeX ('x-5', '3-x', '-2x+7')"""
    k, b = frac(k), frac(b)
    if k == 0:
        return tex_num(b)
    if k < 0 and b > 0:   # «15-x» привычнее, чем «-x+15»
        return tex_num(b) + coef(k, var)
    return coef(k, var, first=True) + (signed(b) if b else '')


# ---------------------------------------------------------------------------
# Текст
# ---------------------------------------------------------------------------

def signed(x, first: bool = False) -> str:
    """Слагаемое со знаком: signed(3) = '+3', signed(-3) = '-3', first — без плюса"""
    s = tex_num(x)
    if first or s.startswith('-'):
        return s
    return '+' + s


def coef(k, var: str, first: bool = False) -> str:
    """Коэффициент при переменной: 1·x → x, -1·x → -x, 3x → 3x, со знаком для не первого слагаемого"""
    k = frac(k)
    if k == 0:
        return ''
    body = var if abs(k) == 1 else tex_num(abs(k)) + var
    if k < 0:
        return '-' + body
    return body if first else '+' + body


def poly(coefs: list, var: str = 'x') -> str:
    """[a, b, c] → ax^2+bx+c (старшая степень первой)"""
    deg = len(coefs) - 1
    parts = []
    for i, k in enumerate(coefs):
        k = frac(k)
        if k == 0:
            continue
        power = deg - i
        v = '' if power == 0 else var if power == 1 else f'{var}^{{{power}}}' if power > 9 else f'{var}^{power}'
        if power == 0:
            parts.append(signed(k, first=not parts))
        else:
            parts.append(coef(k, v, first=not parts))
    return ''.join(parts) or '0'


def par(x) -> str:
    """Отрицательное число в скобках: для произведений и степеней"""
    s = tex_num(x)
    return f'({s})' if s.startswith('-') else s


def linear_steps(k, b, rhs, var: str = 'x') -> str:
    """kx + b = rhs → «$$kx=rhs-b,\\quad x=…$$» (формула без окружающего текста)"""
    k, b, rhs = frac(k), frac(b), frac(rhs)
    x = (rhs - b) / k
    steps = [f'{lin(k, b, var)}={tex_num(rhs)}']
    if b != 0:
        steps.append(f'{coef(k, var, first=True)}={tex_num(rhs - b)}')
    if k != 1:
        steps.append(f'{var}={tex_num(x)}')
    return '$$' + ',\\quad '.join(steps) + '.$$'


def choice(rng: random.Random, *values):
    return rng.choice(values)


def plural(n: int, one: str, few: str, many: str) -> str:
    n = abs(n) % 100
    if 11 <= n <= 19:
        return many
    n %= 10
    return one if n == 1 else few if 2 <= n <= 4 else many


def close(a, b, eps: float = 1e-9) -> bool:
    return abs(float(a) - float(b)) < eps * max(1.0, abs(float(b)))


def isqrt_exact(n: int) -> int | None:
    if n < 0:
        return None
    r = math.isqrt(n)
    return r if r * r == n else None
