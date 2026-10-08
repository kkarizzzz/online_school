export interface StatsTotals {
    answered: number;
    correct: number;
    /** Доля ответов на полный балл, 0–1 */
    accuracy: number | null;
    tasksSolved: number;
    seconds: number;
    lessonsDone: number;
}

export interface DayActivity {
    /** YYYY-MM-DD в поясе ученика */
    day: string;
    answered: number;
    correct: number;
    seconds: number;
    lessonsDone: number;
}

export interface HomeworkSummary {
    current: number;
    overdue: number;
    done: number;
    /** Сдано после срока */
    late: number;
    avgPercent: number | null;
}

/** Сданный полный вариант */
export interface MockExamResult {
    attemptId: number;
    title: string;
    subject: string;
    primaryScore: number | null;
    secondaryScore: number | null;
    maxScore: number | null;
    submittedAt: string;
}

export interface AchievementState {
    code: string;
    title: string;
    description: string;
    /** null — ещё не получено */
    unlockedAt: string | null;
}

export interface SubjectTasks {
    subject: string;
    tasksSolved: number;
    taskCount: number;
}

export interface StudentStats {
    streak: number;
    /** «Топ N%» по решённым заданиям; null — пока нечего сравнивать */
    rankPercent: number | null;
    subjects: SubjectTasks[];
    totals: StatsTotals;
    /** Последние 7 дней, сегодня — последний */
    week: DayActivity[];
    homework: HomeworkSummary;
    mockExams: MockExamResult[];
    achievements: AchievementState[];
}
