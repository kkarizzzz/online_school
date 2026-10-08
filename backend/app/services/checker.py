"""Проверка ответа ученика по answer_type задания (перенесено из concepts/tasks_page/checker.py)"""
import re

from app.db.enums import AnswerType
from app.db.models import TaskModel


def normalize(value: str) -> str:
    """«  0,6 » -> «0.6», «Неторопливой» -> «неторопливой», «ё» -> «е»"""
    value = value.strip().lower().replace('ё', 'е').replace(',', '.')
    return re.sub(r'\s+', '', value)


def _as_number(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def _same(given: str, expected: str) -> bool:
    given, expected = normalize(given), normalize(expected)
    if given == expected:
        return True
    # «0.60» и «0.6» — один и тот же ответ
    a, b = _as_number(given), _as_number(expected)
    return a is not None and b is not None and abs(a - b) < 1e-9


def check_answer(task: TaskModel, raw: str) -> bool | None:
    """True / False, либо None — если ответ проверяет человек"""
    if task.answer_type == AnswerType.detailed:
        return None
    if not raw.strip():
        return False

    accepted: list[str] = task.answer.get('accepted', [])
    match task.answer_type:
        case AnswerType.short:
            return any(_same(raw, a) for a in accepted)
        case AnswerType.digits_set:
            digits = sorted(re.sub(r'\D', '', raw))
            return any(digits == sorted(re.sub(r'\D', '', a)) for a in accepted)
        case AnswerType.sequence:
            parts = re.split(r'[\s;]+', raw.strip())
            for a in accepted:
                expected = a.split()
                if len(parts) == len(expected) and all(_same(p, e) for p, e in zip(parts, expected)):
                    return True
            return False
    return False
