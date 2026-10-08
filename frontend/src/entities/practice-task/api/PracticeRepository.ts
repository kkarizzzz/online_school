import type { PracticeTask, PracticeTopics, SubmitResult } from '../model/types';

export interface NextTaskQuery {
    /** Тема ленты; null — «Торнадо» по всем темам */
    topicId: number | null;
    /** Текущее задание — его не повторяем */
    currentId: number | null;
    /** Уже показанные в ленте задания */
    exclude: number[];
}

export interface PracticeRepository {
    getTopics(): Promise<PracticeTopics>;
    getTask(taskId: number): Promise<PracticeTask>;
    nextTask(query: NextTaskQuery): Promise<PracticeTask>;
    /** Случайное задание из той же подтемы */
    similarTask(taskId: number, exclude: number[]): Promise<PracticeTask>;
    /** timeSpentSec — сколько думал над ответом: идёт в статистику времени */
    submit(taskId: number, answer: string, timeSpentSec?: number): Promise<SubmitResult>;
}
