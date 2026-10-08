import type { BankNumber, BankNumberTasks } from '../../../../entities/bank-task';

export interface PrototypeTasksProps {
    number: BankNumberTasks;
    /** Все номера — для стрелок «предыдущий / следующий» */
    numbers: BankNumber[];
}
