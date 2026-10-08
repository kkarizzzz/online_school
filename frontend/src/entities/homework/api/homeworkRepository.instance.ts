import type { HomeworkRepository } from './HomeworkRepository';
import { HttpHomeworkRepository } from './HttpHomeworkRepository';

export const homeworkRepository: HomeworkRepository = new HttpHomeworkRepository();
