import type { LessonContentRepository } from './LessonContentRepository';
import { HttpLessonContentRepository } from './HttpLessonContentRepository';

export const lessonContentRepository: LessonContentRepository = new HttpLessonContentRepository();
