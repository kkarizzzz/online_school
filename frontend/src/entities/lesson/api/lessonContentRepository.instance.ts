import type { LessonContentRepository } from './LessonContentRepository';
import { MockLessonContentRepository } from './MockLessonContentRepository';

export const lessonContentRepository: LessonContentRepository = new MockLessonContentRepository();
