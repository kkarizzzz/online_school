from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.db.database import engine
from fastapi.middleware.cors import CORSMiddleware
from app.api.admin import router as admin_router
from app.api.attempts import router as attempts_router
from app.api.auth import router as auth_router
from app.api.bank import router as bank_router
from app.api.homework import router as homework_router
from app.api.notifications import router as notifications_router
from app.api.practice import router as practice_router
from app.api.stats import router as stats_router
from app.api.users import router as users_router
from app.api.variants import router as variants_router
from app.core.config import settings
from app.services.errors import ServiceError
from app.services.storage import storage_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Сервер запущен')
    yield
    print('Сервер остановлен')
    await engine.dispose()






app = FastAPI(
    title='Онлайн школа',
    version='1.0',
    lifespan=lifespan
    )

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(practice_router)
app.include_router(bank_router)
app.include_router(homework_router)
app.include_router(variants_router)
app.include_router(attempts_router)
app.include_router(stats_router)
app.include_router(notifications_router)
app.include_router(admin_router)


@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError):
    """Ошибки сервисного слоя → {"detail": "..."} с кодом ошибки, как у HTTPException"""
    return JSONResponse(status_code=exc.status_code, content={'detail': exc.detail})


# Файлы заданий и решений. Временно, до S3/MinIO: в проде их раздаст хранилище или nginx
app.mount(settings.STORAGE_PUBLIC_URL, StaticFiles(directory=storage_dir()), name='storage')

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://localhost:80",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/', tags=['Система'])
async def check() -> str:
    return 'Сервер запущен'