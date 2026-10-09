import type { Difficulty, PracticeNumber, PracticeTask, SubmitResult, TaskSolution } from '../model/types';

export interface NextTaskQuery {
    /** Темы подборки; пусто — все темы */
    topicIds: number[];
    /** Только эта часть экзамена: «Торнадо» — 1 */
    part: number | null;
    /** Сложности; пусто — все */
    difficulties: Difficulty[];
    /** Текущее задание — его не повторяем */
    currentId: number | null;
    /** Уже показанные в ленте задания */
    exclude: number[];
}

export interface PracticeRepository {
    /** Номера ЕГЭ с темами и числом заданий по сложности */
    getNumbers(): Promise<PracticeNumber[]>;
    getTask(taskId: number): Promise<PracticeTask>;
    nextTask(query: NextTaskQuery): Promise<PracticeTask>;
    /** Случайное задание из той же подтемы с учётом выбранных сложностей */
    similarTask(taskId: number, exclude: number[], difficulties: Difficulty[]): Promise<PracticeTask>;
    /** Ответ и решение без попытки — ученик решил посмотреть разбор */
    getSolution(taskId: number): Promise<TaskSolution>;
    /** timeSpentSec — сколько думал над ответом: идёт в статистику времени */
    submit(taskId: number, answer: string, timeSpentSec?: number): Promise<SubmitResult>;
}
