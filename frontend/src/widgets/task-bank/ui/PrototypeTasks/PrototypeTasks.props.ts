import type { BankNumber } from '../../../../entities/bank-task';

export interface PrototypeTasksProps {
    number: BankNumber;
    /** Все номера — для стрелок «предыдущий / следующий» */
    numbers: BankNumber[];
}
