"""
LaTeX → sympy: независимая проверка ответов.

Шаблон считает ответ своей формулой, а здесь выражение из готового условия разбирается заново
и вычисляется sympy. Не сошлось — шаблон ошибся в условии или в решении.

Свой разборщик, а не sympy.parse_latex: в заданиях ЕГЭ пишут \\sin 68^\\circ, \\log_3 162, \\tg\\frac{\\pi}{4},
2\\sqrt{3}\\cos^2\\frac{13\\pi}{12} — аргументы функций без скобок, что стандартный парсер не понимает.
Нужен sympy (requirements-bankgen.txt), рабочий бэкенд его не использует.
"""
import re
from fractions import Fraction

import sympy as sp

FUNCS = {
    'sin': sp.sin, 'cos': sp.cos, 'tg': sp.tan, 'tan': sp.tan, 'ctg': sp.cot, 'cot': sp.cot,
    'arcsin': sp.asin, 'arccos': sp.acos, 'arctg': sp.atan, 'arctan': sp.atan, 'arcctg': sp.acot,
    'ln': sp.log, 'lg': lambda x: sp.log(x, 10), 'exp': sp.exp,
}
GREEK = {'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'varphi': 'φ', 'phi': 'φ'}

TOKEN = re.compile(r'\s*(?:(\d+(?:\.\d+)?)|(\\[a-zA-Z]+)|(.))')


class TexError(ValueError):
    pass


KNOWN = set(FUNCS) | {'log', 'frac', 'sqrt', 'pi', 'cdot', 'times', 'div', 'circ', 'le', 'ge', 'ne', 'in', 'cup', 'cap', 'infty',
                      'alpha', 'beta', 'gamma', 'varphi', 'phi', 'left', 'right', 'operatorname', 'text', 'tan', 'cot'}


def _split_command(t: str) -> list[str]:
    """«\\cosx» (пробел съел compact) → «\\cos», «x»; известные команды не трогаем"""
    if not t.startswith('\\') or t[1:] in KNOWN:
        return [t]
    name = t[1:]
    for k in sorted(KNOWN, key=len, reverse=True):
        if name.startswith(k) and name[len(k):].isalpha():
            return ['\\' + k] + list(name[len(k):])
    return [t]


def prepare(tex: str) -> str:
    s = tex.replace('\\left', '').replace('\\right', '').replace('{,}', '.').replace('·', '\\cdot ')
    s = s.replace('\\displaystyle', '').replace('\\,', ' ').replace('\\ ', ' ').replace('−', '-')
    s = re.sub(r'\\operatorname\{(\w+)\}', r'\\\1', s)
    s = re.sub(r'\\text\{\s*(\d*)\s*π\s*\}', r'\1\\pi', s)
    s = re.sub(r'\\text\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\text(?![a-zA-Z{])', '', s)  # «\text» без аргумента — мусор экспорта ФИПИ
    s = s.replace('π', '\\pi ').replace('α', '\\alpha ').replace('β', '\\beta ')
    s = s.replace('\\dfrac', '\\frac').replace('\\tfrac', '\\frac')
    return s


class Parser:
    def __init__(self, tex: str, symbols: dict | None = None):
        self.tokens = []
        for m in TOKEN.finditer(prepare(tex)):
            t = m.group(1) or m.group(2) or m.group(3)
            if t is None or not t.strip():
                continue
            self.tokens.extend(_split_command(t))
        self.i = 0
        self.symbols = symbols or {}
        self.log_args = []  # аргументы логарифмов до упрощений sympy (3^{log_3 f} сразу превращается в f, а ОДЗ f > 0 нужна)

    # --- токены
    def peek(self, k: int = 0):
        j = self.i + k
        return self.tokens[j] if j < len(self.tokens) else None

    def take(self, expected: str | None = None):
        t = self.peek()
        if t is None or (expected is not None and t != expected):
            raise TexError(f'ждали {expected!r}, а там {t!r} (позиция {self.i})')
        self.i += 1
        return t

    # --- грамматика
    def parse(self) -> sp.Expr:
        e = self.expr()
        if self.peek() is not None:
            raise TexError(f'лишнее: {self.tokens[self.i:]}')
        return e

    def expr(self) -> sp.Expr:
        if self.peek() in ('+', '-'):
            sign = -1 if self.take() == '-' else 1
            e = sign * self.term()
        else:
            e = self.term()
        while self.peek() in ('+', '-'):
            if self.take() == '+':
                e = e + self.term()
            else:
                e = e - self.term()
        return e

    STOP = {'+', '-', ')', '}', ']', '=', '|', '<', '>', ',', ';', '\\le', '\\ge', '\\ne', None}

    def term(self, in_arg: bool = False) -> sp.Expr:
        e = self.power()
        while True:
            t = self.peek()
            if t in ('\\cdot', '\\times', '*'):
                if in_arg:
                    return e  # \sin 68^\circ\cdot\sin 22^\circ — точка заканчивает аргумент
                self.take()
                e = e * self.power()
            elif t in (':', '/', '\\div'):
                self.take()
                e = e / self.power()
            elif t in self.STOP:
                return e
            elif in_arg and t and t.startswith('\\') and t[1:] in FUNCS:
                return e  # \sin x \cos x — второй множитель не в аргумент
            else:
                e = e * self.power()  # неявное умножение: 2\sqrt{3}, 3x
        return e

    def power(self) -> sp.Expr:
        base = self.atom()
        while self.peek() == '^':
            self.take()
            if self.peek() == '\\circ':
                self.take()
                base = base * sp.pi / 180
                continue
            if self.peek() == '{' and self.peek(1) == '\\circ':
                self.take('{'), self.take('\\circ'), self.take('}')
                base = base * sp.pi / 180
                continue
            base = base ** self.script()
        return base

    def script(self) -> sp.Expr:
        """Показатель или индекс: {…}, одна цифра, буква, \\frac…"""
        t = self.peek()
        if t == '{':
            return self.group()
        if t == '-':
            self.take()
            return -self.script()
        if re.fullmatch(r'\d+(?:\.\d+)?', t or ''):
            self.take()
            return sp.Rational(t[0]) if len(t) > 1 and '.' not in t else sp.Rational(t)
        return self.atom()

    def group(self) -> sp.Expr:
        self.take('{')
        e = self.expr()
        self.take('}')
        return e

    def atom(self) -> sp.Expr:
        t = self.peek()
        if t is None:
            raise TexError('выражение оборвалось')
        if re.fullmatch(r'\d+(?:\.\d+)?', t):
            self.take()
            return sp.Rational(t)
        if t == '(':
            self.take()
            e = self.expr()
            self.take(')')
            return e
        if t == '[':
            self.take()
            e = self.expr()
            self.take(']')
            return e
        if t == '{':
            return self.group()
        if t == '|':
            self.take()
            e = self.expr()
            self.take('|')
            return sp.Abs(e)
        if t == '\\frac':
            self.take()
            a = self.frac_part()
            b = self.frac_part()
            return a / b
        if t == '\\sqrt':
            self.take()
            n = 2
            if self.peek() == '[':
                self.take()
                n = self.expr()
                self.take(']')
            arg = self.group() if self.peek() == '{' else self.atom()
            return sp.root(arg, n) if n != 2 else sp.sqrt(arg)
        if t == '\\pi':
            self.take()
            return sp.pi
        if t == '\\log':
            self.take()
            base = sp.Integer(10)
            if self.peek() == '_':
                self.take()
                base = self.log_base()
            power = self._func_power()
            parenthesized = self.peek() == '('
            arg = self.func_arg()
            if parenthesized and self.peek() == '^':
                # {\log }_2{(x-5)}^2 у ФИПИ — логарифм квадрата; квадрат логарифма пишут \log_2^2
                self.take()
                arg = arg ** self.script()
            self.log_args.append(arg)
            return sp.log(arg, base) ** power
        if t.startswith('\\') and t[1:] in FUNCS:
            self.take()
            power = self._func_power()
            parenthesized = self.peek() == '('
            arg = self.func_arg()
            if t in ('\\ln', '\\lg') and parenthesized and self.peek() == '^':
                # \ln(x+9)^5 в заданиях ЕГЭ означает ln((x+9)^5)
                self.take()
                arg = arg ** self.script()
            if t in ('\\ln', '\\lg'):
                self.log_args.append(arg)
            return FUNCS[t[1:]](arg) ** power
        if t.startswith('\\') and t[1:] in GREEK:
            self.take()
            return self.symbols.get(GREEK[t[1:]], sp.Symbol(GREEK[t[1:]]))
        if re.fullmatch(r'[a-zA-Zα-ω]', t):
            self.take()
            if t == 'e' and 'e' not in self.symbols:
                return sp.E
            return self.symbols.get(t, sp.Symbol(t))
        raise TexError(f'непонятный токен {t!r}')

    def frac_part(self) -> sp.Expr:
        t = self.peek()
        if t == '{':
            return self.group()
        if re.fullmatch(r'\d+', t or ''):  # \frac17 — токен «17» это две цифры
            self.take()
            if len(t) > 1:
                self.tokens.insert(self.i, t[1:])
                return sp.Integer(t[0])
            return sp.Integer(t)
        return self.atom()

    def log_base(self) -> sp.Expr:
        t = self.peek()
        if t == '{':
            return self.group()
        if re.fullmatch(r'\d+(?:\.\d+)?', t or ''):  # \log_3162, \log_26.4 — основание одна цифра
            self.take()
            if len(t) > 1:
                self.tokens.insert(self.i, t[1:])
            return sp.Integer(t[0])
        return self.atom()

    def _func_power(self) -> sp.Expr:
        if self.peek() == '^':
            self.take()
            return self.script()
        return sp.Integer(1)

    def func_arg(self) -> sp.Expr:
        """Аргумент функции: в скобках — до скобки, иначе произведение до знака + / - / следующей функции"""
        if self.peek() == '(':
            self.take()
            e = self.expr()
            self.take(')')
            return e
        return self.term(in_arg=True)


def to_sympy(tex: str, symbols: dict | None = None) -> sp.Expr:
    return Parser(tex, symbols).parse()


def numeric(tex: str, subs: dict | None = None) -> complex:
    expr = to_sympy(tex)
    if subs:
        expr = expr.subs({sp.Symbol(k): v for k, v in subs.items()})
    return complex(sp.N(expr, 30))


def equals(tex: str, answer, subs: dict | None = None, eps: float = 1e-9) -> bool:
    """Выражение в LaTeX численно равно ответу"""
    v = numeric(tex, subs)
    if abs(v.imag) > eps:
        return False
    a = float(Fraction(answer)) if not isinstance(answer, float) else answer
    return abs(v.real - a) <= eps * max(1.0, abs(a))


def to_sympy_logs(tex: str):
    """(выражение, аргументы всех логарифмов) — для ОДЗ"""
    p = Parser(tex)
    return p.parse(), p.log_args
