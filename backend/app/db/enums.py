"""
Перечисления для моделей.

В базе они хранятся строкой с CHECK-ограничением, а не нативным ENUM PostgreSQL:
новое значение добавляется миграцией, которая пересоздаёт CHECK, без ALTER TYPE.
"""
from enum import Enum


class UserRole(str, Enum):
    student = 'student'
    parent = 'parent'
    teacher = 'teacher'   # создаёт ДЗ и варианты, проверяет вторую часть
    admin = 'admin'


class Subject(str, Enum):
    math = 'math'
    physics = 'physics'
    russian = 'russian'
    informatics = 'informatics'


class AnswerType(str, Enum):
    short = 'short'            # одно число или слово: «5», «-14», «0,6», «неторопливой»
    digits_set = 'digits_set'  # номера вариантов, порядок не важен: «135» == «531»
    sequence = 'sequence'      # несколько значений по порядку: «412 1867»
    detailed = 'detailed'      # развёрнутый ответ, проверяет преподаватель по критериям


class FileKind(str, Enum):
    image = 'image'            # картинка внутри условия или решения
    attachment = 'attachment'  # файл к заданию (информатика: 17.txt, 9.xlsx)


class TaskSetKind(str, Enum):
    homework = 'homework'                # ДЗ
    variant = 'variant'                  # полный вариант или пробник
    drill = 'drill'                      # отработка одного или нескольких номеров
    lesson_practice = 'lesson_practice'  # практика внутри урока


class AttemptStatus(str, Enum):
    in_progress = 'in_progress'  # ученик решает, ответы сохраняются черновиком
    checking = 'checking'        # сдано, вторая часть ждёт преподавателя
    graded = 'graded'            # всё проверено
    abandoned = 'abandoned'      # брошено, не считается


class LessonStatus(str, Enum):
    in_progress = 'in_progress'
    done = 'done'


class ReviewQuestionKind(str, Enum):
    theory = 'theory'
    calc = 'calc'


class NotificationType(str, Enum):
    homework_assigned = 'homework_assigned'
    homework_due_soon = 'homework_due_soon'
    homework_overdue = 'homework_overdue'
    homework_submitted = 'homework_submitted'  # родителю: ребёнок сдал ДЗ
    attempt_graded = 'attempt_graded'          # вторую часть проверили
    achievement_unlocked = 'achievement_unlocked'
    system = 'system'


class NotificationChannel(str, Enum):
    telegram = 'telegram'
    sms = 'sms'
    email = 'email'


class DeliveryStatus(str, Enum):
    pending = 'pending'
    sent = 'sent'
    failed = 'failed'
