import { API, apiClient } from '../../../shared/api';
import type { LessonContentDto } from '../model/content.types';
import type { LessonContent, LessonContentRepository } from './LessonContentRepository';

interface LessonResponse {
    content: LessonContentDto | null;
    is_demo: boolean;
}

export class HttpLessonContentRepository implements LessonContentRepository {
    async getContent(lessonId: string): Promise<LessonContent> {
        const { data } = await apiClient.get<LessonResponse>(API.lessons.one(lessonId));
        if (!data.content) throw new Error('У урока пока нет содержимого');
        return { content: data.content, isDemo: data.is_demo };
    }
}
