# Концепты

Макеты страниц личного кабинета, которые живут отдельно от основного проекта (`backend/`, `frontend/`). Каждый концепт — своя папка со своим README и инструкцией по запуску.

| Папка | Что это | Как открыть |
|---|---|---|
| [`math_plan/`](math_plan/README.md) | План подготовки к ЕГЭ по математике и карта тем `ege-map.html` — источник данных для теории | открыть `ege-map.html` в браузере |
| [`theory_page/`](theory_page/README.md) | Вкладка «Теория»: маршрут по темам и урокам | http://localhost:8200/concepts/theory_page/static/index.html |
| [`lesson_page/`](lesson_page/README.md) | Прохождение урока: ролики, вопросы, практика | http://localhost:8201/concepts/lesson_page/static/index.html?id=1.10.2 |
| [`tasks_page/`](tasks_page/README.md) | «Нарешка»: лента заданий (FastAPI + SQLite) | http://localhost:8100 |
| [`practice_page/`](practice_page/README.md) | «Нарешка» по номерам: номера ЕГЭ и подтемы, «Торнадо» по первой части, персональный режим: номера ЕГЭ на отдельной странице, три последние подборки, лента заданий | http://localhost:8207/concepts/practice_page/static/index.html |
| [`review_page/`](review_page/README.md) | «Быстрое повторение»: микс вопросов по теории и вычислениям с вариантами ответа | http://localhost:8202/concepts/review_page/static/index.html |
| [`variants_page/`](variants_page/README.md) | «Каталог вариантов»: список с фильтрами, панель варианта, решение на время и результаты | http://localhost:8203/concepts/variants_page/static/index.html |
| [`variant_page2/`](variant_page2/README.md) | «Каталог вариантов», вторая версия: «Начать» ведёт на стартовую страницу с «Приступить к варианту», начатую попытку продолжить нельзя | http://localhost:8211/concepts/variant_page2/static/index.html |
| [`bank_page/`](bank_page/README.md) | «Банк заданий»: номера 1–19 → выбор тем → задания прототипа с отметками «решено» и сортировкой | http://localhost:8204/concepts/bank_page/static/index.html |
| [`homework_page/`](homework_page/README.md) | «Домашнее задание»: вкладки текущие / выполненные / просроченные, выполнение ДЗ и результаты | http://localhost:8205/concepts/homework_page/static/index.html |
| [`main_page/`](main_page/README.md) | Обновлённая главная: без преподавателей и психологов, вкладки обучения, страницы «Выпускникам» и «Родителям» | http://localhost:8206/concepts/main_page/static/index.html |
| [`admin_page/`](admin_page/README.md) | Кабинет преподавателя: банк заданий с редактором, конструктор и выдача ДЗ, проверка второй части, ученики и их карта номеров | http://localhost:8210/concepts/admin_page/static/index.html |
| [`parent_page/`](parent_page/README.md) | Кабинет родителя: три варианта главной — «Четыре ответа» (дашборд), «Отчёт недели», «Светофор» — и настройки отчётов и сигналов | http://localhost:8212/concepts/parent_page/static/index.html |
| [`league_page/`](league_page/README.md) | «Лига»: кланы, друзья и вызовы, недельные лиги, задания и валюта «сотки», магазин; схема БД и план реализации | http://localhost:8209/concepts/league_page/static/index.html |

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

В `.claude/launch.json` есть конфиги `concept-theory`, `concept-lesson`, `concept-tasks`, `concept-review`, `concept-variants`, `concept-bank`, `concept-homework`, `concept-main`, `concept-practice`, `concept-admin`, `concept-league`, `concept-parent` — их можно запускать во встроенном браузере приложения.
