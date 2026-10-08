import type { ExamTask, TaskAttachment, TaskReveal } from '../../exam-task';

/** in_progress — решается; checking — сдано, вторую часть проверяет преподаватель; graded — проверено */
export type AttemptStatus = 'in_progress' | 'checking' | 'graded' | 'abandoned';

export type TaskSetKind = 'homework' | 'variant' | 'drill' | 'lesson_practice';

/** Набор, по которому идёт попытка */
export interface AttemptSet {
    id: number;
    kind: TaskSetKind;
    title: string;
    subject: string;
    /** Полный вариант как на ЕГЭ — результат во вторичных баллах */
    isStandard: boolean;
    /** Лимит времени, с; null — без ограничения */
    timeLimitSec: number | null;
}

/** Проверка ответа — есть только после сдачи */
export interface AttemptItemResult extends TaskReveal {
    isCorrect: boolean | null;
    score: number | null;
    /** Ждёт проверки преподавателем */
    needsReview: boolean;
    reviewerComment: string | null;
}

export interface AttemptItem {
    position: number;
    maxScore: number;
    task: ExamTask;
    answer: string | null;
    files: TaskAttachment[];
    result: AttemptItemResult | null;
}

/** Попытка целиком: задания по порядку, ответы, после сдачи — разбор */
export interface AttemptData {
    id: number;
    status: AttemptStatus;
    set: AttemptSet;
    studentAssignmentId: number | null;
    deadlineAt: string | null;
    startedAt: string;
    /** Когда закончится время, ISO; null — без ограничения */
    expiresAt: string | null;
    submittedAt: string | null;
    /** Насколько часы сервера впереди часов браузера, мс — для таймера */
    clockOffset: number;
    timeSpentSec: number;
    currentPosition: number;
    isLate: boolean;
    isRated: boolean;
    maxScore: number | null;
    /** После сдачи; пока идёт проверка — предварительный */
    primaryScore: number | null;
    secondaryScore: number | null;
    answered: number;
    items: AttemptItem[];
}

/** Попытка в списках ДЗ и вариантов */
export interface AttemptBrief {
    id: number;
    status: AttemptStatus;
    answered: number;
    primaryScore: number | null;
    secondaryScore: number | null;
    maxScore: number | null;
    startedAt: string;
    submittedAt: string | null;
    timeSpentSec: number;
    isLate: boolean;
}
