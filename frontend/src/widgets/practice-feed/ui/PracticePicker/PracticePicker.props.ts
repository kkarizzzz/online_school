import type { PracticeTopics } from '../../../../entities/practice-task';
import type { FeedMode } from '../../model/FeedMode';

export interface PracticePickerProps {
    data: PracticeTopics;
    onPick: (mode: FeedMode) => void;
}
