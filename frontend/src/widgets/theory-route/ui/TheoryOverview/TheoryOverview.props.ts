import type { LearningProgress } from '../../../../entities/curriculum';

export interface TheoryOverviewProps {
    progress: LearningProgress;
    onSelectLevel: (level: number) => void;
}
