import type { BankNumber } from '../../../../entities/bank-task';

export interface TopicsDrawerProps {
    /** Открытый номер; null — панель закрыта */
    number: BankNumber | null;
    onClose: () => void;
}
