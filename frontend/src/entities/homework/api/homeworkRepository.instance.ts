import type { HomeworkRepository } from './HomeworkRepository';
import { MockHomeworkRepository } from './MockHomeworkRepository';

export const homeworkRepository: HomeworkRepository = new MockHomeworkRepository();
