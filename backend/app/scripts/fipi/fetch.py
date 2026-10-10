"""
Выкачивает открытый банк ФИПИ (ЕГЭ, профильная математика) в data/fipi:

    data/fipi/tasks.json        — задания как есть: guid, короткий номер, HTML условия, КЭС, тип ответа, картинки
    data/fipi/img/<файл>        — картинки условий

    python -m app.scripts.fipi.fetch            # всё
    python -m app.scripts.fipi.fetch --pages 2  # первые 2 страницы по 100

Страницы и картинки качаются с паузой, уже скачанные картинки не перекачиваются.
"""
import argparse
import json
import re
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

SITE = 'https://ege.fipi.ru'
BANK = f'{SITE}/bank'
PROJ = 'AC437B34557F88EA4115D2F374B0A07B'  # «Математика. Профильный уровень»
PAGE_SIZE = 100
PAUSE = 1.0

DATA = Path(__file__).resolve().parents[3] / 'data' / 'fipi'
HEADERS = {'User-Agent': 'Mozilla/5.0 (online-school bank importer)', 'Accept-Language': 'ru-RU,ru;q=0.9'}

PICTURE = re.compile(r"""ShowPicture\w*\(['"]([^'"]+)['"]""")  # путь бывает и в одинарных, и в двойных кавычках


def fetch_page(client: httpx.Client, page: int) -> tuple[str, int]:
    r = client.post(f'{BANK}/questions.php', data={
        'search': 1, 'pagesize': PAGE_SIZE, 'page': page, 'proj': PROJ,
    })
    r.raise_for_status()
    html = r.content.decode('cp1251')
    total = int(re.search(r'setQCount\((\d+)', html).group(1))
    return html, total


def parse_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, 'lxml')
    tasks = []
    for block in soup.select('div.qblock'):
        short_id = block['id'][1:]
        guid = block.find('input', attrs={'name': 'guid'})['value']
        cell = block.select_one('td.cell_0')
        # картинки вставляются скриптом document.write — достаём пути из вызовов
        images = []
        for script in cell.find_all('script'):
            for path in PICTURE.findall(script.get_text()):
                images.append(path.replace('. ', '.'))
        hint = block.select_one('div.hint')
        # варианты выбора (ILI_STD_SELECTONE) лежат вне cell_0
        variants = [td.get_text(' ', strip=True) for td in block.select('td.varinats-block .distractors-table td')]

        info = soup.find('div', id=f'i{short_id}')
        params = {}
        if info:
            for row in info.select('.task-info-content tr'):
                cells = row.find_all('td')
                if len(cells) == 2:
                    key = cells[0].get_text(strip=True).rstrip(':')
                    params[key] = [d.get_text(strip=True) for d in cells[1].find_all('div')] or [cells[1].get_text(strip=True)]
        tasks.append({
            'guid': guid,
            'id': short_id,
            'hint': hint.get_text(strip=True) if hint else None,
            'html': str(cell.decode_contents()),
            'images': images,
            'variants': variants,
            'kes': params.get('КЭС', []),
            'answer_kind': (params.get('Тип ответа') or [None])[0],
        })
    return tasks


def download_images(client: httpx.Client, tasks: list[dict]) -> None:
    folder = DATA / 'img'
    folder.mkdir(parents=True, exist_ok=True)
    for task in tasks:
        local = []
        for path in task['images']:
            name = f"{task['id']}_{Path(path).name}".replace('(copy1)', '')
            target = folder / name
            if not target.exists():
                r = client.get(f'{SITE}/{path}')  # qfiles_location='../../' — от корня сайта
                if r.status_code != 200:
                    print(f"  картинка {path}: {r.status_code}")
                    continue
                target.write_bytes(r.content)
                time.sleep(PAUSE / 4)
            local.append(name)
        task['image_files'] = local


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', type=int, default=None)
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    tasks: dict[str, dict] = {}
    with httpx.Client(headers=HEADERS, verify=False, timeout=60, follow_redirects=True, trust_env=False) as client:
        page, total = 0, None
        while True:
            html, total = fetch_page(client, page)
            batch = parse_page(html)
            for t in batch:
                tasks[t['guid']] = t
            print(f'страница {page}: {len(batch)} заданий, всего собрано {len(tasks)} из {total}')
            page += 1
            if not batch or page * PAGE_SIZE >= total or (args.pages and page >= args.pages):
                break
            time.sleep(PAUSE)
        result = list(tasks.values())
        download_images(client, result)

    (DATA / 'tasks.json').write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'сохранено {len(result)} заданий в {DATA / "tasks.json"}')


if __name__ == '__main__':
    main()
