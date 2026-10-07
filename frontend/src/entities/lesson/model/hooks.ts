import { useQuery } from '@tanstack/react-query';
import { lessonContentRepository } from '../api/lessonContentRepository.instance';

export const useLessonContent = (lessonId: string) =>
    useQuery({
        queryKey: ['lesson', 'content', lessonId],
        queryFn: () => lessonContentRepository.getContent(lessonId),
        staleTime: Infinity,
    });
