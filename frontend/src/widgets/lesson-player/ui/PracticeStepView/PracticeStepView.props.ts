import type { LessonSession } from '../../model/LessonSession';
import type { PracticeStep } from '../../model/LessonStep';

export interface PracticeStepViewProps {
    session: LessonSession;
    step: PracticeStep;
    stepIndex: number;
    onSolved: (itemIndex: number) => void;
}
