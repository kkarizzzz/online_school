import { API, apiClient } from '../../../shared/api';
import type { ReviewQuestion } from '../model/types';
import type { ReviewQuestionRepository } from './ReviewQuestionRepository';

export class HttpReviewQuestionRepository implements ReviewQuestionRepository {
    async getQuestions(): Promise<ReviewQuestion[]> {
        const { data } = await apiClient.get<ReviewQuestion[]>(API.review.questions);
        return data;
    }
}
