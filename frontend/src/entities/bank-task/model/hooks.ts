import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { bankRepository } from '../api/bankRepository.instance';

export const bankKeys = {
    numbers: ['bank', 'numbers'] as const,
    solved: ['bank', 'solved'] as const,
};

export const useBankNumbers = () =>
    useQuery({
        queryKey: bankKeys.numbers,
        queryFn: () => bankRepository.getNumbers(),
        staleTime: Infinity,
    });

/** id решённых заданий */
export const useSolvedTasks = () =>
    useQuery({
        queryKey: bankKeys.solved,
        queryFn: () => bankRepository.getSolved(),
        select: (ids) => new Set(ids),
    });

/** Отметка «решено»: кэш меняется сразу, не дожидаясь ответа */
export const useToggleSolved = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ taskId, solved }: { taskId: string; solved: boolean }) => bankRepository.setSolved(taskId, solved),
        onMutate: ({ taskId, solved }) => {
            queryClient.setQueryData<string[]>(bankKeys.solved, (ids = []) =>
                solved ? [...new Set([...ids, taskId])] : ids.filter((id) => id !== taskId));
        },
        onSettled: () => queryClient.invalidateQueries({ queryKey: bankKeys.solved }),
    });
};
