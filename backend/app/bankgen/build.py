"""
Сборка банка: задания ФИПИ + аналоги с другими числами → data/bank.

    python -m app.bankgen.build                 # всё, с проверкой ответов на сайте ФИПИ
    python -m app.bankgen.build --offline       # без обращения к ФИПИ (только кэш проверок)
    python -m app.bankgen.build --only 6 7      # только эти номера
    python -m app.bankgen.build --variants 3    # аналогов на каждое задание ФИПИ

На выходе:
    data/bank/bank.json        — задания для импорта (app/scripts/import_bank.py)
    data/bank/figures/*.svg    — наши рисунки к аналогам
    data/bank/report.md        — что не распознано и где ответ не сошёлся с ФИПИ

Задание ФИПИ попадает в банк, только если шаблон его узнал и ФИПИ подтвердил ответ
(для второй части — если ответ прошёл независимую проверку шаблона).
"""
import argparse
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from app.bankgen.core import Template, answer_json
from app.bankgen.registry import TEMPLATES, extra_templates
from app.scripts.fipi.classify import exam_number
from app.scripts.fipi.fetch import DATA as FIPI

OUT = FIPI.parent / 'bank'


def _seed(*parts) -> int:
    return int(hashlib.sha1('|'.join(map(str, parts)).encode()).hexdigest()[:12], 16)


def _figures(rendered, prefix: str, out: Path) -> tuple[str, str, list[str]]:
    """figure://name → figure://<prefix>-name.svg, SVG пишем в out"""
    names = []
    cond, sol = rendered.condition, rendered.solution
    for name, svg in rendered.figures.items():
        file = f'{prefix}-{name}.svg'
        (out / file).write_text(svg, encoding='utf-8')
        cond = cond.replace(f'figure://{name})', f'figure://{file})')
        sol = sol.replace(f'figure://{name})', f'figure://{file})')
        names.append(file)
    return cond, sol, names


BLOCK_IMAGE = re.compile(r'(^|\n)[ \t]*!\[\]\(fipi://[^)]+\)')


def _own_pictures(t: Template, params, task: dict, solution: str, figs: list[str],
                  out: Path) -> tuple[str, str, list[str], list[str]]:
    """
    Картинки ФИПИ мелкие (≈150 px) и растровые. Вместо них — своё: условие из параметров шаблона (формулы в LaTeX,
    рисунок — наш SVG по тем же данным), а если шаблон условие не пишет — хотя бы наш рисунок вместо рисунка ФИПИ.
    Возвращает (условие, решение, оставшиеся картинки ФИПИ, наши рисунки)
    """
    own = dict(params) if isinstance(params, dict) else params
    if isinstance(own, dict):
        own.pop('_fipi', None)
    try:
        rendered = t.render(own)
    except Exception:  # noqa: BLE001 — остаёмся с картинками ФИПИ
        rendered = None
    if rendered is not None and rendered.condition.strip() and 'fipi://' not in rendered.condition \
            and (rendered.figures or 'рисун' not in rendered.condition.lower()):
        # решение тоже из этого рендера: у задач части 2 рисунок переезжает из решения в условие
        cond, sol, names = _figures(rendered, f'fipi-{task["id"]}', out)
        return cond, sol, [], names
    cond = _formulas(task['condition'])
    if len(BLOCK_IMAGE.findall(cond)) == 1 and figs:
        cond = BLOCK_IMAGE.sub(lambda m: f'{m.group(1)}![](figure://{figs[0]})', cond)
    used = set(re.findall(r'fipi://([^)]+)\)', cond))
    return cond, solution, [i for i in task['images'] if i in used], figs


FORMULAS_FILE = FIPI / 'formulas.json'


def _formulas(text: str) -> str:
    """Формулы-картинки ФИПИ → LaTeX (переписаны вручную в data/fipi/formulas.json): отдельной строкой — $$…$$, в тексте — $…$"""
    if not FORMULAS_FILE.exists():
        return text
    table = json.loads(FORMULAS_FILE.read_text(encoding='utf-8'))

    def sub(m):
        tex = table.get(m.group(2))
        if tex is None:
            return m.group(0)
        if m.group(1):
            return f'{m.group(1)}$${tex}$$'
        tail = tex[-1] if tex[-1] in '.,;' else ''          # точка в конце картинки — после формулы
        return f'${tex[:len(tex) - len(tail)]}${tail}'
    return re.sub(r'((?:^|\n)[ \t]*)?!\[\]\(fipi://([^)]+)\)', sub, text)


def entry(t: Template, *, source: str, external_id: str, condition: str, solution: str, answer,
          figures: list[str], fipi_images: list[str] = (), origin: str | None = None, topic: str | None = None) -> dict:
    return {
        'number': t.number, 'topic': topic or t.topic, 'template': t.code, 'difficulty': t.difficulty,
        'source': source, 'external_id': external_id, 'origin': origin,
        'answer_type': 'detailed' if t.detailed else 'short',
        'condition': condition, 'solution': solution,
        'answer': answer_json(answer) if not isinstance(answer, dict) else answer,
        'figures': figures, 'fipi_images': list(fipi_images),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--only', type=int, nargs='*')
    parser.add_argument('--variants', type=int, default=2)
    args = parser.parse_args()

    oracle = None
    if not args.offline:
        from app.scripts.fipi.oracle import Oracle
        oracle = Oracle()

    figures_dir = OUT / 'figures'
    figures_dir.mkdir(parents=True, exist_ok=True)
    tasks = json.loads((FIPI / 'normalized.json').read_text(encoding='utf-8'))

    manual_path = FIPI / 'manual.json'
    manual = json.loads(manual_path.read_text(encoding='utf-8')) if manual_path.exists() else {}
    by_code = {t.code: t for ts in TEMPLATES.values() for t in ts}
    by_code.update({t.code: t for t, _ in extra_templates()})

    result, report = [], defaultdict(list)
    stats = Counter()
    per_template = Counter()

    def variant(t: Template, seed: int, vid: str, origin: str | None) -> bool:
        """Аналог с новыми числами; ошибка шаблона — в отчёт, сборка продолжается"""
        try:
            p, a = t.generate(random.Random(seed))
            r = t.render(p)
        except Exception as e:  # noqa: BLE001
            report['ошибка генерации'].append((t.number, vid, f'{t.code}: {e!r}'))
            return False
        cond, sol, figs = _figures(r, f'gen-{vid}', figures_dir)
        result.append(entry(t, source='gen', external_id=vid, condition=cond, solution=sol, answer=a, figures=figs, origin=origin))
        return True
    try:
        for task in tasks:
            number = exam_number(task)
            if number is None or (args.only and number not in args.only):
                continue
            stats[f'{number}:всего'] += 1
            found = None
            if task['id'] in manual:
                # числа сняты с рисунка вручную; правильность всё равно подтверждает ФИПИ
                m = manual[task['id']]
                t = by_code.get(m['template'])
                if t is not None:
                    found = (t, _tuples(m['params']))
            # сначала шаблоны своего номера, потом остальные: классификатор по КЭС иногда путает 4 и 5, 9 и 10
            candidates = TEMPLATES.get(number, []) + [t for n, ts in TEMPLATES.items() if n != number for t in ts]
            for t in candidates if not found else []:
                if t.detailed != (not task['short']):
                    continue
                params = t.match(task)
                if params is not None:
                    found = (t, params)
                    break
            if not found:
                report['не распознано'].append((number, task['id'], task['condition'][:300]))
                continue
            t, params = found
            try:
                answer = t.solve(params)
                ok_local = t.verify(params, answer)
            except Exception as e:  # noqa: BLE001 — в отчёт, сборку не роняем
                report['ошибка решения'].append((number, task['id'], f'{t.code}: {e!r}'))
                continue
            if not ok_local:
                report['не прошло проверку шаблона'].append((number, task['id'], t.code))
                continue
            if task['short'] and not t.detailed:
                shown = answer_json(answer)['display']
                if oracle is not None:
                    if not oracle.check(task['guid'], shown):
                        report['ФИПИ: неверно'].append((number, task['id'], f'{t.code}: {shown}'))
                        continue
                elif shown not in (oracle_cache := _cached()).get(task['guid'], {}) \
                        or not oracle_cache[task['guid']][shown]:
                    report['ФИПИ: не проверено'].append((number, task['id'], f'{t.code}: {shown}'))
                    continue
            try:
                rendered = t.render(params)
            except Exception as e:  # noqa: BLE001
                report['ошибка решения'].append((number, task['id'], f'{t.code}: render {e!r}'))
                continue
            stats[f'{number}:в банке'] += 1
            per_template[t.code] += 1
            _, solution, figs = _figures(rendered, f'fipi-{task["id"]}', figures_dir)
            condition, images = task['condition'], task['images']
            if images:
                condition, solution, images, figs = _own_pictures(t, params, task, solution, figs, figures_dir)
            result.append(entry(t, source='fipi', external_id=task['id'], condition=condition,
                                solution=solution, answer=answer, figures=figs, fipi_images=images,
                                topic=params.get('topic') if isinstance(params, dict) else None))

            for k in range(args.variants if t.variants else 0):
                variant(t, _seed(task['id'], k), f'{task["id"]}-v{k + 1}', task['id'])

        # Прототипы, которых нет в открытом банке ФИПИ (по разбору других банков) — только аналоги
        for t, count in extra_templates():
            if args.only and t.number not in args.only:
                continue
            for k in range(count):
                if variant(t, _seed(t.code, k), f'{t.code}-{k + 1}', None):
                    per_template[t.code] += 1
    finally:
        if oracle is not None:
            oracle.close()

    if args.only and (OUT / 'bank.json').exists():
        # частичная сборка: остальные номера берём из прошлой сборки
        old = json.loads((OUT / 'bank.json').read_text(encoding='utf-8'))
        result = [e for e in old if e['number'] not in args.only] + result
    _levels(result)
    (OUT / 'bank.json').write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
    _write_report(report, stats, per_template, len(result))


# Сложность по объёму решения среди заданий того же номера: в части 1 — уровни 1–3, в № 13–17 — 1–4
# (границы — доли заданий номера). У № 18 и 19 уровни расставлены вручную по семействам (n18.py, n19.py)
LEVEL_SHARES = {**{n: (0.4, 0.8) for n in range(1, 13)}, **{n: (0.2, 0.55, 0.88) for n in range(13, 18)}}


def _levels(entries: list[dict]) -> None:
    def size(e):
        text = re.sub(r'\\[a-zA-Z]+|[{}$\s]', '', e['solution'])
        return len(text)
    by_number = defaultdict(list)
    for e in entries:
        if e['number'] in LEVEL_SHARES:
            by_number[e['number']].append(e)
    for number, group in by_number.items():
        group.sort(key=size)
        for i, e in enumerate(group):
            e['difficulty'] = 1 + sum(i >= share * len(group) for share in LEVEL_SHARES[number])


def _tuples(v):
    """JSON-списки точек → кортежи; строки «1/2» → Fraction"""
    from fractions import Fraction
    if isinstance(v, dict):
        return {k: _tuples(x) for k, x in v.items()}
    if isinstance(v, list):
        return tuple(_tuples(x) for x in v) if all(not isinstance(x, (list, dict)) for x in v) and len(v) == 2 else [_tuples(x) for x in v]
    if isinstance(v, str) and '/' in v and v.replace('/', '').replace('-', '').isdigit():
        return Fraction(v)
    return v


_CACHE = None


def _cached() -> dict:
    global _CACHE
    if _CACHE is None:
        path = FIPI / 'checked.json'
        _CACHE = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    return _CACHE


def _write_report(report, stats, per_template, total) -> None:
    lines = [f'# Сборка банка: {total} заданий', '', '| № | ФИПИ | в банке |', '|---|---|---|']
    for n in range(1, 20):
        lines.append(f'| {n} | {stats[f"{n}:всего"]} | {stats[f"{n}:в банке"]} |')
    for title, rows in report.items():
        lines += ['', f'## {title} ({len(rows)})', '']
        for number, tid, text in sorted(rows):
            lines.append(f'- **{number}** `{tid}` {text}'.replace('\n', ' '))
    lines += ['', '## Шаблоны', ''] + [f'- `{code}`: {n}' for code, n in sorted(per_template.items())]
    (OUT / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines[:24]))
    for title, rows in report.items():
        print(f'{title}: {len(rows)}')


if __name__ == '__main__':
    main()
