import type { ExamTaskNumber } from '../../exam-task';

/** Вкладка списка. Назначенное ДЗ — current или overdue, сданное — всегда done */
export type HomeworkStatus = 'current' | 'done' | 'overdue';

/** Начатое ДЗ: ответы сохраняются сразу, к нему можно вернуться */
export interface HomeworkSession {
    /** Когда начато, мс */
    startedAt: number;
    /** Ответы по задачам, как их ввёл ученик */
    answers: string[];
    /** Открытая задача, с 0 */
    current: number;
}

/** Сданное ДЗ */
export interface HomeworkResult {
    /** По задачам: 1 — верно, 0 — неверно или без ответа */
    points: number[];
    /** Ответы ученика; у старых сдач их может не быть */
    answers?: string[];
    /** Сколько решал, с */
    seconds: number;
    /** Когда сдано, ISO */
    date: string;
    /** Сдано после срока */
    late?: boolean;
}

/** ДЗ, как его отдаёт репозиторий: задание преподавателя + прогресс ученика */
export interface HomeworkDto {
    id: string;
    title: string;
    /** Раздел программы — подпись под названием */
    topic: string;
    /** Номера ЕГЭ, из которых собрано ДЗ */
    numbers: ExamTaskNumber[];
    /** Число задач */
    tasks: number;
    /** Срок сдачи, YYYY-MM-DD (до 23:59) */
    deadline: string;
    /** Назначенный статус: current — срок не прошёл, overdue — прошёл */
    status: Exclude<HomeworkStatus, 'done'>;
    session: HomeworkSession | null;
    result: HomeworkResult | null;
}
