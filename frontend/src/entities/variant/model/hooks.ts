import { useQuery } from '@tanstack/react-query';
import { attemptRepository } from '../../attempt';
import { variantRepository } from '../api/variantRepository';

// Попытки — отдельные корни ключей: сброс каталога не должен перезапрашивать «начать вариант»,
// иначе сервер создаст следующую попытку
export const variantKeys = {
    list: ['variants', 'list'] as const,
    start: (variantId: number) => ['variant-start', variantId] as const,
    attempt: (attemptId: number) => ['variant-attempt', attemptId] as const,
};

export const useVariants = () =>
    useQuery({
        queryKey: variantKeys.list,
        queryFn: () => variantRepository.getAll(),
    });

/** Начатая или новая попытка варианта. Повторный запрос продолжает ту же незаконченную попытку */
export const useVariantStart = (variantId: number) =>
    useQuery({
        queryKey: variantKeys.start(variantId),
        queryFn: () => variantRepository.start(variantId),
        enabled: Number.isInteger(variantId) && variantId > 0,
        retry: false,
        staleTime: Infinity,
        gcTime: 0,
    });

/** Сданная попытка — для разбора */
export const useVariantAttempt = (attemptId: number) =>
    useQuery({
        queryKey: variantKeys.attempt(attemptId),
        queryFn: () => attemptRepository.get(attemptId),
        enabled: Number.isInteger(attemptId) && attemptId > 0,
        retry: false,
    });
