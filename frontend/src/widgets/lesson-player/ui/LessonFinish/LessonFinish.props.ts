import type { Lesson } from '../../../../entities/curriculum';
import type { LessonSession } from '../../model/LessonSession';

export interface LessonFinishProps {
    session: LessonSession;
    nextLesson: Lesson | null;
    onGo: (stepIndex: number) => void;
}
