import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { curriculumRepository } from '../api/curriculumRepository.instance';
import { LearningProgress } from './LearningProgress';
import { LessonSummary } from './LessonSummary';
import type { Lesson } from './Lesson';

export const curriculumKeys = {
    all: ['curriculum'] as const,
    progress: ['curriculum', 'progress'] as const,
    summary: (lessonId: string) => ['curriculum', 'summary', lessonId] as const,
};

/** Программа курса вместе с прогрессом ученика */
export const useLearningProgress = () =>
    useQuery({
        queryKey: curriculumKeys.progress,
        queryFn: async () => {
            const [curriculum, completed] = await Promise.all([
                curriculumRepository.getCurriculum(),
                curriculumRepository.getCompletedLessonIds(),
            ]);
            return new LearningProgress(curriculum, completed);
        },
        staleTime: Infinity,
    });

export const useLessonSummary = (lesson: Lesson | null) =>
    useQuery({
        queryKey: curriculumKeys.summary(lesson?.id ?? ''),
        queryFn: async () => {
            const target = lesson!;
            return LessonSummary.resolve(target, await curriculumRepository.getSummary(target.id));
        },
        enabled: !!lesson,
        staleTime: Infinity,
    });

/** Засчитать урок пройденным — после этого маршрут теории пересчитывается */
export const useCompleteLesson = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (lessonId: string) => curriculumRepository.completeLesson(lessonId),
        onSuccess: (_, lessonId) => {
            queryClient.setQueryData<LearningProgress>(curriculumKeys.progress, (prev) => prev?.withCompleted(lessonId));
        },
    });
};
