import { useMutation, useQuery } from '@tanstack/react-query';
import { attemptRepository } from '../../attempt';
import { variantRepository } from '../api/variantRepository';

export const variantKeys = {
    list: ['variants', 'list'] as const,
    one: (variantId: number) => ['variants', 'one', variantId] as const,
    attempt: (attemptId: number) => ['variant-attempt', attemptId] as const,
};

export const useVariants = () =>
    useQuery({
        queryKey: variantKeys.list,
        queryFn: () => variantRepository.getAll(),
    });

/** Вариант для стартовой страницы */
export const useVariant = (variantId: number) =>
    useQuery({
        queryKey: variantKeys.one(variantId),
        queryFn: () => variantRepository.getOne(variantId),
        enabled: Number.isInteger(variantId) && variantId > 0,
        retry: false,
    });

/** «Приступить к варианту»: сервер создаёт новую попытку, начатую продолжить нельзя */
export const useStartVariant = () =>
    useMutation({
        mutationFn: (variantId: number) => variantRepository.start(variantId),
    });

/** Сданная попытка — для разбора */
export const useVariantAttempt = (attemptId: number) =>
    useQuery({
        queryKey: variantKeys.attempt(attemptId),
        queryFn: () => attemptRepository.get(attemptId),
        enabled: Number.isInteger(attemptId) && attemptId > 0,
        retry: false,
    });
