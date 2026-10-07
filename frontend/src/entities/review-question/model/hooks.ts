import { useQuery } from '@tanstack/react-query';
import { reviewQuestionRepository } from '../api/reviewQuestionRepository.instance';

export const useReviewQuestions = () =>
    useQuery({
        queryKey: ['review', 'questions'],
        queryFn: () => reviewQuestionRepository.getQuestions(),
        staleTime: Infinity,
    });
