import type { ReactNode } from 'react';
import type { AttemptData } from '../../../../entities/attempt';

export interface AttemptSolverProps {
    attempt: AttemptData;
    /** Ссылка «назад» в шапке */
    back: { to: string; label: string };
    /** Подпись над названием: «Домашнее задание · Алгебра · 8 задач» */
    kicker: string;
    /** Кнопки под результатами */
    resultActions?: ReactNode;
    /** Попытка сдана — обновить списки, счётчики и т.п. */
    onSubmitted?: (attempt: AttemptData) => void;
}
