import type { BankTask } from '../../model/types';

export interface BankTaskCardProps {
    task: BankTask;
    /** Код задания: «6.3.04» — номер, тема, позиция */
    code: string;
    topicName: string;
    solved: boolean;
    onToggleSolved: () => void;
}
