import type { DetailedHTMLProps, HTMLAttributes } from 'react';
import type { Lesson } from '../../../../entities/curriculum';
import type { LessonSession } from '../../model/LessonSession';

export interface LessonHeaderProps extends DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement> {
    lesson: Lesson;
    session: LessonSession;
    title: string;
    goal: string;
    isDemo: boolean;
}
