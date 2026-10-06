# Концепт: вкладка «Теория»

Макет переделанной страницы теории в личном кабинете по карте ЕГЭ (5 веток × 4 уровня, 72 темы, 315 уроков). Карточка урока ведёт на `concepts/lesson_page`.

## Файлы

- `static/index.html` — макет страницы (оболочка кабинета как во `frontend/src`).
- `static/shell.css` — оболочка кабинета (шрифты, сайдбар). Её же использует `lesson_page`.
- `static/styles.css`, `static/app.js` — стили и логика страницы.
- `static/data.js` — темы и уроки, уже отсортированы. Генерируется `build.py`, руками не править.
- `static/summaries.js` — мини-конспекты уроков, написанные вручную (пока темы 3.2 и 3.3). Для остальных конспект собирается из пунктов плана.
- `ORDER.md` — порядок тем: уровень → ветка 1–5 → номер темы. Генерируется `build.py`.
- `build.py` — пересобирает `data.js` и `ORDER.md` из `concepts/math_plan/ege-map.html`.

## Запуск

Нужен только Python. Сервер запускается **из корня репозитория** — страница подтягивает шрифты и логотип из `frontend/` по относительным путям, поэтому корень должен быть доступен по HTTP:

```bash
python -m http.server 8200 --bind 127.0.0.1
```

Открыть http://localhost:8200/concepts/theory_page/static/index.html

Остановить — `Ctrl+C`. В Claude Code то же самое запускает конфиг `concept-theory` из `.claude/launch.json`.

> Открывать `index.html` двойным кликом (`file://`) не стоит: шрифты из `frontend/` не подгрузятся.

## Пересборка данных

Данные берутся из плана в `concepts/math_plan` (см. [его README](../math_plan/README.md)). После правки `plan.txt`:

```bash
python concepts/math_plan/parse.py
```

```bash
python concepts/theory_page/build.py
```

`build.py` по умолчанию читает `concepts/math_plan/ege-map.html`; другой файл можно передать аргументом: `python concepts/theory_page/build.py путь/к/ege-map.html`.

Порядок веток на уровне задаётся `BRANCH_ORDER` в `build.py` (сейчас на уровне 3 ветки идут 5 → 2 → 3 → 4 → 1).
