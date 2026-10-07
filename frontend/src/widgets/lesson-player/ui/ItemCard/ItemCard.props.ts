import type { DetailedHTMLProps, HTMLAttributes } from 'react';
import type { LessonSession } from '../../model/LessonSession';

export interface ItemCardProps extends DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> {
    session: LessonSession;
    stepIndex: number;
    itemIndex: number;
    /** Верный ответ — можно перевести фокус на следующий вопрос */
    onSolved: (itemIndex: number) => void;
    /** Только для вопросов под роликом */
    onRewatch?: () => void;
}
