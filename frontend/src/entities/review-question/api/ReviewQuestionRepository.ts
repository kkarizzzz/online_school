import type { ReviewQuestion } from '../model/types';

export interface ReviewQuestionRepository {
    getQuestions(): Promise<ReviewQuestion[]>;
}
