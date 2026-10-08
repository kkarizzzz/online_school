import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { bankRepository } from '../api/bankRepository.instance';
import type { BankNumberTasks } from './types';

export const bankKeys = {
    all: ['bank'] as const,
    numbers: ['bank', 'numbers'] as const,
    number: (n: number) => ['bank', 'number', n] as const,
};

/** Номера 1–19 с темами и прогрессом */
export const useBankNumbers = () =>
    useQuery({
        queryKey: bankKeys.numbers,
        queryFn: () => bankRepository.getNumbers(),
    });

/** Номер со всеми заданиями */
export const useBankNumber = (n: number) =>
    useQuery({
        queryKey: bankKeys.number(n),
        queryFn: () => bankRepository.getNumber(n),
        enabled: Number.isInteger(n) && n > 0,
        retry: false,
    });

/** Своя отметка «решено»: кэш номера меняется сразу, не дожидаясь ответа */
export const useToggleMarked = (n: number) => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ taskId, marked }: { taskId: number; marked: boolean }) => bankRepository.setMarked(taskId, marked),
        onMutate: ({ taskId, marked }) => {
            queryClient.setQueryData<BankNumberTasks>(bankKeys.number(n), (prev) => prev && {
                ...prev,
                topics: prev.topics.map((topic) => ({
                    ...topic,
                    tasks: topic.tasks.map((t) => (t.id === taskId ? { ...t, marked } : t)),
                })),
            });
        },
        onSettled: () => {
            void queryClient.invalidateQueries({ queryKey: bankKeys.number(n) });
            void queryClient.invalidateQueries({ queryKey: bankKeys.numbers });
        },
    });
};
