"""
№ 13: показательные и логарифмические уравнения (в том числе с тригонометрией в показателе).

Приводим степени к общему простому основанию g, выражаем показатели через одну переменную
(sin x, cos x или x), выделяем «единицу» показателя q и делаем замену t = g^q. Либо, если это
равенство двух степеней, приравниваем показатели. Логарифмы — заменой t = log_b f(x).
Дальше простейшие уравнения решает trig.analytic.
"""
import re

import sympy as sp

from app.bankgen.trig import C, S, T, TWO_PI, X, _defined, analytic, lower, lower_s, to_sc


def _base_power(b):
    """b = g^k для наименьшего g > 1: 16 → (2, 4), 1/49 → (7, −2)"""
    b = sp.nsimplify(b)
    if not b.is_Rational or b <= 0 or b == 1:
        return None
    n, d = int(b.p), int(b.q)
    if d == 1:
        m, sign = n, 1
    elif n == 1:
        m, sign = d, -1
    else:
        return None
    for g in range(2, m + 1):
        k, r = 0, m
        while r % g == 0:
            r //= g
            k += 1
        if r == 1:
            return g, sign * k
    return None


def _canon(e, var_pref=None):
    """Показатель → многочлен от одной переменной: s (sin x), c (cos x) или x"""
    if not e.has(sp.sin, sp.cos, sp.tan):
        return sp.expand(e), X
    sc = sp.expand(to_sc(e))
    if sc.free_symbols <= {S} and var_pref in (None, S):
        return sc, S
    if sc.free_symbols <= {C} and var_pref in (None, C):
        return sc, C
    for v, low in ((S, lower), (C, lower_s)):
        if var_pref not in (None, v):
            continue
        a, b = low(sc)
        if sp.expand(b) == 0:
            return a, v
    return None, None


def var_tex(v) -> str:
    return {S: '\\sin x', C: '\\cos x'}.get(v, 'x')


def poly_tex(e, v) -> str:
    s = sp.latex(sp.expand(e).subs(v, sp.Symbol(var_tex(v))), order='lex')
    return re.sub(r'\\(sin|cos) x\^\{(\d+)\}', r'\\\1^{\2} x', s)


def exp_substitution(expr):
    """(шаги, [уравнения q − значение], переменная) или None"""
    pows = [p for p in expr.atoms(sp.Pow) if p.base.is_number and p.exp.has(X)]
    if not pows or expr.atoms(sp.exp):
        return None
    gs = {}
    for p in pows:
        bp = _base_power(p.base)
        if bp is None:
            return None
        gs[p] = bp
    if len({g for g, _ in gs.values()}) != 1:
        return None
    g = next(iter(gs.values()))[0]
    var, canon = None, {}
    for p, (_, k) in gs.items():
        poly_e, v = _canon(k * p.exp, var)
        if poly_e is None:
            return None
        var = var or v
        canon[p] = poly_e
    consts = {p: e.subs(var, 0) for p, e in canon.items()}
    parts = {p: sp.expand(e - consts[p]) for p, e in canon.items()}
    nonzero = [q for q in parts.values() if q != 0]
    if not nonzero:
        return None
    q1 = nonzero[0]
    ratios = {p: sp.nsimplify(sp.simplify(q / q1)) for p, q in parts.items()}
    if any(not r.is_Rational for r in ratios.values()):
        return None
    lcm = sp.ilcm(*[r.q for r in ratios.values()]) if len(ratios) > 1 else ratios[next(iter(ratios))].q
    ints = {p: int(r * lcm) for p, r in ratios.items()}
    gcd = sp.igcd(*[abs(v) for v in ints.values() if v]) if len([v for v in ints.values() if v]) > 1 else abs(next(v for v in ints.values() if v))
    unit = sp.expand(q1 / lcm * gcd)
    ints = {p: v // gcd for p, v in ints.items()}
    if unit.could_extract_minus_sign():
        unit, ints = -unit, {p: -v for p, v in ints.items()}
    sub = {p: sp.Integer(g) ** consts[p] * T ** ints[p] for p in pows}
    e_t = sp.expand(expr.xreplace(sub))
    if e_t.has(X):
        return None
    lo = min(0, min(ints.values()))
    poly_t = sp.fraction(sp.together(sp.expand(e_t * T ** (-lo))))[0]
    poly_t = sp.expand(poly_t)
    if poly_t.free_symbols != {T}:
        return None
    if sp.Poly(poly_t, T).LC() < 0:
        poly_t = -poly_t
    unit_tex = poly_tex(unit, var)
    steps = [f'Приведём все степени к основанию ${g}$ и сделаем замену $t={g}^{{{unit_tex}}}$, $t>0$: $${sp.latex(poly_t)}=0.$$']
    roots = [r for r in sp.solve(poly_t, T) if r.is_real]
    good, bad = [r for r in roots if r > 0], [r for r in roots if r <= 0]
    msg = 'Корни: ' + ', '.join(f'$t={sp.latex(r)}$' for r in roots) + '.'
    if bad:
        msg += ' Условию $t>0$ не удовлетворяет ' + ', '.join(f'$t={sp.latex(r)}$' for r in bad) + '.'
    steps.append(msg)
    eqs = []
    for r in good:
        val = sp.nsimplify(sp.log(r, g))
        if not val.is_Rational:
            return None
        steps.append(f'${g}^{{{unit_tex}}}={sp.latex(r)}\\ \\Rightarrow\\ {unit_tex}={sp.latex(val)}$.')
        eqs.append((unit - val, var))
    return steps, eqs


def exp_equal(expr):
    """k·g^{e₁} − k·g^{e₂} = 0 → e₁ = e₂"""
    terms = sp.Add.make_args(sp.expand(expr))
    if len(terms) != 2:
        return None
    sides = []
    for term in terms:
        coeff, rest = term.as_independent(X, as_Add=False)
        if not (isinstance(rest, sp.Pow) and rest.base.is_number and rest.exp.has(X)):
            return None
        bp = _base_power(rest.base)
        if bp is None:
            return None
        sides.append((coeff, bp[0], sp.expand(bp[1] * rest.exp)))
    (c1, g1, e1), (c2, g2, e2) = sides
    if g1 != g2 or c1 != -c2:
        return None
    l1, l2 = _tex(e1), _tex(e2)
    steps = [f'Приведём обе степени к основанию ${g1}$: $${g1}^{{{l1}}}={g1}^{{{l2}}}.$$ Показательная функция монотонна, '
             f'поэтому показатели равны: $${l1}={l2}.$$']
    return steps, [(sp.expand(e1 - e2), None)]


def _tex(e) -> str:
    s = sp.latex(e).replace('\\left(', '(').replace('\\right)', ')')
    return re.sub(r'\\(sin|cos)\{\((\w+) \)\}', r'\\\1 \2', s).replace('{\\left(x \\right)}', ' x')


def log_substitution(expr):
    """Многочлен от log_b f(x): замена t = log_b f(x)"""
    logs = list(expr.atoms(sp.log))
    args = {a.args[0] for a in logs if a.args[0].has(X)}
    if len(args) != 1:
        return None
    arg = args.pop()
    base = sp.E
    for a in logs:
        if not a.args[0].has(X):
            base = a.args[0]
    e_t = sp.expand(sp.simplify(expr.subs(sp.log(arg), T * sp.log(base))))
    if e_t.has(X):
        return None
    poly_t = sp.fraction(sp.together(e_t))[0]
    poly_t = sp.Poly(poly_t, T).monic().as_expr()
    roots = [r for r in sp.solve(poly_t, T) if r.is_real]
    arg_tex = _tex(arg)
    btex = sp.latex(base)
    steps = [f'Сделаем замену $t=\\log_{{{btex}}}{arg_tex}$: $${sp.latex(sp.expand(poly_t))}=0,$$ откуда ' + ', '.join(f'$t={sp.latex(r)}$' for r in roots) + '.']
    eqs = []
    for r in roots:
        val = sp.nsimplify(base ** r)
        steps.append(f'$\\log_{{{btex}}}{arg_tex}={sp.latex(r)}\\ \\Rightarrow\\ {arg_tex}={sp.latex(val)}$.')
        eqs.append((arg - val, None))
    return steps, eqs


def solve13(expr):
    """(шаги, корни, kind): kind = 'trig' — корни на [0; 2π), 'real' — вещественные корни"""
    steps = []
    num, den = sp.fraction(sp.together(expr))
    work = expr
    if den.has(X):
        steps.append('Дробь равна нулю, когда числитель равен нулю, а знаменатель определён и отличен от нуля. Решим уравнение '
                     '«числитель равен нулю» и отбросим корни, не входящие в ОДЗ.')
        work = num

    def finish(eqs, local):
        roots, kind = [], 'trig'
        for eq, v in eqs:
            if v in (S, C):
                eq = eq.subs({S: sp.sin(X), C: sp.cos(X)})
            if not eq.has(sp.sin, sp.cos, sp.tan):
                kind = 'real'
                rs = [r for r in sp.solve(eq, X) if r.is_real]
                roots += rs
                continue
            res = analytic(eq)
            if res is None:
                return None
            for st in (res[0][1:] if len(res[0]) > 1 else res[0]):
                head = 'Решаем простейшие уравнения:'
                if st.startswith(head) and any(x.startswith(head) for x in local):
                    i = max(i for i, x in enumerate(local) if x.startswith(head))
                    local[i] += st[len(head):]   # одно перечисление простейших уравнений вместо нескольких
                else:
                    local.append(st)
            roots += res[1]
        if kind == 'trig':
            roots = sorted({sp.nsimplify(r % TWO_PI) for r in roots}, key=lambda r: float(r))
        bad = [r for r in roots if not _defined(expr, r)]
        if bad:
            local.append('Учтём ОДЗ: не подходят ' + ', '.join(f'$x={sp.latex(r)}' + ('+2\\pi k' if kind == 'trig' else '') + '$' for r in bad) + '.')
        return steps + local, [r for r in roots if r not in bad], kind

    for method in (exp_equal, exp_substitution, log_substitution):
        r = method(work)
        if r:
            return finish(r[1], list(r[0]))
    res = analytic(expr)
    if res is None:
        return None
    return res[0], res[1], 'trig'
