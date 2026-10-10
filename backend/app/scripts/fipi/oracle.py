"""
Проверка ответа на сайте ФИПИ (та же, что кнопка «Проверить» в открытом банке).

solve.php отвечает: 3 — верно, 2 — неверно; без сессии — «пользователь не определён»,
поэтому сначала открываем страницу банка за cookie. Результаты кэшируются в data/fipi/checked.json,
повторно один и тот же ответ не отправляем.
"""
import json
import time

import httpx

from app.scripts.fipi.fetch import BANK, DATA, HEADERS, PROJ

CACHE = DATA / 'checked.json'


class Oracle:
    def __init__(self, pause: float = 0.4):
        self.pause = pause
        self.cache: dict[str, dict[str, bool]] = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}
        self.client: httpx.Client | None = None

    def _connect(self) -> httpx.Client:
        if self.client is None:
            self.client = httpx.Client(headers=HEADERS, verify=False, timeout=60, follow_redirects=True, trust_env=False)
            self.client.get(f'{BANK}/index.php', params={'proj': PROJ})
            self.client.get(f'{BANK}/questions.php', params={'proj': PROJ, 'page': 0, 'pagesize': 10})
        return self.client

    def check(self, guid: str, answer: str) -> bool:
        known = self.cache.setdefault(guid, {})
        if answer in known:
            return known[answer]
        client = self._connect()
        r = client.post(f'{BANK}/solve.php', files={
            'guid': (None, guid), 'answer': (None, answer), 'ajax': (None, '1'), 'proj': (None, PROJ),
        })
        text = r.content.decode('cp1251').strip()
        if text not in ('2', '3'):
            raise RuntimeError(f'ФИПИ ответил «{text}» на {guid}')
        known[answer] = text == '3'
        time.sleep(self.pause)
        return known[answer]

    def save(self) -> None:
        CACHE.write_text(json.dumps(self.cache, ensure_ascii=False, indent=1), encoding='utf-8')

    def close(self) -> None:
        self.save()
        if self.client:
            self.client.close()
