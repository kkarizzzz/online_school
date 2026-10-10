"""
MathML (как его отдаёт ФИПИ: префикс m:, обёртки semantics/mstyle) → LaTeX.

Покрывает то, что реально встречается в банке профильной математики:
mi, mn, mo, mtext, mrow, mfrac, msup, msub, msubsup, msqrt, mroot, mover, mfenced, mtable.
"""
import re

from bs4 import NavigableString, Tag

# Символы, которые в LaTeX пишутся командой
SYMBOLS = {
    '−': '-', '–': '-', '·': '\\cdot ', '⋅': '\\cdot ', '×': '\\cdot ', '∙': '\\cdot ',
    '≤': '\\le ', '≥': '\\ge ', '≠': '\\ne ', '≈': '\\approx ', '∞': '\\infty ',
    '∈': '\\in ', '∉': '\\notin ', '∪': '\\cup ', '∩': '\\cap ', '⊂': '\\subset ', '∅': '\\varnothing ',
    '→': '\\to ', '⇒': '\\Rightarrow ', '⇔': '\\Leftrightarrow ', '∠': '\\angle ', '°': '^\\circ',
    '△': '\\triangle ', '∆': '\\triangle ', '⊥': '\\perp ', '∥': '\\parallel ', '‖': '\\parallel ',
    'π': '\\pi ', 'α': '\\alpha ', 'β': '\\beta ', 'γ': '\\gamma ', 'φ': '\\varphi ', 'ϕ': '\\varphi ',
    'ω': '\\omega ', 'ρ': '\\rho ', 'λ': '\\lambda ', 'μ': '\\mu ', 'ν': '\\nu ', 'θ': '\\theta ',
    'Δ': '\\Delta ', 'δ': '\\delta ', 'ε': '\\varepsilon ', 'σ': '\\sigma ', 'τ': '\\tau ', 'η': '\\eta ',
    'ξ': '\\xi ', 'Ω': '\\Omega ', 'Φ': '\\Phi ', 'ψ': '\\psi ',
    ' ': ' ', ' ': ' ', '⁡': '', '⁢': '', '​': '', '′': "'", '″': "''",
    '{': '\\{', '}': '\\}', '%': '\\%', '…': '\\ldots ', '⋯': '\\cdots ',
}
FUNCTIONS = {'sin', 'cos', 'tg', 'ctg', 'tan', 'cot', 'log', 'ln', 'lg', 'arcsin', 'arccos', 'arctg', 'arcctg',
             'max', 'min', 'exp'}
ACCENTS = {'→': '\\overrightarrow', '¯': '\\overline', '‾': '\\overline', '^': '\\hat', '~': '\\tilde',
           '⌒': '\\overset{\\frown}', '⏜': '\\overset{\\frown}', '̑': '\\overset{\\frown}'}


def _name(tag: Tag) -> str:
    return tag.name.split(':')[-1]


def _symbols(text: str) -> str:
    return ''.join(SYMBOLS.get(ch, ch) for ch in text)


def _children(tag: Tag) -> list[Tag]:
    return [c for c in tag.children if isinstance(c, Tag)]


def _group(tex: str) -> str:
    tex = tex.strip()
    return tex if len(tex) == 1 else '{' + tex + '}'


def convert(tag: Tag) -> str:
    name = _name(tag)
    kids = _children(tag)

    if name in ('math', 'mrow', 'mstyle', 'mpadded', 'mphantom', 'menclose', 'merror'):
        return ''.join(convert(k) for k in kids)
    if name == 'semantics':
        return convert(kids[0]) if kids else ''
    if name in ('annotation', 'annotation-xml', 'mspace'):
        return ' ' if name == 'mspace' else ''

    if name == 'mi':
        text = tag.get_text().strip()
        if text in FUNCTIONS:
            return {'tg': '\\operatorname{tg}', 'ctg': '\\operatorname{ctg}', 'arctg': '\\operatorname{arctg}',
                    'arcctg': '\\operatorname{arcctg}'}.get(text, '\\' + text) + ' '
        if len(text) > 1 and text.isalpha() and text.isascii():
            return '\\mathrm{' + text + '}'
        if tag.get('mathvariant') == 'normal' and text.isalpha():
            return '\\mathrm{' + text + '}'
        return _symbols(text)
    if name == 'mn':
        return tag.get_text().strip().replace('.', ',').replace(',', '{,}')
    if name == 'mo':
        text = tag.get_text().strip()
        if text in ('(', ')', '[', ']', '|'):
            return text
        if text in FUNCTIONS:
            return '\\' + text + ' '
        return _symbols(text)
    if name == 'mtext':
        text = re.sub('[  ]', ' ', tag.get_text()).replace('​', '')
        if not text.strip():
            return ' ' if text else ''
        return '\\text{' + text + '}'

    if name == 'mfrac':
        return '\\frac{' + convert(kids[0]).strip() + '}{' + convert(kids[1]).strip() + '}'  # без скобок \frac kx склеивается в \frackx
    if name == 'msqrt':
        return '\\sqrt{' + ''.join(convert(k) for k in kids) + '}'
    if name == 'mroot':
        return '\\sqrt[' + convert(kids[1]) + ']{' + convert(kids[0]) + '}'
    if name == 'msup':
        return _base(kids[0]) + '^' + _group(convert(kids[1]))
    if name == 'msub':
        return _base(kids[0]) + '_' + _group(convert(kids[1]))
    if name == 'msubsup':
        return _base(kids[0]) + '_' + _group(convert(kids[1])) + '^' + _group(convert(kids[2]))
    if name in ('mover', 'munder', 'munderover'):
        base = convert(kids[0])
        mark = kids[1].get_text().strip() if len(kids) > 1 else ''
        if name == 'mover' and mark in ACCENTS:
            return ACCENTS[mark] + '{' + base + '}'
        if name == 'mover':
            return '\\overset{' + convert(kids[1]) + '}{' + base + '}'
        if name == 'munder':
            return '\\underset{' + convert(kids[1]) + '}{' + base + '}'
        return base + '_' + _group(convert(kids[1])) + '^' + _group(convert(kids[2]))

    if name == 'mfenced':
        open_, close = tag.get('open', '('), tag.get('close', ')')
        inner = ','.join(convert(k) for k in kids) if kids and not (len(kids) == 1) else ''.join(convert(k) for k in kids)
        return _fence(open_, '\\left') + inner + _fence(close, '\\right')
    if name == 'mtable':
        rows = []
        for tr in kids:
            rows.append(' & '.join(convert(td) for td in _children(tr)) if _name(tr) == 'mtr' else convert(tr))
        return '\\begin{array}{l}' + ' \\\\ '.join(rows) + '\\end{array}'
    if name in ('mtr', 'mtd'):
        return ''.join(convert(k) for k in kids)

    return ''.join(convert(k) for k in kids) or _symbols(tag.get_text())


def _base(tag: Tag) -> str:
    tex = convert(tag)
    if _name(tag) in ('mrow', 'mfenced') and len(tex) > 1 and not tex.startswith('\\left'):
        return '{' + tex + '}'
    return tex


def _fence(ch: str, side: str) -> str:
    if not ch:
        return side + '.'
    return side + {'{': '\\{', '}': '\\}'}.get(ch, ch)


def math_to_latex(tag: Tag) -> str:
    tex = convert(tag)
    return _tidy(tex)


def _tidy(tex: str) -> str:

    tex = re.sub(r'[ \t]+', ' ', tex).strip()
    tex = re.sub(r' ?(\\(?:le|ge|ne|cdot|in|cup|cap|to))(?![a-zA-Z]) ?', r' \1 ', tex)
    tex = re.sub(r' +', ' ', tex)
    tex = tex.replace('\\text{ }', ' ')
    tex = re.sub(r'\\text(?![a-zA-Z{])', '', tex)  # «\text» без аргумента — остаток пустого mtext
    return tex.strip()


def is_math(node) -> bool:
    return isinstance(node, Tag) and _name(node) == 'math' and not isinstance(node, NavigableString)
