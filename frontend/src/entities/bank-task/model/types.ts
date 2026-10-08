import type { ExamTask, ExamTaskNumber, TaskReveal } from '../../exam-task';

/** Сложность: «гроб» — только во второй части */
export type BankLevel = 'base' | 'medium' | 'hard' | 'coffin';

/** Задание банка: ответ и разбор в банке открыты сразу */
export interface BankTask {
    id: number;
    n: ExamTaskNumber;
    /** id темы (строкой — так он живёт в адресе страницы) */
    topic: string;
    /** Порядковый номер в теме, с 1 */
    index: number;
    task: ExamTask;
    reveal: TaskReveal;
    level: BankLevel;
    /** Решено засчитанным ответом — в нарешке, ДЗ или варианте. Такую отметку не снять */
    autoSolved: boolean;
    /** Ученик сам отметил «решено» */
    marked: boolean;
    /** Сколько учеников решило */
    solvedBy: number;
    /** Дата добавления, ISO */
    date: string;
}

/** Тема (прототип) в списке номеров — без заданий */
export interface BankTopicSummary {
    id: string;
    name: string;
    taskCount: number;
    solvedCount: number;
}

/** Номер ЕГЭ в банке */
export interface BankNumber {
    n: ExamTaskNumber;
    title: string;
    /** 1 — краткий ответ (1–12), 2 — развёрнутый (13–19) */
    part: 1 | 2;
    taskCount: number;
    solvedCount: number;
    topics: BankTopicSummary[];
}

export interface BankTopic {
    id: string;
    name: string;
    tasks: BankTask[];
}

/** Номер со всеми темами и заданиями — для страницы номера */
export interface BankNumberTasks {
    n: ExamTaskNumber;
    title: string;
    part: 1 | 2;
    topics: BankTopic[];
}
