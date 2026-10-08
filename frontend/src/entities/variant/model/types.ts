import type { AttemptBrief, AttemptBriefDto, TaskSetKind } from '../../attempt';
import type { Difficulty } from '../../exam-task';

/** Вариант каталога, как его отдаёт сервер */
export interface VariantDto {
    id: number;
    kind: TaskSetKind;
    subject: string;
    title: string;
    description: string | null;
    publisher: string | null;
    difficulty: number | null;
    is_standard: boolean;
    numbers: number[];
    task_count: number;
    max_score: number;
    time_limit_sec: number | null;
    published_at: string;
    solved_students: number;
    avg_percent: number | null;
    last_attempt: AttemptBriefDto | null;
    best_attempt: AttemptBriefDto | null;
    in_progress_attempt_id: number | null;
}

export interface Variant {
    id: number;
    /** variant — полный, как на ЕГЭ; drill — отработка номеров */
    kind: TaskSetKind;
    title: string;
    description: string | null;
    publisher: string | null;
    difficulty: Difficulty | null;
    isStandard: boolean;
    numbers: number[];
    taskCount: number;
    maxScore: number;
    timeLimitSec: number | null;
    publishedAt: string;
    solvedStudents: number;
    /** Последняя сданная попытка ученика */
    lastAttempt: AttemptBrief | null;
    bestAttempt: AttemptBrief | null;
    inProgressAttemptId: number | null;
}

export type VariantKindFilter = 'all' | 'variant' | 'drill';
export type VariantStatusFilter = 'all' | 'todo' | 'done';
export type VariantSort = 'date' | 'difficulty' | 'popular';
