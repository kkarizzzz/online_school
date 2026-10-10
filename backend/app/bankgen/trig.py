"""
Решатель тригонометрических уравнений для № 13.

Две независимые части:
  numeric_roots() — корни на [0; 2π) численно (смена знака + касания), каждый корень распознаётся как
                    рациональная доля π и проверяется точной подстановкой и ОДЗ исходного уравнения;
  reduce_poly()   — аналитика: формулы приведения и двойного угла (expand_trig), замена sin x = s, cos x = c,
                    понижение c² = 1 − s², разложение на множители. По её шагам пишется решение.
Ответ принимается, только если множества корней обеих частей совпали.
"""
import math
import re
from fractions import Fraction

import sympy as sp

X = sp.Symbol('x', real=True)
S, C, T = sp.symbols('s c t', real=True)
TWO_PI = 2 * sp.pi


# ---------------------------------------------------------------------------
# Численная часть
# ---------------------------------------------------------------------------

def _defined(expr, x0) -> bool:
    """Выражение определено в точке: знаменатели ≠ 0, под корнями ≥ 0, под логарифмами > 0"""
    for node in sp.preorder_traversal(expr):
        if isinstance(node, sp.Pow) and node.exp.is_negative:
            v = complex(sp.N(node.base.subs(X, x0), 30))
            if abs(v) < 1e-12:
                return False
        if isinstance(node, sp.Pow) and node.exp.is_Rational and not node.exp.is_integer:
            v = complex(sp.N(node.base.subs(X, x0), 30))
            if abs(v.imag) > 1e-12 or v.real < -1e-12:
                return False
            if node.exp.is_negative and abs(v) < 1e-12:
                return False
        if isinstance(node, sp.log):
            v = complex(sp.N(node.args[0].subs(X, x0), 30))
            if abs(v.imag) > 1e-12 or v.real <= 1e-12:
                return False
        if isinstance(node, (sp.tan, sp.cot)):
            v = complex(sp.N(node.subs(X, x0), 30))
            if not math.isfinite(abs(v)) or abs(v) > 1e12:
                return False
    return True


def numeric_roots(expr, period=TWO_PI, max_den: int = 24) -> list[sp.Expr]:
    """Корни на [0; period), распознанные как p/q·π и подтверждённые подстановкой"""
    f = sp.lambdify(X, expr, modules=['mpmath'])
    import mpmath
    mpmath.mp.dps = 30
    P = float(period)
    n = 7200
    xs = [P * i / n for i in range(n + 1)]

    def val(x):
        try:
            v = complex(f(mpmath.mpf(x)))
            return v.real if abs(v.imag) < 1e-9 else math.nan
        except (ValueError, ZeroDivisionError, TypeError, OverflowError):
            return math.nan

    ys = [val(x) for x in xs]
    candidates = set()
    for i in range(n):
        a, b = ys[i], ys[i + 1]
        if math.isnan(a) or math.isnan(b):
            continue
        if a == 0:
            candidates.add(xs[i])
        if a * b < 0:
            candidates.add((xs[i] + xs[i + 1]) / 2)
    # касания: локальные минимумы |f|
    for i in range(1, n):
        a, b, c = ys[i - 1], ys[i], ys[i + 1]
        if any(math.isnan(v) for v in (a, b, c)):
            continue
        if abs(b) <= abs(a) and abs(b) <= abs(c) and abs(b) < 1e-2:
            candidates.add(xs[i])
    roots = set()
    for x0 in candidates:
        r = Fraction(x0 / math.pi).limit_denominator(max_den)
        exact = sp.Rational(r.numerator, r.denominator) * sp.pi
        exact = exact % period
        try:
            v = complex(sp.N(expr.subs(X, exact), 40))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if abs(v) < 1e-20 and _defined(expr, exact):
            roots.add(sp.nsimplify(exact))
    return sorted(roots, key=lambda r: float(r))


# ---------------------------------------------------------------------------
# Аналитическая часть
# ---------------------------------------------------------------------------

def to_sc(expr) -> sp.Expr:
    """Выражение от x → многочлен (или дробь) от s = sin x, c = cos x"""
    e = sp.expand_trig(sp.expand(expr))
    e = e.rewrite(sp.sin).rewrite(sp.cos) if False else e
    e = e.subs({sp.tan(X): sp.sin(X) / sp.cos(X), sp.cot(X): sp.cos(X) / sp.sin(X)})
    e = sp.expand_trig(e)
    return sp.together(e.subs({sp.sin(X): S, sp.cos(X): C}))


def lower(poly_sc):
    """Понижаем чётные степени c через c² = 1 − s² (или s через c): P = A(s) + c·B(s)"""
    p = sp.Poly(sp.expand(poly_sc), C)
    a = b = sp.Integer(0)
    for (k,), coeff in p.terms():
        base = (1 - S ** 2) ** (k // 2)
        if k % 2 == 0:
            a += coeff * base
        else:
            b += coeff * base
    return sp.expand(a), sp.expand(b)


def lower_s(poly_sc):
    p = sp.Poly(sp.expand(poly_sc), S)
    a = b = sp.Integer(0)
    for (k,), coeff in p.terms():
        base = (1 - C ** 2) ** (k // 2)
        if k % 2 == 0:
            a += coeff * base
        else:
            b += coeff * base
    return sp.expand(a), sp.expand(b)


def basic_roots(func: str, value) -> list[sp.Expr]:
    """Корни sin x = a / cos x = a / tg x = a на [0; 2π)"""
    value = sp.nsimplify(value)
    if func in ('sin', 'cos') and (value > 1 or value < -1):
        return []
    if func == 'sin':
        a = sp.asin(value)
        cands = [a, sp.pi - a]
    elif func == 'cos':
        a = sp.acos(value)
        cands = [a, -a]
    else:
        a = sp.atan(value)
        cands = [a, a + sp.pi]
    return sorted({sp.nsimplify(c % TWO_PI) for c in cands}, key=lambda r: float(r))


def series_text(residues: list[sp.Expr]) -> list[str]:
    """Корни на [0; 2π) → серии: «r + 2πk», а пары r, r+π — «r + πk» (k ∈ Z)"""
    rs = sorted(set(residues), key=lambda r: float(r))
    used, out = set(), []
    # шаг π/2: четыре корня через четверть периода
    for r in rs:
        if r in used:
            continue
        quarter = [sp.nsimplify((r + j * sp.pi / 2) % TWO_PI) for j in range(4)]
        if all(q in rs for q in quarter):
            base = min(quarter, key=lambda q: float(q))
            out.append(_series(base, '\\frac{\\pi k}{2}'))
            used.update(quarter)
            continue
        twin = sp.nsimplify((r + sp.pi) % TWO_PI)
        if twin in rs and twin not in used:
            base = min(r, twin, key=lambda q: float(q))
            base = _nice_base(base, sp.pi)
            out.append(_series(base, '\\pi k'))
            used.update({r, twin})
            continue
        out.append(_series(_nice_base(r, TWO_PI), '2\\pi k'))
        used.add(r)
    return out


def _nice_base(r, period):
    """Представитель серии ближе к нулю: 7π/4 + 2πk → −π/4 + 2πk"""
    alt = r - period
    return alt if abs(float(alt)) < abs(float(r)) else r


def _series(base, step: str) -> str:
    if base == 0:
        return step if step != '2\\pi k' else '2\\pi k'
    b = sp.latex(base).replace('\\frac{\\pi}{', '\\frac{\\pi}{')
    return f'{b}+{step}'


def _tex_sc(e) -> str:
    """Многочлен от s, c → LaTeX с sin x, cos x"""
    sx, cx = sp.Symbol('\\sin x'), sp.Symbol('\\cos x')
    s = sp.latex(sp.expand(e).subs({S: sx, C: cx}), order='lex')
    return re.sub(r'\\(sin|cos) x\^\{(\d+)\}', r'\\\1^{\2} x', s)


def _var_name(v) -> str:
    return '\\sin x' if v == S else '\\cos x'


def _factor(e):
    """Разложение с учётом корней в коэффициентах (√2, √3 …)"""
    ext = sorted({a for a in e.atoms(sp.Pow) if a.exp == sp.Rational(1, 2) and a.base.is_Integer}, key=str)
    try:
        return sp.factor_list(e, S, C, extension=ext) if ext else sp.factor_list(e, S, C)
    except (sp.PolynomialError, NotImplementedError):
        return sp.factor_list(e, S, C)


def _homogeneous(e) -> bool:
    """Однородное и делится на cosⁿx без потери корней: есть слагаемое sinⁿx (иначе cos x = 0 — тоже корень)"""
    if e.free_symbols != {S, C}:
        return False
    p = sp.Poly(e, S, C)
    degs = {sum(m) for m in p.monoms()}
    if len(degs) != 1 or 0 in degs:
        return False
    return p.coeff_monomial(S ** degs.pop()) != 0


def _symmetric(e):
    """Симметричный многочлен от sin x и cos x: замена t = sin x + cos x, sin x·cos x = (t² − 1)/2"""
    from sympy.polys.polyfuncs import symmetrize
    s1, s2 = sp.symbols('s1 s2')
    sym, rem = symmetrize(sp.expand(e), S, C, formal=True)[:2]
    if rem != 0:
        return None
    q = sp.expand(sym.subs(s2, (T ** 2 - 1) / 2).subs(s1, T)) if sym.has(s1, s2) else None
    if q is None or q.free_symbols != {T}:
        return None
    q_tex = sp.latex(q)
    ts = [r for r in sp.solve(q, T) if r.is_real]
    steps = [f'Сделаем замену $t=\\sin x+\\cos x$, тогда $t^2=1+2\\sin x\\cos x$, то есть $\\sin x\\cos x=\\frac{{t^2-1}}{{2}}$, '
             f'и $|t|\\le\\sqrt{{2}}$: $${q_tex}=0,$$ откуда ' + ', '.join(f'$t={sp.latex(r)}$' for r in ts) + '.']
    roots, pieces = [], []
    for t0 in ts:
        if abs(float(t0)) > math.sqrt(2) + 1e-12:
            pieces.append(f'$t={sp.latex(t0)}$ не подходит: $|t|>\\sqrt{{2}}$')
            continue
        val = sp.nsimplify(t0 / sp.sqrt(2))
        ys = basic_roots('sin', val)
        xs = [sp.nsimplify((y - sp.pi / 4) % TWO_PI) for y in ys]
        roots += xs
        pieces.append(f'$\\sin x+\\cos x=\\sqrt{{2}}\\sin\\left(x+\\frac{{\\pi}}{{4}}\\right)={sp.latex(t0)}$, '
                      f'$\\sin\\left(x+\\frac{{\\pi}}{{4}}\\right)={sp.latex(val)}$: ' + ', '.join(f'$x={s}$' for s in series_text(xs)))
    steps.append('Возвращаемся к $x$:\n\n' + '\n\n'.join(f'- {p_};' for p_ in pieces))
    return steps, sorted(set(roots), key=lambda r: float(r))


def _homogenize(e):
    """Слагаемые младших степеней домножаем на (s² + c²)^k до общей чётной степени"""
    p = sp.Poly(sp.expand(e), S, C)
    degs = {sum(m) for m in p.monoms()}
    top = max(degs)
    if any((top - d) % 2 for d in degs):
        return None
    out = 0
    for m, coeff in p.terms():
        out += coeff * S ** m[0] * C ** m[1] * (S ** 2 + C ** 2) ** ((top - sum(m)) // 2)
    return sp.expand(out)


def analytic(expr):
    """
    Аналитическое решение уравнения expr = 0, если оно сводится к многочлену от sin x и cos x.
    Возвращает (шаги решения — список абзацев, корни на [0; 2π)) или None.
    """
    num, den = sp.fraction(sp.together(to_sc(expr)))
    num = sp.expand(num)
    if num.free_symbols - {S, C}:
        return None
    steps = []
    poly_tex = _tex_sc(num)
    steps.append(f'Применим формулы приведения и двойного угла и запишем уравнение через $\\sin x$ и $\\cos x$: $${poly_tex}=0.$$')

    # 1) многочлен от одной функции
    if num.free_symbols == {C}:          # уже уравнение относительно cos x
        target, var = num, C
    elif num.free_symbols == {S}:
        target, var = num, S
    else:
        a, b = lower(num)
        if sp.expand(b) == 0:
            target, var = a, S
        else:
            a2, b2 = lower_s(num)
            target, var = (a2, C) if sp.expand(b2) == 0 else (None, None)

    factors = []
    if target is not None and target.free_symbols <= {var}:
        if target != num:
            rule = '\\cos^2 x=1-\\sin^2 x' if var == S else '\\sin^2 x=1-\\cos^2 x'
            steps.append(f'Заменим ${rule}$ и получим уравнение относительно ${_var_name(var)}$: $${_tex_sc(target)}=0.$$')
        fl = sp.factor_list(sp.expand(target), var)
        factors = [f for f, _ in fl[1]]
    else:
        fl = (1, [(num, 1)]) if _homogeneous(num) else _factor(num)  # однородное сразу сводим к tg x
        factors = [f for f, _ in fl[1]]
        if len(factors) < 2 and not _homogeneous(num):
            sym = _symmetric(num)
            if sym is not None:
                return steps + sym[0], sym[1]
            # постоянные слагаемые заменяем на k(sin²x + cos²x) — бывает, что после этого раскладывается
            hom = _homogenize(num)
            if hom is None:
                return None
            fl = _factor(hom)
            factors = [f for f, _ in fl[1]]
            if len(factors) < 2 and not _homogeneous(hom):
                return None
            steps.append(f'Заменим $1=\\sin^2 x+\\cos^2 x$: $${_tex_sc(hom)}=0.$$')
            num = hom
        if len(factors) > 1:
            steps.append('Разложим левую часть на множители: $$' + '\\cdot '.join(f'\\left({_tex_sc(f)}\\right)' for f in factors) + '=0.$$')

    roots, pieces = [], []
    for f in factors:
        syms = f.free_symbols
        if syms == {S} or syms == {C}:
            v = next(iter(syms))
            func = 'sin' if v == S else 'cos'
            for val in sp.solve(f, v):
                if not val.is_real:
                    continue
                rs = basic_roots(func, val)
                name = _var_name(v)
                if not rs:
                    pieces.append(f'${name}={sp.latex(val)}$ — корней нет, так как $|{sp.latex(val)}|>1$')
                    continue
                pieces.append(f'${name}={sp.latex(val)}$: ' + ', '.join(f'$x={s}$' for s in series_text(rs)))
                roots += rs
        elif syms == {S, C} and _homogeneous(f):
            # однородное: при cos x = 0 было бы и sin x = 0 — делим на cosⁿx, получаем многочлен от tg x
            deg = sp.Poly(f, S, C).total_degree()
            tp = sp.expand(sp.expand(f.subs(S, T * C)) / C ** deg)
            vals = [v for v in sp.solve(tp, T) if v.is_real]
            sub = []
            for val in vals:
                rs = basic_roots('tg', val)
                roots += rs
                sub.append(f'$\\operatorname{{tg}} x={sp.latex(sp.nsimplify(val))}$, $x={series_text(rs)[0]}$')
            ttex = re.sub(r'\\operatorname\{tg\} x\^\{(\d+)\}', r'\\operatorname{tg}^{\1} x',
                          sp.latex(tp.subs(T, sp.Symbol('\\operatorname{tg} x'))))
            pieces.append(f'${_tex_sc(f)}=0$ — однородное уравнение: $\\cos x=0$ его не обращает в верное равенство (тогда и $\\sin x=0$), '
                          f'делим на ${"\\cos x" if deg == 1 else f"\\cos^{deg} x"}$: ${ttex}=0$, откуда ' + '; '.join(sub))
        else:
            return None
    steps.append('Решаем простейшие уравнения:\n\n' + '\n\n'.join(f'- {p_};' for p_ in pieces))
    roots = sorted(set(sp.nsimplify(r % TWO_PI) for r in roots), key=lambda r: float(r))
    if den.free_symbols & {S, C}:
        bad = [r for r in roots if not _defined(expr, r)]
        if bad:
            steps.append('Учтём ОДЗ (знаменатель не равен нулю, выражения под корнем и логарифмом допустимы): не подходят '
                         + ', '.join(f'$x={sp.latex(r)}+2\\pi k$' for r in bad) + '.')
        roots = [r for r in roots if r not in bad]
    return steps, roots


def in_segment(residues: list[sp.Expr], a, b) -> list[sp.Expr]:
    out = []
    lo, hi = float(a), float(b)
    for r in residues:
        k0 = math.floor((lo - float(r)) / (2 * math.pi)) - 1
        for k in range(k0, k0 + 4 + int((hi - lo) / (2 * math.pi)) + 2):
            x = sp.nsimplify(r + 2 * k * sp.pi)
            if lo - 1e-12 <= float(x) <= hi + 1e-12:
                out.append(x)
    return sorted(set(out), key=lambda v: float(v))
