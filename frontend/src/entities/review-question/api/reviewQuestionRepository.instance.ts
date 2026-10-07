import { MockReviewQuestionRepository } from './MockReviewQuestionRepository';
import type { ReviewQuestionRepository } from './ReviewQuestionRepository';

export const reviewQuestionRepository: ReviewQuestionRepository = new MockReviewQuestionRepository();
