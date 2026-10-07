import type { LearningProgress, Lesson } from '../../../../entities/curriculum';
import type { TheoryRouteState } from '../../model/TheoryRouteState';

export interface RouteListProps {
    progress: LearningProgress;
    state: TheoryRouteState;
    onOpenLesson: (lesson: Lesson) => void;
}
