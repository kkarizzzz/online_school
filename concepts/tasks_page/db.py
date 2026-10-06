from pathlib import Path

from sqlalchemy import create_engine


BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / 'tasks.db'
STORAGE_DIR = BASE_DIR / 'storage'  # имитация S3/MinIO: ключ файла = путь внутри папки

engine = create_engine(f'sqlite:///{DB_PATH}')
