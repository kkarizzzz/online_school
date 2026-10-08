import type { BankNumber, BankNumberTasks } from '../model/types';

export interface BankRepository {
    /** Номера 1–19 с темами и прогрессом ученика */
    getNumbers(): Promise<BankNumber[]>;
    /** Номер со всеми заданиями */
    getNumber(n: number): Promise<BankNumberTasks>;
    /** Поставить или снять свою отметку «решено» */
    setMarked(taskId: number, marked: boolean): Promise<void>;
}
