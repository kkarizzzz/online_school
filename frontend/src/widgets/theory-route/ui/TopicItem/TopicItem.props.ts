import type { LearningProgress, Lesson, Topic } from '../../../../entities/curriculum';
import type { TheoryRouteState } from '../../model/TheoryRouteState';

export interface TopicItemProps {
    topic: Topic;
    progress: LearningProgress;
    state: TheoryRouteState;
    onOpenLesson: (lesson: Lesson) => void;
}
