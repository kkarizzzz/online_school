import { useQuery } from '@tanstack/react-query';
import { statsRepository } from '../api/statsRepository';

export const statsKeys = {
    all: ['stats'] as const,
    mine: ['stats', 'me'] as const,
};

/** Статистика ученика: серия, итоги, неделя, ДЗ, пробники, достижения */
export const useMyStats = () =>
    useQuery({
        queryKey: statsKeys.mine,
        queryFn: () => statsRepository.getMine(),
        staleTime: 60_000,
    });
