# Концепт: «Нарешка»

Бесконечная лента заданий по математике: по выбранной теме или «торнадо» по всем темам. Можно ответить, посмотреть решение, взять «Следующее» (из той же темы) или «Похожее» (из той же подтемы).

Отдельное приложение на FastAPI + SQLite, с основным бэкендом не связано — только переиспользует его виртуальное окружение, шрифты и логотип из `frontend/`.

## Файлы

- `app.py` — FastAPI: API `/api/...` и раздача статики.
- `models.py`, `db.py` — схема SQLAlchemy и подключение к `tasks.db`.
- `checker.py` — проверка ответов (число, дробь, варианты).
- `seed.py` — заполняет базу тестовыми заданиями и рисует картинки в `storage/`.
- `figures.py` — SVG-рисунки к заданиям.
- `static/` — страница (`index.html`, `app.js`, `styles.css`).
- `tasks.db`, `storage/` — генерируются `seed.py`, **в git не попадают**.

## Запуск

### 1. Окружение (один раз)

Используется venv бэкенда. Если его ещё нет — из корня репозитория:

```bash
python -m venv backend/.venv
```

```bash
backend/.venv/Scripts/python -m pip install -r backend/requirements.txt
```

(На macOS/Linux путь к интерпретатору — `backend/.venv/bin/python`.)

### 2. Поднять сервер

Из корня репозитория:

```bash
backend/.venv/Scripts/python -m uvicorn app:app --app-dir concepts/tasks_page --port 8100 --reload --reload-dir concepts/tasks_page
```

Открыть http://localhost:8100. Документация API — http://localhost:8100/docs.

При первом запуске, если `tasks.db` нет, база и рисунки создаются автоматически. Остановить — `Ctrl+C`. В Claude Code то же самое запускает конфиг `concept-tasks` из `.claude/launch.json`.

### Пересоздать базу

Удаляет все задания и попытки и заливает тестовые заново:

```bash
cd concepts/tasks_page
```

```bash
../../backend/.venv/Scripts/python seed.py
```
