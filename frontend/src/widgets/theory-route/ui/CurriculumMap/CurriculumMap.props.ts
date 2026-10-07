import type { LearningProgress, Topic } from '../../../../entities/curriculum';

export interface CurriculumMapProps {
    progress: LearningProgress;
    onSelectTopic: (topic: Topic) => void;
}
