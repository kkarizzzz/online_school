import type { BankNumber } from '../model/types';

export interface BankRepository {
    /** Номера 1–19 с темами и заданиями */
    getNumbers(): Promise<BankNumber[]>;
    /** id заданий, отмеченных учеником решёнными */
    getSolved(): Promise<string[]>;
    /** Поставить или снять отметку «решено» */
    setSolved(taskId: string, solved: boolean): Promise<void>;
}
