import type { PracticeTask } from '../../../../entities/practice-task';
import type { PracticeFeed } from '../../model/PracticeFeed';

export interface PracticeTaskCardProps {
    feed: PracticeFeed;
    task: PracticeTask;
}
