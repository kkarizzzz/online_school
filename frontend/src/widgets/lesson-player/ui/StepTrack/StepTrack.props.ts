import type { DetailedHTMLProps, HTMLAttributes } from 'react';
import type { LessonSession } from '../../model/LessonSession';

export interface StepTrackProps extends DetailedHTMLProps<HTMLAttributes<HTMLOListElement>, HTMLOListElement> {
    session: LessonSession;
    onGo: (stepIndex: number) => void;
}
