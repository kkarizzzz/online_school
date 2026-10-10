"""
Движок кредитных и вкладных схем для № 16.

Схема — n периодов. В начале периода долг умножается на q = 1 + r/100, затем вносится платёж p_k,
остаток D_k. Для каждого периода задаётся либо остаток (выражение от S, r, x …), либо платёж; недостающее
выводится из D_k = q·D_{k−1} − p_k. Дополнительные условия — уравнения (сумма платежей, последний платёж и т. п.).

    scheme = Scheme(n=3, rate='r', S=6000, debts=['S', '0.3*S', '0.09*S', '0'], equations=['total = 8085'])
    scheme.solve('r') → 15

Решение для ученика строится по той же схеме: таблица долгов и платежей и уравнение.
"""
from dataclasses import dataclass, field
from fractions import Fraction

import sympy as sp

S, r, x, y = sp.symbols('S r x y', real=True)
NAMES = {'S': S, 'r': r, 'x': x, 'y': y}


def _e(v):
    if v is None:
        return None
    if isinstance(v, (int, float, Fraction)):
        return sp.nsimplify(v)
    return sp.sympify(str(v).replace(',', '.'), locals=NAMES)


@dataclass
class Scheme:
    n: int
    rate: object = 'r'                 # процент за период (число или 'r'), можно список по периодам
    S: object = 'S'                    # сумма кредита
    debts: list = field(default_factory=list)      # длина n+1: D_0 … D_n (None — вывести)
    payments: list = field(default_factory=list)   # длина n: p_1 … p_n (None — вывести)
    equations: list = field(default_factory=list)  # строки «левая = правая», доступны total, p1…, D0…
    deposit: bool = False              # вклад: пополнения вместо платежей, рост без выплат

    def build(self):
        """Символьные D_k, p_k"""
        rates = self.rate if isinstance(self.rate, list) else [self.rate] * self.n
        q = [1 + _e(v) / 100 for v in rates]
        debts = [_e(d) for d in (self.debts or [None] * (self.n + 1))]
        pays = [_e(p) for p in (self.payments or [None] * self.n)]
        if debts[0] is None:
            debts[0] = S
        known_S = _e(self.S)
        self.links = []   # периоды, где заданы и долг, и платёж: даёт уравнение
        for k in range(1, self.n + 1):
            grown = q[k - 1] * debts[k - 1]
            if debts[k] is None and pays[k - 1] is not None:
                debts[k] = sp.expand(grown - pays[k - 1])
            elif pays[k - 1] is None and debts[k] is not None:
                pays[k - 1] = sp.expand(grown - debts[k])
            elif debts[k] is None and pays[k - 1] is None:
                raise ValueError(f'период {k}: не задан ни долг, ни платёж')
            else:
                self.links.append(sp.Eq(sp.expand(grown - pays[k - 1]), debts[k]))
        if known_S != S:
            debts = [sp.expand(d.subs(S, known_S)) for d in debts]
            pays = [sp.expand(p.subs(S, known_S)) for p in pays]
            self.links = [l.subs(S, known_S) for l in self.links]
        return debts, pays, q

    def context(self, debts, pays):
        ctx = {f'p{k + 1}': p for k, p in enumerate(pays)}
        ctx.update({f'D{k}': d for k, d in enumerate(debts)})
        ctx['total'] = sp.expand(sum(pays))
        ctx.update(NAMES)
        return ctx

    def equations_sym(self, debts, pays):
        ctx = self.context(debts, pays)
        out = []
        for eq in self.equations:
            left, right = eq.split('=')
            out.append(sp.Eq(sp.sympify(left.replace(',', '.'), locals=ctx), sp.sympify(right.replace(',', '.'), locals=ctx)))
        return out

    def solve(self, ask: str, unknowns=None):
        debts, pays, _ = self.build()
        eqs = self.equations_sym(debts, pays) + [l for l in self.links if l is not sp.true]
        syms = sorted(set().union(*[e.free_symbols for e in eqs]) if eqs else set(), key=str)
        sol = sp.solve(eqs, syms, dict=True) if eqs else [{}]
        good = [s for s in sol if all(v.is_real and (v > 0) for v in s.values())] or sol
        if not good:
            raise ValueError('нет решения')
        s = good[0]
        ctx = self.context([d.subs(s) for d in debts], [p.subs(s) for p in pays])
        val = sp.nsimplify(sp.sympify(ask, locals=ctx).subs(s))
        return val, s, debts, pays


def money(v, unit: str = '') -> str:
    v = sp.nsimplify(v)
    t = sp.latex(v) if not v.is_Integer else f'{int(v):,}'.replace(',', '\\,')
    return t.replace('.', '{,}')
