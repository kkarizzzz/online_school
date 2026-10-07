import type { LessonContent, LessonContentRepository } from './LessonContentRepository';
import { LESSON_CONTENT_MOCK } from './mock/lessonContent.data';

/** Урок с готовым содержимым — его показываем вместо уроков, которые ещё не наполнены */
const DEMO_LESSON_ID = '1.10.2';

export class MockLessonContentRepository implements LessonContentRepository {
    async getContent(lessonId: string): Promise<LessonContent> {
        const own = LESSON_CONTENT_MOCK[lessonId];
        return { content: own ?? LESSON_CONTENT_MOCK[DEMO_LESSON_ID], isDemo: !own };
    }
}
