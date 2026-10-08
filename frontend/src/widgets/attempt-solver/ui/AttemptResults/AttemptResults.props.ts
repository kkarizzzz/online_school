import type { ReactNode } from 'react';
import type { AttemptData } from '../../../../entities/attempt';

export interface AttemptResultsProps {
    attempt: AttemptData;
    /** Только что сдано — иначе открыт разбор сданного раньше */
    justFinished?: boolean;
    /** Кнопки под итогом: «К домашним заданиям», «Попробовать снова» */
    actions?: ReactNode;
}
