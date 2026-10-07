import type { ReviewQuestion } from '../model/types';
import type { ReviewQuestionRepository } from './ReviewQuestionRepository';
import { REVIEW_QUESTIONS_MOCK } from './mock/questions.data';

/** Банк вопросов из файла. Позже очередь будет строить алгоритм повторения на сервере */
export class MockReviewQuestionRepository implements ReviewQuestionRepository {
    async getQuestions(): Promise<ReviewQuestion[]> {
        return REVIEW_QUESTIONS_MOCK.map((q, id) => ({ ...q, id }));
    }
}
