import type { ReviewCard, ReviewFeed } from '../../model/ReviewFeed';

export interface ReviewCardViewProps {
    feed: ReviewFeed;
    card: ReviewCard;
}
