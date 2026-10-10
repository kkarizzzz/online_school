"""
Решатель неравенств № 15 (показательные, логарифмические, рациональные).

Схема: ОДЗ → замена t = g^{u(x)} или t = log_b f(x) (если выражение через неё рационально) → рациональное
неравенство относительно t решается точно (sympy, метод интервалов) → обратная замена (монотонная функция)
→ пересечение с ОДЗ. Если замены нет — метод интервалов прямо по x.

Ответ проверяется независимо: на плотной сетке точек знак выражения сравнивается с найденным множеством.
"""
import math
import re

import sympy as sp

from app.bankgen.texmath import to_sympy, to_sympy_logs
from app.bankgen.trig_exp import _base_power

X = sp.Symbol('x', real=True)
T = sp.Symbol('t', real=True)
REL = {'\\ge': sp.GreaterThan, '\\geq': sp.GreaterThan, '\\le': sp.LessThan, '\\leq': sp.LessThan, '>': sp.StrictGreaterThan,
       '<': sp.StrictLessThan}


def parse_inequality(tex: str):
    """'f\\ge g' → (f − g, '\\ge')"""
    m = re.search(r'\\geq?|\\leq?|(?<!\\)[<>]', tex)
    if not m:
        raise ValueError('нет знака неравенства')
    left, rel, right = tex[:m.start()], m.group(0).replace('geq', 'ge').replace('leq', 'le'), tex[m.end():]
    (l, logs_l), (r_, logs_r) = to_sympy_logs(left), to_sympy_logs(right)
    e = (l - r_).subs(sp.Symbol('x'), X)
    logs = [a.subs(sp.Symbol('x'), X) for a in logs_l + logs_r if a.has(sp.Symbol('x'))]
    return e, rel, logs


def domain(expr, extra_logs=()) -> sp.Set:
    """ОДЗ: знаменатели ≠ 0, аргументы логарифмов > 0 (в том числе исчезнувших при упрощении), подкоренные ≥ 0"""
    conds = [a > 0 for a in extra_logs]
    for node in sp.preorder_traversal(expr):
        if isinstance(node, sp.log) and node.args[0].has(X):
            conds.append(node.args[0] > 0)
        if isinstance(node, sp.Pow) and node.base.has(X):
            if node.exp.is_negative:
                conds.append(sp.Ne(node.base, 0))
            if node.exp.is_Rational and not node.exp.is_integer:
                conds.append(node.base >= 0 if node.exp > 0 else node.base > 0)
    s = sp.S.Reals
    for c in conds:
        part = _solve_cond(c)
        s = sp.Intersection(s, part)
    return sp.simplify(s) if not isinstance(s, sp.Intersection) else s


def _solve_cond(c) -> sp.Set:
    try:
        s = sp.solveset(c, X, sp.S.Reals)
    except (NotImplementedError, ValueError):
        s = sp.reduce_inequalities(c, X).as_set()
    if s.has(sp.ConditionSet):
        if isinstance(c, sp.Ne):
            # знаменатель вида log²x − 4·log x: его нули исключит решение после замены (полюса по t)
            return sp.S.Reals
        raise NotImplementedError(f'ОДЗ: {c}')
    return _clean(s)


def _canon(b):
    """Число к одному виду: log 16/log 64 → 2/3, 1 + log 28/log 3 → log 84/log 3, иначе sympy их не сравнит"""
    if b in (sp.oo, -sp.oo):
        return b
    if b.has(sp.log):
        b = sp.logcombine(sp.together(b), force=True)
    return sp.nsimplify(sp.simplify(b))


def _clean(s):
    """Концы промежутков — к каноническому виду (_canon)"""
    v = _canon
    if isinstance(s, sp.Interval):
        return sp.Interval(v(s.start), v(s.end), s.left_open, s.right_open)
    if isinstance(s, sp.FiniteSet):
        return sp.FiniteSet(*[v(b) for b in s])
    if isinstance(s, (sp.Union, sp.Intersection, sp.Complement)):
        return type(s)(*[_clean(a) for a in s.args])
    return s


def _sub_exp(expr):
    """Замена t = g^{u}: (выражение от t, u, g, steps) или None"""
    pows = [p for p in expr.atoms(sp.Pow) if p.base.is_number and p.exp.has(X)] + [e for e in expr.atoms(sp.exp) if e.has(X)]
    if not pows:
        return None
    g = None
    expo = {}
    for p in pows:
        if isinstance(p, sp.exp):
            return None
        bp = _base_power(p.base)
        if bp is None:
            return None
        if g is None:
            g = bp[0]
        elif g != bp[0]:
            return None
        expo[p] = sp.expand(bp[1] * p.exp)
    # единица показателя: общая часть, зависящая от x
    parts = {p: e - e.subs(X, 0) for p, e in expo.items()}
    base = next(q for q in parts.values() if q != 0)
    ratios = {p: sp.nsimplify(sp.simplify(q / base)) for p, q in parts.items()}
    if any(not r.is_Rational for r in ratios.values()):
        return None
    den = sp.ilcm(*[r.q for r in ratios.values()]) if len(ratios) > 1 else next(iter(ratios.values())).q
    ints = {p: int(r * den) for p, r in ratios.items()}
    nz = [abs(v) for v in ints.values() if v]
    gcd = sp.igcd(*nz) if len(nz) > 1 else nz[0]
    unit = sp.expand(base / den * gcd)
    ints = {p: v // gcd for p, v in ints.items()}
    if unit.could_extract_minus_sign():
        unit, ints = -unit, {p: -v for p, v in ints.items()}
    sub = {p: sp.Integer(g) ** sp.expand(expo[p] - parts[p]) * T ** ints[p] for p in pows}
    e_t = sp.together(expr.xreplace(sub))
    if e_t.has(X):
        return None
    return e_t, unit, g


def _log_normalize(expr):
    """
    Все логарифмы — через один log g: log a = k·log g + log c при a = c·g^k (k целое, c > 0).
    На ОДЗ g > 0 (log g есть в условии), поэтому равносильно: log(x²−8x+16) = 2·log(4−x).
    Возвращает (выражение, g) или None.
    """
    args = {l.args[0] for l in expr.atoms(sp.log) if l.args[0].has(X)}
    for g in sorted(args, key=sp.count_ops):
        repl = {}
        for a in args:
            k = sp.Integer(1) if a == g else None
            if k is None and a.is_polynomial(X) and g.is_polynomial(X):
                k = sp.Rational(sp.degree(a, X), sp.degree(g, X))
                c = sp.cancel(a / g ** k) if k.is_Integer else None
                if c is None or c.has(X) or not c.is_positive:
                    k = None
            if k is None:
                break
            repl[sp.log(a)] = k * sp.log(g) + (sp.log(sp.cancel(a / g ** k)) if a != g else 0)
        else:
            return expr.xreplace(repl), g
    return None


def _sub_log(expr):
    """Замена t = log_b f(x), если все логарифмы — от одного аргумента f или его степеней"""
    logs = [l for l in expr.atoms(sp.log) if l.args[0].has(X)]
    if not logs:
        return None
    args = {l.args[0] for l in logs}
    # сначала без «силового» раскрытия: x⁴ = (x²)², аргумент x² (иначе log x² → 2·log x теряет x < 0)
    norm = _log_normalize(expr)
    if norm is not None:
        e, g = norm
        bases = [l.args[0] for l in expr.atoms(sp.log) if not l.args[0].has(X) and l.args[0] != 1]
        b = min(bases, key=lambda v: float(v)) if bases else sp.E
        e_t = sp.simplify(e.subs(sp.log(g), T * sp.log(b)))
        if not e_t.has(X):
            return sp.together(e_t), g, b
    # каждый log(a) раскладываем: a = c·g^k → log a = k·log g + log c; нужен один общий g
    expanded = {a: sp.expand_log(sp.log(sp.factor(a)), force=True) for a in args}
    atoms = {l for v in expanded.values() for l in v.atoms(sp.log) if l.has(X)}
    if len(atoms) != 1:
        return None
    base_log = atoms.pop()
    base_arg = base_log.args[0]
    repl = {}
    for a, v in expanded.items():
        k = sp.simplify(v.coeff(base_log))
        rest = sp.simplify(v - k * base_log)
        if rest.has(X) or not k.is_Rational:
            return None
        repl[sp.log(a)] = k * base_log + rest
    e = expr.xreplace(repl)
    # основание: из числовых логарифмов, делящих log f
    bases = [l.args[0] for l in e.atoms(sp.log) if not l.args[0].has(X) and l.args[0] != 1]
    b = min(bases, key=lambda v: float(v)) if bases else sp.E
    e_t = sp.simplify(e.subs(sp.log(base_arg), T * sp.log(b)))
    if e_t.has(X):
        return None
    return sp.together(e_t), base_arg, b


def _prime_split(expr):
    """
    Степени с разными основаниями: 15^x = 3^x·5^x, 9^x = (3^x)². Переменные u_p = p^x; если выражение —
    многочлен (или дробь) от них и раскладывается на множители, каждый множитель зависит от одной u_p.
    Возвращает (разложенное выражение от x, список множителей) или None.
    """
    pows = [p for p in expr.atoms(sp.Pow) if p.base.is_Integer and p.exp.has(X)]
    if not pows:
        return None
    us, sub = {}, {}
    for p in pows:
        k, c = sp.Poly(p.exp, X).all_coeffs() if sp.Poly(p.exp, X).degree() == 1 else (None, None)
        if k is None or not k.is_Integer:
            return None
        term = sp.Integer(1)
        for prime, mult in sp.factorint(int(p.base)).items():
            u = us.setdefault(prime, sp.Symbol(f'u{prime}', positive=True))
            term *= u ** (mult * k) * sp.Integer(prime) ** (mult * c)
        sub[p] = term
    e_u = sp.together(expr.xreplace(sub))
    num, den = sp.fraction(e_u)
    if num.has(X):
        return None
    fl = sp.factor_list(num)
    factors = [f for f, _ in fl[1]]
    if len(factors) < 2:
        return None
    back = {u: sp.Integer(prime) ** X for prime, u in us.items()}
    den_x = sp.factor(den.xreplace(back))
    num_x = sp.Mul(fl[0], *[f.xreplace(back) ** k for f, k in fl[1]], evaluate=False)
    return num_x / den_x, [f.xreplace(back) for f in factors]


def rational_solve(e_t, rel: str, var=T) -> sp.Set:
    """Рациональное неравенство e_t (rel) 0 по переменной var — точно"""
    cmp = REL[rel](e_t, 0)
    return sp.solve_univariate_inequality(cmp, var, relational=False, domain=sp.S.Reals)


def _back(set_t: sp.Set, inv, low=-sp.oo) -> sp.Set:
    """Образ множества значений t при монотонно возрастающем обратном отображении x = inv(t) (t > 0 для степеней)"""
    if set_t is sp.S.EmptySet:
        return set_t
    if isinstance(set_t, sp.Union):
        return sp.Union(*[_back(s, inv, low) for s in set_t.args])
    if isinstance(set_t, sp.FiniteSet):
        return sp.FiniteSet(*[inv(v) for v in set_t])
    if isinstance(set_t, sp.Interval):
        lo = inv(set_t.start) if set_t.start != -sp.oo else low
        hi = inv(set_t.end) if set_t.end != sp.oo else sp.oo
        return sp.Interval(lo, hi, set_t.left_open, set_t.right_open)
    if isinstance(set_t, sp.Complement):
        return sp.Complement(_back(set_t.args[0], inv, low), _back(set_t.args[1], inv, low))
    raise ValueError(f'не умею обратную замену для {set_t}')


def _zeros(f) -> list:
    """Вещественные нули выражения от x (точно, через sympy)"""
    try:
        sol = sp.solve(f, X)
    except (NotImplementedError, ValueError):
        return []
    return [_canon(s) for s in sol if s.is_real]


def _num_value(expr, x0):
    try:
        v = complex(sp.N(expr.subs(X, x0), 30))
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    if abs(v.imag) > 1e-12 or not math.isfinite(v.real):
        return None
    return v.real


def interval_method(expr, rel: str, points) -> sp.Set:
    """Метод интервалов по точным критическим точкам: знак на каждом промежутке и в самих точках"""
    pts = []
    for p in sorted({_canon(p) for p in points if p.is_real}, key=float):
        if not pts or float(p) - float(pts[-1]) > 1e-12:   # одна точка в разной записи
            pts.append(p)
    res = sp.S.EmptySet
    edges = [-sp.oo] + pts + [sp.oo]
    for a, b in zip(edges, edges[1:]):
        if a == -sp.oo and b == sp.oo:
            mid = 0
        elif a == -sp.oo:
            mid = b - 1
        elif b == sp.oo:
            mid = a + 1
        else:
            mid = (a + b) / 2
        v = _num_value(expr, mid)
        if v is not None and _holds(v, rel):
            res = sp.Union(res, sp.Interval.open(a, b))
    for p in pts:
        v = _num_value(expr, p)
        if v is not None and abs(v) < 1e-20 and rel in ('\\ge', '\\le'):
            if all(sp.Pow(n.base, -1).subs(X, p) != sp.zoo for n in []):
                res = sp.Union(res, sp.FiniteSet(p))
        elif v is not None and _holds(v, rel) and abs(v) > 1e-20:
            res = sp.Union(res, sp.FiniteSet(p))
    return sp.simplify(res)


def _holds(v: float, rel: str) -> bool:
    return {'\\ge': v >= 0, '\\le': v <= 0, '>': v > 0, '<': v < 0}[rel]


def _crit(expr, D, factors=None) -> list:
    """Критические точки: нули множителей числителя и знаменателя и границы ОДЗ"""
    num, den = sp.fraction(sp.together(expr))
    pts = []
    for part in (factors or []) + [num, den]:
        for f, _ in sp.factor_list(part)[1] if part.is_polynomial(X) else [(part, 1)]:
            pts += _zeros(f)
    pts += _bounds(D)
    return [p for p in pts if p not in (-sp.oo, sp.oo)]


def solve_inequality(tex: str):
    """(шаги решения, ответ-множество)"""
    expr, rel, logs = parse_inequality(tex)
    steps = []
    D = domain(expr, logs)
    if D != sp.S.Reals:
        steps.append(f'ОДЗ: $x\\in {latex_set(D)}$.')
    if logs and not expr.has(sp.log):
        steps.append('По основному логарифмическому тождеству $a^{\\log_a f}=f$ (при $f>0$, это учтено в ОДЗ) выражение упрощается.')
    split = _prime_split(expr)
    if split:
        fx, factors = split
        steps.append(f'Разложим числитель на множители, записав степени через простые основания: $${sp.latex(fx)}{_rel_tex(rel)}0.$$')
        num, den = sp.fraction(sp.together(expr))
        pts = []
        for f in factors + [f for f, _ in sp.factor_list(den)[1]]:
            z = _zeros(f)
            pts += z
        pts += [b for b in _bounds(D)]
        crit = sorted({sp.nsimplify(p) for p in pts if p not in (-sp.oo, sp.oo)}, key=float)
        steps.append('Нули множителей: ' + ', '.join(f'$x={_v(p)}$' for p in crit) + '. Расставим их на числовой прямой и определим '
                     'знаки на промежутках (метод интервалов).')
        answer = sp.simplify(sp.Intersection(interval_method(expr, rel, crit), D))
        steps.append(f'Получаем $x\\in {latex_set(answer)}$.')
        return steps, answer, expr, rel, logs
    sub = _sub_exp(expr)
    if sub:
        e_t, unit, g = sub
        ut = sp.latex(unit)
        num, den = sp.fraction(sp.factor(e_t))
        steps.append(f'Сделаем замену $t={g}^{{{ut}}}$, $t>0$. Неравенство примет вид $${sp.latex(sp.factor(e_t))}{_rel_tex(rel)}0.$$')
        st = sp.Intersection(rational_solve(e_t, rel), sp.Interval.open(0, sp.oo))
        st = sp.simplify(st)
        steps.append(f'Методом интервалов (с учётом $t>0$): $t\\in {latex_set(st)}$.')
        # обратная замена: g^{unit} ∈ st → unit ∈ log_g(st) → x
        u_set = _back(st, lambda v: sp.nsimplify(sp.log(v, g)) if v > 0 else -sp.oo)
        steps.append(f'Обратная замена: ${ut}\\in {latex_set(u_set)}$.')
        x_set = _unit_to_x(unit, u_set)
    else:
        lsub = _sub_log(expr)
        if lsub:
            e_t, arg, b = lsub
            at = sp.latex(arg)
            bt = sp.latex(b)
            steps.append(f'Сделаем замену $t=\\log_{{{bt}}}\\left({at}\\right)$. Неравенство примет вид $${sp.latex(sp.factor(e_t))}{_rel_tex(rel)}0.$$')
            st = sp.simplify(rational_solve(e_t, rel))
            steps.append(f'Методом интервалов: $t\\in {latex_set(st)}$.')
            arg_set = _back(st, lambda v: sp.nsimplify(b ** v), low=sp.S.Zero)
            steps.append(f'Обратная замена: ${at}\\in {latex_set(arg_set)}$ (логарифм с основанием ${bt}>1$ возрастает).')
            x_set = _arg_to_x(arg, arg_set)
        elif (comb := _combine_logs(expr)) is not None:
            R, b, c = comb
            bt = sp.latex(b)
            steps.append(f'Соберём логарифмы по основанию ${bt}$ в один: $$\\log_{{{bt}}}\\left({sp.latex(R)}\\right){_rel_tex(rel)}{sp.latex(c)}.$$')
            steps.append(f'Основание ${bt}>1$, логарифм возрастает: $${sp.latex(R)}{_rel_tex(rel)}{sp.latex(sp.Pow(b, c, evaluate=False))}.$$')
            x_set = sp.solve_univariate_inequality(REL[rel](sp.together(R - b ** c), 0), X, relational=False, domain=sp.S.Reals)
        else:
            f = sp.factor(sp.together(expr))
            if f.is_rational_function(X):
                steps.append(f'Приведём к виду $${sp.latex(f)}{_rel_tex(rel)}0$$ и решим методом интервалов.')
                x_set = sp.solve_univariate_inequality(REL[rel](f, 0), X, relational=False, domain=sp.S.Reals)
            else:
                # solve_univariate_inequality с логарифмами может молча ошибиться — только свои нули и метод интервалов
                norm = _log_normalize(expr)
                if norm is not None and norm[0] != expr:
                    f = sp.factor(sp.together(norm[0]))
                    steps.append(f'На ОДЗ выразим все логарифмы через ${_tex_log(norm[1], _log_base(f))}$ '
                                 f'(например, $\\log(c\\cdot g^k)=k\\log g+\\log c$ при $g>0$): $${_tex_logs(f, norm[1])}{_rel_tex(rel)}0.$$')
                crit = _factor_zeros(f) + [b for b in _bounds(D) if b not in (-sp.oo, sp.oo)]
                crit = sorted({sp.nsimplify(p) for p in crit}, key=float)
                steps.append('Нули числителя и знаменателя: ' + ', '.join(f'$x={_v(p)}$' for p in crit) + '. Расставим их вместе с '
                             'границами ОДЗ на числовой прямой и определим знаки на промежутках.')
                x_set = interval_method(expr, rel, crit)
    answer = sp.simplify(sp.Intersection(_clean(x_set), D))
    if D != sp.S.Reals:
        steps.append(f'С учётом ОДЗ: $x\\in {latex_set(answer)}$.')
    return steps, answer, expr, rel, logs


def _factor_zeros(f) -> list:
    """Нули каждого множителя числителя и знаменателя: напрямую, сборкой логарифмов или заменой t = log_b g"""
    num, den = sp.fraction(sp.together(f))
    pts = []
    for part in (num, den):
        for m in sp.Mul.make_args(sp.factor(part)):
            g = m.base if isinstance(m, sp.Pow) else m
            if not g.has(X):
                continue
            if not g.has(sp.log):
                pts += _zeros(g)
                continue
            R = _log_product(g)
            if R is not None:
                pts += _zeros_exp(sp.together(R[0] - R[1]))
                continue
            lsub = _sub_log(g)
            if lsub is not None:
                e_t, arg, b = lsub
                for t in sp.solve(sp.fraction(sp.together(e_t))[0], T):
                    if t.is_real:
                        pts += list(_preimage(arg, sp.FiniteSet(b ** t)))
    return [p for p in pts if p.is_real]


def _log_base(expr):
    bases = [l.args[0] for l in expr.atoms(sp.log) if not l.args[0].has(X) and l.args[0] != 1]
    return min(bases, key=lambda v: float(v)) if bases else sp.E


def _tex_log(g, b) -> str:
    return f'\\log_{{{sp.latex(b)}}}\\left({sp.latex(g)}\\right)'


def _tex_logs(f, g) -> str:
    """ln g/ln b → \\log_b g в записи выражения"""
    b = _log_base(f)
    L = sp.Symbol(_tex_log(g, b))
    return sp.latex(sp.factor(sp.nsimplify(sp.simplify(sp.expand_log(f.subs(sp.log(g), L * sp.log(b)), force=True)))))


def _zeros_exp(g) -> list:
    """Нули выражения с показательными функциями — заменой t = a^{u}, иначе напрямую"""
    num = sp.fraction(sp.together(g))[0]
    sub = _sub_exp(num)
    if sub is None:
        return _zeros(num)
    e_t, unit, base = sub
    res = []
    for t in sp.solve(sp.fraction(sp.together(e_t))[0], T):
        if t.is_real and t > 0:
            res += [z for z in sp.solve(sp.Eq(unit, sp.nsimplify(sp.log(t, base))), X) if z.is_real]
    return res


def _log_product(g):
    """g = Σ kᵢ·ln aᵢ + C с kᵢ/k₀ целыми → (R = Π aᵢ^{kᵢ/k₀}, e^{−C/k₀}): g = 0 ⇔ R = e^{−C/k₀}"""
    terms = sp.Add.make_args(sp.expand(sp.expand_log(g)))
    k0, R, C = None, sp.Integer(1), sp.Integer(0)
    linear = []   # x·ln 2 — от log 2^{x+1}: войдёт в R как 2^{…}
    for t in sorted(terms, key=lambda t: not t.has(sp.log(X)) and not any(l.has(X) for l in t.atoms(sp.log))):
        k, dep = t.as_independent(X, as_Add=False)
        if dep == 1:
            C += t
            continue
        if not isinstance(dep, sp.log):
            if dep.is_polynomial(X) and k0 is not None:
                linear.append(t)
                continue
            return None
        k0 = k if k0 is None else k0
        r = sp.nsimplify(sp.simplify(k / k0))
        if not r.is_Integer:
            return None
        R *= dep.args[0] ** r
    if k0 is None:
        return None
    for t in linear:
        R *= sp.simplify(sp.exp(sp.expand(t / k0)))
    val = sp.nsimplify(sp.simplify(sp.exp(-C / k0)))
    return sp.cancel(R), val


def _combine_logs(expr):
    """
    Σ rᵢ·log_b aᵢ(x) + const (rᵢ целые, одно основание b > 1) → (R(x) = Π aᵢ^{rᵢ}, b, c): неравенство log_b R (rel) c.
    На ОДЗ все aᵢ > 0, поэтому сборка в один логарифм равносильна.
    """
    terms = sp.Add.make_args(sp.expand(expr))
    num_logs = {l.args[0] for l in expr.atoms(sp.log) if not l.args[0].has(X) and l.args[0] != 1}
    for b in sorted(num_logs, key=float):
        if b <= 1:
            continue
        R, c, good = sp.Integer(1), sp.Integer(0), True
        for t in terms:
            k, dep = t.as_independent(X, as_Add=False)
            if dep == 1:
                c -= sp.nsimplify(sp.simplify(t))   # log_b R + const (rel) 0 → log_b R (rel) −const
                continue
            if not isinstance(dep, sp.log):
                good = False
                break
            r = sp.nsimplify(sp.simplify(k * sp.log(b)))
            if not r.is_Integer:
                good = False
                break
            R *= dep.args[0] ** r
        if good and c.is_Rational and R != 1:
            return sp.factor(sp.cancel(R)), b, c
    return None


def _unit_to_x(unit, u_set):
    if unit == X:
        return u_set
    # unit — многочлен от x (например, x² или 2x): решаем unit ∈ u_set
    return sp.solveset(sp.Contains(unit, u_set), X, sp.S.Reals) if False else _preimage(unit, u_set)


def _arg_to_x(arg, arg_set):
    return _preimage(arg, arg_set)


def _preimage(f, s: sp.Set) -> sp.Set:
    """{x : f(x) ∈ s} для интервалов s — через неравенства"""
    if s is sp.S.EmptySet:
        return s
    if isinstance(s, sp.Union):
        return sp.Union(*[_preimage(f, a) for a in s.args])
    if isinstance(s, sp.FiniteSet):
        return sp.Union(*[sp.solveset(sp.Eq(f, v), X, sp.S.Reals) for v in s])
    if isinstance(s, sp.Interval):
        res = sp.S.Reals
        if s.start != -sp.oo:
            res = sp.Intersection(res, sp.solveset(f > s.start if s.left_open else f >= s.start, X, sp.S.Reals))
        if s.end != sp.oo:
            res = sp.Intersection(res, sp.solveset(f < s.end if s.right_open else f <= s.end, X, sp.S.Reals))
        return res
    raise ValueError(f'множество {s}')


def _rel_tex(rel: str) -> str:
    return {'\\ge': '\\ge ', '\\le': '\\le ', '>': '>', '<': '<'}[rel]


def latex_set(s) -> str:
    """Множество в школьной записи: (−∞; 2] ∪ {3} ∪ (5; +∞)"""
    s = sp.simplify(s)
    if s is sp.S.EmptySet:
        return '\\varnothing'
    if s == sp.S.Reals:
        return '(-\\infty;+\\infty)'
    if isinstance(s, sp.Union):
        parts = sorted(s.args, key=lambda a: float(a.inf) if a.inf != -sp.oo else -1e18)
        return '\\cup '.join(latex_set(a) for a in parts)
    if isinstance(s, sp.FiniteSet):
        return '\\{' + ';\\ '.join(_v(v) for v in sorted(s, key=float)) + '\\}'
    if isinstance(s, sp.Interval):
        lo = '-\\infty' if s.start == -sp.oo else _v(s.start)
        hi = '+\\infty' if s.end == sp.oo else _v(s.end)
        return ('(' if s.left_open else '[') + lo + ';\\ ' + hi + (')' if s.right_open else ']')
    if isinstance(s, sp.Complement):
        return latex_set(s.args[0]) + '\\setminus ' + latex_set(s.args[1])
    return sp.latex(s)


def _v(v) -> str:
    v = _canon(v)
    if v.has(sp.log):
        # 2·ln 2/ln 3 → \log_3 4 (sympy сам раскладывает ln 4 обратно)
        n, d = sp.fraction(sp.together(v))
        if isinstance(d, sp.log) and d.args[0].is_Integer:
            arg = sp.nsimplify(sp.exp(n))
            if arg.is_Rational and 0 < arg < 1 and (1 / arg).is_Integer:
                return f'-\\log_{{{d.args[0]}}}{1 / arg}'
            if arg.is_Rational and arg > 0:
                return f'\\log_{{{d.args[0]}}}{sp.latex(arg) if arg.is_Integer else "{" + sp.latex(arg) + "}"}'
    t = sp.latex(v)
    t = re.sub(r'\\frac\{\\log\{\\left\((\d+) \\right\)\}\}\{\\log\{\\left\((\d+) \\right\)\}\}', r'\\log_{\2}\1', t)
    return t.replace('.', '{,}')


def check(expr, rel, answer, logs=(), lo=-60, hi=60, n=24000) -> bool:
    """
    Независимая проверка: знак выражения на сетке точек совпадает с принадлежностью ответу.
    Считаем в mpmath с двумя точностями: значение 10⁻²⁰⁰⁰ при x ≈ 60 — честный знак, а не ноль;
    нулём считаем только то, что меньше погрешности округления.
    """
    import mpmath
    f = sp.lambdify(X, expr, 'mpmath')
    gs = [sp.lambdify(X, a, 'mpmath') for a in logs]
    pieces = _pieces(answer)
    bounds = [float(b) for b in _bounds(answer)]

    def value(x, dps):
        with mpmath.workdps(dps):
            try:
                v = f(mpmath.mpf(x))
                if any(not (g(mpmath.mpf(x)) > 0) for g in gs):
                    return None
            except (ValueError, ZeroDivisionError, TypeError, OverflowError):
                return None
            if isinstance(v, mpmath.mpc):
                if abs(v.imag) > abs(v.real) * mpmath.mpf(10) ** (-dps // 2) + mpmath.mpf(10) ** (-dps // 2):
                    return None
                v = v.real
            return v if mpmath.isfinite(v) else None

    bad = 0
    for i in range(n + 1):
        x = lo + (hi - lo) * i / n + 1e-7 * math.pi
        v1, v2 = value(x, 40), value(x, 80)
        if v1 is None or v2 is None:
            ok = False
        else:
            zero = abs(v2) <= 1000 * abs(v2 - v1)
            ok = {'\\ge': zero or v2 > 0, '\\le': zero or v2 < 0, '>': not zero and v2 > 0, '<': not zero and v2 < 0}[rel]
        inside = any(a < x < b or (x == a and not lo_open) or (x == b and not hi_open) for a, b, lo_open, hi_open in pieces)
        if ok != inside:
            # граница с точностью до шага сетки не считается ошибкой
            if not any(abs(b - x) < 2 * (hi - lo) / n for b in bounds):
                bad += 1
    return bad == 0


def _pieces(s) -> list:
    """Множество-ответ → [(a, b, a открыт, b открыт)] во float — sympy contains на тысячах точек слишком медленный"""
    if s is sp.S.EmptySet:
        return []
    if isinstance(s, sp.Union):
        return [p for a in s.args for p in _pieces(a)]
    if isinstance(s, sp.FiniteSet):
        return [(float(v), float(v), False, False) for v in s]
    if isinstance(s, sp.Interval):
        return [(float(s.start), float(s.end), s.left_open, s.right_open)]
    if isinstance(s, sp.Complement):
        # ответ вида промежуток без точек: точки на сетку не попадают
        return _pieces(s.args[0])
    raise ValueError(f'множество {s}')


def _bounds(s):
    if isinstance(s, sp.Union):
        return [b for a in s.args for b in _bounds(a)]
    if isinstance(s, sp.Interval):
        return [b for b in (s.start, s.end) if b not in (-sp.oo, sp.oo)]
    if isinstance(s, sp.FiniteSet):
        return list(s)
    if isinstance(s, sp.Complement):
        return _bounds(s.args[0]) + _bounds(s.args[1])
    return []
