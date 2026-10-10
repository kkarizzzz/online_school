"""
Контактный лист рисунков для просмотра глазами (dev-инструмент, нужен resvg-py):

    python -m app.bankgen.preview 1 3 --per 2   # по 2 рисунка на шаблон из номеров 1 и 3 → data/bank/preview.png
"""
import argparse
import json
import re

import resvg_py

from app.bankgen.build import OUT

CELL_W, CELL_H, COLS = 380, 300, 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('numbers', type=int, nargs='*')
    parser.add_argument('--per', type=int, default=2)
    parser.add_argument('--template', default=None)
    parser.add_argument('--source', default='gen')
    args = parser.parse_args()

    bank = json.loads((OUT / 'bank.json').read_text(encoding='utf-8'))
    taken: dict[str, int] = {}
    cells = []
    for e in bank:
        if args.numbers and e['number'] not in args.numbers:
            continue
        if args.template and not e['template'].startswith(args.template):
            continue
        if e['source'] != args.source or not e['figures'] or taken.get(e['template'], 0) >= args.per:
            continue
        taken[e['template']] = taken.get(e['template'], 0) + 1
        for fig in e['figures'][:1]:
            svg = (OUT / 'figures' / fig).read_text(encoding='utf-8')
            cells.append((f"{e['template']} = {e['answer']['display']}", svg))

    rows = (len(cells) + COLS - 1) // COLS
    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{COLS * CELL_W}' height='{rows * CELL_H}'>",
             "<rect width='100%' height='100%' fill='#eee'/>"]
    for i, (title, svg) in enumerate(cells):
        x, y = (i % COLS) * CELL_W, (i // COLS) * CELL_H
        inner = re.sub(r"<svg ([^>]*)width='[\d.]+' height='[\d.]+'", rf"<svg \1x='{x + 5}' y='{y + 22}' width='{CELL_W - 10}' height='{CELL_H - 30}'", svg, count=1)
        parts.append(f"<text x='{x + 6}' y='{y + 15}' font-size='13' font-family='Arial'>{title}</text>")
        parts.append(inner)
    parts.append('</svg>')
    png = resvg_py.svg_to_bytes(svg_string='\n'.join(parts))
    (OUT / 'preview.png').write_bytes(bytes(png))
    print(f'{len(cells)} рисунков → {OUT / "preview.png"}')


if __name__ == '__main__':
    main()
