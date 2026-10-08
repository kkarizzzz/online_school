"""Общие колонки и типы моделей"""
import re
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, func
from sqlalchemy.orm import mapped_column


def str_enum(enum_cls: type[Enum]) -> SAEnum:
    """Перечисление как VARCHAR(32) + CHECK по значениям (см. app/db/enums.py)"""
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', enum_cls.__name__).lower()  # TaskSetKind -> task_set_kind
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=32,
        values_callable=lambda e: [m.value for m in e],
        validate_strings=True,
    )


def created_at_column():
    return mapped_column(DateTime(timezone=True), server_default=func.now(), init=False)


def updated_at_column():
    return mapped_column(DateTime(timezone=True), onupdate=func.now(), default=None, init=False)


def optional_datetime_column():
    return mapped_column(DateTime(timezone=True), default=None)
