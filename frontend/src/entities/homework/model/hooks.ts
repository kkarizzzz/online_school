import { useQuery } from '@tanstack/react-query';
import { homeworkRepository } from '../api/homeworkRepository.instance';
import { Homework } from './Homework';

// Попытка — отдельный корень ключа: сброс списка ДЗ не перезапрашивает попытку
export const homeworkKeys = {
    all: ['homework'] as const,
    attempt: (homeworkId: number) => ['homework-attempt', homeworkId] as const,
};

/** Все ДЗ ученика и счётчики вкладок */
export const useHomeworkList = () =>
    useQuery({
        queryKey: homeworkKeys.all,
        queryFn: () => homeworkRepository.getAll(),
        select: ({ items, counts }) => ({ items: items.map((h) => new Homework(h)), counts }),
    });

/**
 * Попытка ДЗ: новая, начатая или сданная. Запрос идемпотентный — сервер возвращает
 * уже существующую попытку, поэтому его можно повторять при каждом открытии страницы
 */
export const useHomeworkAttempt = (homeworkId: number) =>
    useQuery({
        queryKey: homeworkKeys.attempt(homeworkId),
        queryFn: () => homeworkRepository.start(homeworkId),
        enabled: Number.isInteger(homeworkId) && homeworkId > 0,
        retry: false,
        staleTime: Infinity,
        gcTime: 0,
    });
