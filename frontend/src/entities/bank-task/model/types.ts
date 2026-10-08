import type { ExamTaskNumber } from '../../exam-task';

/** Сложность: «гроб» — только во второй части */
export type BankLevel = 'base' | 'medium' | 'hard' | 'coffin';

/** Задание банка */
export interface BankTask {
    /** «6-log-3» */
    id: string;
    n: ExamTaskNumber;
    /** id темы */
    topic: string;
    /** Порядковый номер в теме, с 1 */
    index: number;
    /** Условие с формулами в $...$ */
    text: string;
    answer: number;
    /** Разбор решения, с формулами в $...$ */
    solution: string;
    level: BankLevel;
    /** Сколько учеников решило */
    solved: number;
    /** Дата добавления, YYYY-MM-DD */
    date: string;
}

/** Тема (прототип) внутри номера */
export interface BankTopic {
    id: string;
    name: string;
    tasks: BankTask[];
}

/** Номер ЕГЭ в банке */
export interface BankNumber {
    n: ExamTaskNumber;
    title: string;
    /** 1 — краткий ответ (1–12), 2 — развёрнутый (13–19) */
    part: 1 | 2;
    topics: BankTopic[];
}
