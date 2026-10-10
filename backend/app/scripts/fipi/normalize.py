"""
data/fipi/tasks.json (сырой HTML) → data/fipi/normalized.json (Markdown + LaTeX).

    python -m app.scripts.fipi.normalize

Вёрстка ФИПИ — экспорт из Word: таблицы без рамки — это раскладка «текст слева, рисунок справа»,
их разворачиваем в абзацы; таблицы с рамкой — настоящие данные, из них делаем Markdown-таблицу.
Картинка вставляется в условие ссылкой ![](fipi://<файл>), импорт заменит её на storage://.
"""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

from app.scripts.fipi.fetch import DATA, PICTURE
from app.scripts.fipi.mathml import math_to_latex


def _inline(node, images: list[str]) -> str:
    """Содержимое абзаца: текст, формулы $...$, картинки"""
    out = []
    for child in node.children:
        if isinstance(child, NavigableString):
            # \u0432 \u0447\u0430\u0441\u0442\u0438 \u0437\u0430\u0434\u0430\u043d\u0438\u0439 Word \u043e\u0441\u0442\u0430\u0432\u0438\u043b \u0432 \u0442\u0435\u043a\u0441\u0442\u0435 \u00ab?xml:namespace prefix = m ns = "..." /\u00bb
            out.append(re.sub(r'\??xml:namespace.*?MathML"\s*/', '', str(child)).replace('\u00a0', ' '))
            continue
        name = child.name.split(':')[-1]
        if name == 'math':
            out.append(_math(math_to_latex(child)))
        elif name == 'script':
            for _ in PICTURE.findall(child.get_text()):
                if images:
                    name = images.pop(0)
                    # innerimg — формула картинкой посреди строки, её оставляем в тексте; остальное — рисунок отдельным абзацем
                    out.append(f' ![](fipi://{name}) ' if 'innerimg' in name or (child.find_parent(['p', 'td']) or node).get_text(strip=True) else f'\n\n![](fipi://{name})\n\n')
        elif name == 'br':
            out.append(' ')
        elif name == 'b':
            out.append('**' + _inline(child, images).strip() + '** ')
        elif name == 'i':
            text = _inline(child, images).strip()
            out.append(f'*{text}* ' if text else '')
        elif name in ('sub', 'sup') and child.find('script'):
            out.append(_inline(child, images))  # внутри — картинка-формула, индекс тут ни при чём
        elif name == 'sub':
            out.append('$_{' + child.get_text(strip=True) + '}$' if child.get_text(strip=True) else '')
        elif name == 'sup':
            out.append('$^{' + child.get_text(strip=True) + '}$' if child.get_text(strip=True) else '')
        else:
            out.append(_inline(child, images))
    return ''.join(out)


TRAILING = re.compile(r'(?:\{,\}|[.,;:])$')


def _math(tex: str) -> str:
    """Формула в $...$; точку или запятую в конце формулы выносим в текст, чистое тире — тоже текст"""
    tail = ''
    while (m := TRAILING.search(tex)):
        tail = (',' if m.group() == '{,}' else m.group()) + tail
        tex = tex[:m.start()].rstrip()
    if tex in ('—', '-', '–'):
        return ' — ' + tail
    return (' $' + tex + '$' if tex else '') + tail + ' '


def _block(node: Tag, images: list[str]) -> list[str]:
    paragraphs = []
    for child in node.children:
        if isinstance(child, NavigableString):
            if child.strip():
                paragraphs.append(str(child))
            continue
        name = child.name
        if name == 'table':
            if child.get('border') == '1':
                paragraphs.append(_table(child, images))
            else:
                for td in child.find_all('td'):
                    paragraphs.extend(_block(td, images))
        elif name in ('p', 'div', 'span', 'a'):
            paragraphs.append(_inline(child, images))
        elif name == 'script':
            paragraphs.append(_inline(BeautifulSoup(f'<p>{child}</p>', 'lxml').p, images))
        else:
            paragraphs.append(_inline(child, images))
    return paragraphs


def _table(table: Tag, images: list[str]) -> str:
    rows = []
    for tr in table.find_all('tr'):
        cells = [_clean(' '.join(_block(td, images))).replace('|', '\\|').replace('\n', ' ') for td in tr.find_all('td')]
        rows.append('| ' + ' | '.join(cells) + ' |')
    if rows:
        width = rows[0].count('|') - 1
        rows.insert(1, '|' + ' --- |' * width)
    return '\n'.join(rows)


def _clean(text: str) -> str:
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r' +([.,;:?)])', r'\1', text)  # «!» не трогаем: с него начинается картинка ![](...)
    text = re.sub(r'\$ *([.,;:])', r'$\1', text)
    text = re.sub(r'\( +', '(', text)
    return text.strip()


def to_markdown(html: str, images: list[str]) -> str:
    soup = BeautifulSoup(f'<div>{html}</div>', 'lxml')
    queue = list(images)
    paragraphs = [_clean(p) for p in _block(soup.div, queue)]
    text = '\n\n'.join(p for p in paragraphs if p)
    text = re.sub(r'(\$|\w)\s*,\s*$', r'\1.', text)  # «…=6$,» в конце условия — опечатка вёрстки
    for rest in queue:  # картинка, которую не нашли в тексте, — в конец
        text += f'\n\n![](fipi://{rest})'
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def plain(markdown: str) -> str:
    """Текст для сопоставления с шаблонами: без картинок, LaTeX упрощён до чисел и букв"""
    text = re.sub(r'!\[\]\([^)]*\)', ' ', markdown)
    return re.sub(r'\s+', ' ', text).strip()


def main() -> None:
    raw = json.loads((DATA / 'tasks.json').read_text(encoding='utf-8'))
    result = []
    for t in raw:
        md = to_markdown(t['html'], t.get('image_files', []))
        result.append({
            'id': t['id'],
            'guid': t['guid'],
            'kes': [k.split(' ', 1)[0] for k in t['kes']],
            'short': t['answer_kind'] == 'Краткий ответ',
            'condition': md,
            'images': t.get('image_files', []),
        })
    (DATA / 'normalized.json').write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(result)} заданий → {DATA / "normalized.json"}')


if __name__ == '__main__':
    main()
