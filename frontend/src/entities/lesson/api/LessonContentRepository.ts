import type { LessonContentDto } from '../model/content.types';

export interface LessonContent {
    content: LessonContentDto;
    /** Своего содержимого у урока нет — показан демо-урок */
    isDemo: boolean;
}

export interface LessonContentRepository {
    getContent(lessonId: string): Promise<LessonContent>;
}
