import type { DetailedHTMLProps, HTMLAttributes } from 'react';
import type { LessonSession } from '../../model/LessonSession';

export interface LessonSidebarProps extends DetailedHTMLProps<HTMLAttributes<HTMLElement>, HTMLElement> {
    session: LessonSession;
    onGo: (stepIndex: number) => void;
}
