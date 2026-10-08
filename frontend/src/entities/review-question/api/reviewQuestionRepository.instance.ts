import { HttpReviewQuestionRepository } from './HttpReviewQuestionRepository';
import type { ReviewQuestionRepository } from './ReviewQuestionRepository';

export const reviewQuestionRepository: ReviewQuestionRepository = new HttpReviewQuestionRepository();
