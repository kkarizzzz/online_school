import { useQuery } from '@tanstack/react-query';
import { practiceRepository } from '../api/practiceRepository.instance';

export const practiceKeys = {
    numbers: ['practice', 'numbers'] as const,
};

/** Номера ЕГЭ с темами — для главной нарешки и настройки персонального режима */
export const usePracticeNumbers = () =>
    useQuery({
        queryKey: practiceKeys.numbers,
        queryFn: () => practiceRepository.getNumbers(),
    });
