import type { LessonSession } from '../../model/LessonSession';
import type { VideoStep } from '../../model/LessonStep';

export interface VideoStepViewProps {
    session: LessonSession;
    step: VideoStep;
    stepIndex: number;
    onSolved: (itemIndex: number) => void;
}
