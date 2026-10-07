import { useQuery } from '@tanstack/react-query';
import { practiceRepository } from '../api/practiceRepository.instance';

export const practiceKeys = {
    topics: ['practice', 'topics'] as const,
};

export const usePracticeTopics = () =>
    useQuery({
        queryKey: practiceKeys.topics,
        queryFn: () => practiceRepository.getTopics(),
    });
