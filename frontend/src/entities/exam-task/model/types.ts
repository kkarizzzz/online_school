/** Номер задания ЕГЭ (профиль): 1–12 — краткий ответ, 13–19 — развёрнутый */
export type ExamTaskNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19;

/** Задание с числовым ответом. text и solution — с формулами в $...$ (см. MathText) */
export interface ExamTask {
    number: ExamTaskNumber;
    text: string;
    answer: number;
    /** Разбор решения */
    solution: string;
}
