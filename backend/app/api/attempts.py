"""Прохождение набора: общее для ДЗ, вариантов и отработок. Начинают попытку /homework и /variants"""
import uuid
from pathlib import PurePath

from fastapi import APIRouter, UploadFile, status
from sqlalchemy import func, select

from app.core.dependencies import StudentDep
from app.db.database import SessionDep
from app.db.models import AnswerFileModel, AnswerModel
from app.repositories.attempts import attempt_view, get_own_attempt
from app.schemas.attempt_schemas import AttemptOut, SaveAnswerRequest, SavePositionRequest
from app.schemas.task_schemas import FileOut
from app.services import attempts as attempts_service
from app.services import storage
from app.services.errors import ServiceError

router = APIRouter(prefix='/attempts', tags=['Попытки'])

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.pdf'}
MAX_FILES_PER_ANSWER = 5


@router.get('/{attempt_id}', response_model=AttemptOut, summary='Попытка: задания, ответы, после сдачи — разбор')
async def get_attempt(attempt_id: int, session: SessionDep, student: StudentDep):
    return await attempt_view(session, await get_own_attempt(session, attempt_id, student.id))


@router.put('/{attempt_id}/answers/{task_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Сохранить ответ')
async def save_answer(attempt_id: int, task_id: int, data: SaveAnswerRequest, session: SessionDep, student: StudentDep):
    """Вызывается при вводе: ответ — черновик, проверяется только при сдаче"""
    attempt = await get_own_attempt(session, attempt_id, student.id)
    await attempts_service.save_answer(session, attempt, task_id, data.answer, data.time_spent_sec)
    await session.commit()


@router.put('/{attempt_id}/position', status_code=status.HTTP_204_NO_CONTENT, summary='Открытое задание и время')
async def save_position(attempt_id: int, data: SavePositionRequest, session: SessionDep, student: StudentDep):
    attempt = await get_own_attempt(session, attempt_id, student.id)
    await attempts_service.save_position(session, attempt, data.position, data.time_spent_sec)
    await session.commit()


@router.post('/{attempt_id}/answers/{task_id}/files', response_model=FileOut, summary='Фото решения второй части')
async def upload_answer_file(attempt_id: int, task_id: int, file: UploadFile, session: SessionDep, student: StudentDep):
    attempt = await get_own_attempt(session, attempt_id, student.id)
    extension = PurePath(file.filename or '').suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ServiceError('Можно загрузить фото (jpg, png, webp, heic) или pdf')
    content = await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise ServiceError('Файл больше 10 МБ')

    answer = (await session.execute(
        select(AnswerModel).where(AnswerModel.attempt_id == attempt.id, AnswerModel.task_id == task_id)
    )).scalar_one_or_none()
    if answer is None:
        # Решение только фотографией — заводим пустой черновик ответа
        answer = await attempts_service.save_answer(session, attempt, task_id, '')
    else:
        attempts_service.ensure_open(attempt)
    count = (await session.execute(
        select(func.count()).select_from(AnswerFileModel).where(AnswerFileModel.answer_id == answer.id)
    )).scalar_one()
    if count >= MAX_FILES_PER_ANSWER:
        raise ServiceError(f'Не больше {MAX_FILES_PER_ANSWER} файлов к одному ответу')

    key = f'answers/{answer.id}/{uuid.uuid4().hex}{extension}'
    storage.save(key, content)
    filename = PurePath(file.filename).name[:255]
    session.add(AnswerFileModel(answer_id=answer.id, storage_key=key, filename=filename))
    await session.commit()
    return FileOut(filename=filename, url=storage.public_url(key))


@router.post('/{attempt_id}/submit', response_model=AttemptOut, summary='Сдать')
async def submit(attempt_id: int, session: SessionDep, student: StudentDep):
    attempt = await get_own_attempt(session, attempt_id, student.id)
    await attempts_service.submit_attempt(session, attempt)
    await session.commit()
    return await attempt_view(session, attempt)


@router.post('/{attempt_id}/abandon', status_code=status.HTTP_204_NO_CONTENT, summary='Бросить вариант')
async def abandon(attempt_id: int, session: SessionDep, student: StudentDep):
    """Незаконченная попытка не считается, вариант можно начать заново. ДЗ бросить нельзя"""
    attempt = await get_own_attempt(session, attempt_id, student.id)
    if attempt.student_assignment_id is not None:
        raise ServiceError('ДЗ нельзя бросить — его можно только сдать')
    await attempts_service.abandon_attempt(session, attempt)
    await session.commit()
