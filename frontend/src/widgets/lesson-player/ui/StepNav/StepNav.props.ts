import type { LessonSession } from '../../model/LessonSession';

export interface StepNavProps {
    session: LessonSession;
    onGo: (stepIndex: number) => void;
}
