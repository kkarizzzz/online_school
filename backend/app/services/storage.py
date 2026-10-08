"""
Файлы заданий и решений. Ключ файла (storage_key) — путь внутри хранилища: «figures/math-8-graph-a.svg».
В тексте заданий ссылки пишутся как storage://<ключ> и превращаются в URL при выдаче.

Сейчас хранилище — папка settings.STORAGE_DIR, которую раздаёт main.py.
При переезде на S3/MinIO меняются только эти функции.
"""
from pathlib import Path

from app.core.config import settings


def storage_dir() -> Path:
    path = Path(settings.STORAGE_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def public_url(key: str) -> str:
    return f'{settings.STORAGE_PUBLIC_URL.rstrip("/")}/{key}'


def resolve_links(markdown: str | None) -> str | None:
    """storage://figures/x.svg -> /storage/figures/x.svg"""
    return markdown.replace('storage://', settings.STORAGE_PUBLIC_URL.rstrip('/') + '/') if markdown else markdown


def save(key: str, content: bytes) -> None:
    path = storage_dir() / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
