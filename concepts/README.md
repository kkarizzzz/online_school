# Концепты

Макеты страниц личного кабинета, которые живут отдельно от основного проекта (`backend/`, `frontend/`). Каждый концепт — своя папка со своим README и инструкцией по запуску.

| Папка | Что это | Как открыть |
|---|---|---|
| [`math_plan/`](math_plan/README.md) | План подготовки к ЕГЭ по математике и карта тем `ege-map.html` — источник данных для теории | открыть `ege-map.html` в браузере |
| [`theory_page/`](theory_page/README.md) | Вкладка «Теория»: маршрут по темам и урокам | http://localhost:8200/concepts/theory_page/static/index.html |
| [`lesson_page/`](lesson_page/README.md) | Прохождение урока: ролики, вопросы, практика | http://localhost:8201/concepts/lesson_page/static/index.html?id=1.10.2 |
| [`tasks_page/`](tasks_page/README.md) | «Нарешка»: лента заданий (FastAPI + SQLite) | http://localhost:8100 |

Все команды в README запускаются **из корня репозитория** (`online_school/`), а не из папки концепта: страницы берут шрифты и логотип из `frontend/`.

Нужен Python 3.12+. Для `tasks_page` — зависимости бэкенда (`backend/.venv`, см. [tasks_page/README.md](tasks_page/README.md)).

## Как связаны данные

```
math_plan/plan.txt ──parse.py──▶ math_plan/ege-map.html ──theory_page/build.py──▶ theory_page/static/data.js
                                                                                         │
                                                         lesson_page берёт data.js ◀──────┘
```

Поменяли план → пересоберите карту и теорию:

```bash
python concepts/math_plan/parse.py
```

```bash
python concepts/theory_page/build.py
```

## Запуск через Claude Code

В `.claude/launch.json` есть конфиги `concept-theory`, `concept-lesson`, `concept-tasks` — их можно запускать во встроенном браузере приложения.
