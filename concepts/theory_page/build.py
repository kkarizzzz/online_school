"""Собирает data.js и ORDER.md из карты ЕГЭ (ege-map.html).

Порядок тем: уровень (0 → 3), затем ветка (1 → 5), затем номер темы внутри ветки.
На уровне 3 ветки 1 и 5 поменяны местами (см. BRANCH_ORDER).

    python build.py [путь к ege-map.html]   # по умолчанию concepts/math_plan/ege-map.html
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE.parent / 'math_plan' / 'ege-map.html'

BRANCHES = ['Числа и теория чисел', 'Уравнения и неравенства', 'Функции и анализ',
            'Геометрия', 'Прикладная математика и вероятность']
# Порядок веток внутри уровня (индексы с нуля); по умолчанию 1 → 5
BRANCH_ORDER = {3: [4, 1, 2, 3, 0]}
branch_order = lambda level: BRANCH_ORDER.get(level, list(range(len(BRANCHES))))

LEVELS = [
    {'name': 'База', 'desc': '1–6 класс'},
    {'name': 'Фундамент', 'desc': '7–9 класс, алгебра и геометрия'},
    {'name': 'База ЕГЭ', 'desc': 'Первая часть, №1–12'},
    {'name': 'Профиль', 'desc': 'Вторая часть, №13–19'},
]

html = SRC.read_text(encoding='utf-8')
start = html.index('const DATA = ') + len('const DATA = ')
data, _ = json.JSONDecoder().raw_decode(html[start:])

nums = lambda s: [int(n) for n in re.findall(r'№\s?(\d+)', s)]
strip_no = lambda s: re.sub(r'\s*\([^()]*№[^()]*\)', '', s).strip()


def split_note(s):
    """«Название (уточнение)» → ('Название', 'уточнение')."""
    m = re.match(r'^(.*?)\s*\(([^()]*)\)\s*$', s)
    return (m.group(1), m.group(2)) if m and m.group(1) else (s, '')


def outline(nodes):
    return [{'t': n['t'], **({'c': outline(n['c'])} if n.get('c') else {})} for n in nodes]


topics = []
for bi, branch in enumerate(data):
    for lv in branch['c']:
        level = int(re.search(r'УРОВЕНЬ\s*(\d)', lv['t']).group(1))
        for t in lv['c']:
            tid, tname = re.match(r'^(\d+\.\d+)\.\s*(.*)$', t['t']).groups()
            lessons = []
            for s in t.get('c', []):
                sid, sname = re.match(r'^(\d+\.\d+\.\d+)\.\s*(.*)$', s['t']).groups()
                name, note = split_note(strip_no(sname))
                lessons.append({'id': sid, 'name': name, 'note': note, 'outline': outline(s.get('c', []))})
            topics.append({'id': tid, 'b': bi, 'l': level, 'name': strip_no(tname),
                           'tasks': nums(t['t']) or nums(lv['t']), 'lessons': lessons})

key = lambda t: (t['l'], branch_order(t['l']).index(t['b']), *map(int, t['id'].split('.')))
topics.sort(key=key)

for i, lv in enumerate(LEVELS):
    lv['order'] = branch_order(i)
payload = {'branches': BRANCHES, 'levels': LEVELS, 'topics': topics}
(BASE / 'static' / 'data.js').write_text(
    '// Сгенерировано build.py из карты ЕГЭ — не редактировать вручную\n'
    'window.THEORY = ' + json.dumps(payload, ensure_ascii=False) + ';\n', encoding='utf-8')

# ORDER.md
lines = ['# Порядок тем — теория, математика (профиль)', '',
         'Сортировка: **уровень** (0 → 3) → **ветка** (1 → 5) → **номер темы** внутри ветки.',
         'Исключение: на уровне 3 ветка 5 идёт первой, ветка 1 — последней (5 → 2 → 3 → 4 → 1).',
         'Каждая тема — модуль, каждая подтема (x.y.z) — отдельный урок.', '',
         f'Итого: тем — {len(topics)}, уроков — {sum(len(t["lessons"]) for t in topics)}.', '']
n = 0
for li, lv in enumerate(LEVELS):
    lt = [t for t in topics if t['l'] == li]
    lines += [f'## Уровень {li} · {lv["name"]} — {lv["desc"]}', '',
              f'Тем: {len(lt)}, уроков: {sum(len(t["lessons"]) for t in lt)}', '']
    for bi in branch_order(li):
        bname = BRANCHES[bi]
        bt = [t for t in lt if t['b'] == bi]
        if not bt:
            continue
        lines += [f'### Ветка {bi + 1} · {bname}', '', '| # | Тема | Уроков | ЕГЭ |', '|---|---|---|---|']
        for t in bt:
            n += 1
            tasks = ', '.join(f'№{x}' for x in t['tasks']) or '—'
            lines.append(f'| {n} | {t["id"]}. {t["name"]} | {len(t["lessons"])} | {tasks} |')
        lines.append('')
(BASE / 'ORDER.md').write_text('\n'.join(lines), encoding='utf-8')

print(len(topics), 'тем,', sum(len(t['lessons']) for t in topics), 'уроков')
