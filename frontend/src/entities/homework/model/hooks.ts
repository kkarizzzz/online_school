import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { homeworkRepository } from '../api/homeworkRepository.instance';
import { Homework } from './Homework';
import type { HomeworkResult } from './types';

export const homeworkKeys = {
    all: ['homework'] as const,
};

/** Все ДЗ ученика */
export const useHomeworkList = () =>
    useQuery({
        queryKey: homeworkKeys.all,
        queryFn: () => homeworkRepository.getAll(),
        select: (list) => list.map((dto) => new Homework(dto)),
    });

/** Одно ДЗ; data === null — такого нет */
export const useHomework = (id: string) =>
    useQuery({
        queryKey: homeworkKeys.all,
        queryFn: () => homeworkRepository.getAll(),
        select: (list) => {
            const dto = list.find((hw) => hw.id === id);
            return dto ? new Homework(dto) : null;
        },
    });

export const useSubmitHomework = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, result }: { id: string; result: HomeworkResult }) => homeworkRepository.submit(id, result),
        onSuccess: () => queryClient.invalidateQueries({ queryKey: homeworkKeys.all }),
    });
};
