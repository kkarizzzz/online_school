import type { AttemptBrief, AttemptBriefDto } from '../../attempt';

/** Вкладка списка: срок не прошёл, прошёл или ДЗ уже сдано. Считает сервер */
export type HomeworkStatus = 'current' | 'done' | 'overdue';

/** ДЗ ученика, как его отдаёт сервер */
export interface HomeworkDto {
    /** id назначения ученику */
    id: number;
    set_id: number;
    title: string;
    /** Раздел программы — подпись под названием */
    topic: string | null;
    /** Комментарий преподавателя */
    note: string | null;
    subject: string;
    /** Номера ЕГЭ, из которых собрано ДЗ */
    numbers: number[];
    task_count: number;
    max_score: number;
    deadline_at: string | null;
    assigned_at: string;
    status: HomeworkStatus;
    attempt: AttemptBriefDto | null;
}

export interface HomeworkListDto {
    items: HomeworkDto[];
    counts: Record<HomeworkStatus, number>;
}

export interface HomeworkData {
    id: number;
    setId: number;
    title: string;
    topic: string | null;
    note: string | null;
    numbers: number[];
    taskCount: number;
    maxScore: number;
    deadlineAt: string | null;
    assignedAt: string;
    status: HomeworkStatus;
    attempt: AttemptBrief | null;
}

export interface HomeworkList {
    items: HomeworkData[];
    counts: Record<HomeworkStatus, number>;
}
