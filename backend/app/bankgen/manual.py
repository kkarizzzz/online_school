"""
Задания ФИПИ, решённые вручную: единичные формулировки, под которые нет смысла заводить генератор
(формула в условии — картинкой, редкий прототип). Решение и ответ — в data/fipi/manual.json
(template = «manual.<номер>»), ответ первой части всё равно сверяется с ФИПИ.
"""
from fractions import Fraction

from app.bankgen.core import Rendered, Template, dec


class ManualTask(Template):
    variants = False
    def match(self, task):
        return None

    def solve(self, p):
        a = p['answer']
        return a if isinstance(a, (str, dict)) else Fraction(str(a))

    def render(self, p):
        """
        Условие — p['condition'] (переписанное с формулами в LaTeX вместо картинок ФИПИ), иначе остаётся условие ФИПИ.
        Рисунок — p['figure'] = {template, params}: рисунок шаблона с теми же данными
        """
        ans = self.solve(p)
        shown = ans['display'] if isinstance(ans, dict) else dec(ans) if not isinstance(ans, str) else ans
        figures = {}
        cond = p.get('condition', '')
        if p.get('figure'):
            from app.bankgen.registry import TEMPLATES, extra_templates
            by = {t.code: t for ts in TEMPLATES.values() for t in ts} | {t.code: t for t, _ in extra_templates()}
            other = by[p['figure']['template']].render(p['figure']['params'])
            figures = dict(list(other.figures.items())[:1])
            if cond and figures:
                cond += f'\n\n![](figure://{next(iter(figures))})'
        return Rendered(cond, p['solution'] + f'\n\n**Ответ:** {shown}.', figures)

    def sample(self, rng):
        return None


def _make(n: int, detailed: bool = False) -> ManualTask:
    cls = type(f'Manual{n}', (ManualTask,), {'number': n, 'topic': 'Разные задачи', 'code': f'manual.{n}', 'detailed': detailed})
    return cls()


TEMPLATES = [_make(n) for n in range(1, 13)] + [_make(n, detailed=True) for n in range(13, 20)]
EXTRA = []
