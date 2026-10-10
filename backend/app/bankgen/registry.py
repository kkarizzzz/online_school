"""Все шаблоны по номерам ЕГЭ"""
import importlib

from app.bankgen.core import Template

MODULES = [f'app.bankgen.n{n:02d}' for n in range(1, 20)] + ['app.bankgen.manual']

TEMPLATES: dict[int, list[Template]] = {}
_EXTRA: list[tuple[Template, int]] = []

for name in MODULES:
    try:
        module = importlib.import_module(name)
    except ModuleNotFoundError as e:
        if e.name != name:
            raise
        continue
    for t in getattr(module, 'TEMPLATES', []):
        TEMPLATES.setdefault(t.number, []).append(t)
    _EXTRA.extend(getattr(module, 'EXTRA', []))


def extra_templates() -> list[tuple[Template, int]]:
    """(шаблон, сколько аналогов) — прототипы без задания-оригинала в открытом банке ФИПИ"""
    return _EXTRA
