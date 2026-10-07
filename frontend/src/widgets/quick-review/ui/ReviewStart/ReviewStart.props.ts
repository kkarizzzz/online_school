import type { ReviewQuestion } from '../../../../entities/review-question';
import type { ReviewHistory } from '../../model/ReviewHistory';
import type { ReviewMode } from '../../model/ReviewMode';

export interface ReviewStartProps {
    questions: ReviewQuestion[];
    history: ReviewHistory;
    onStart: (mode: ReviewMode) => void;
}
