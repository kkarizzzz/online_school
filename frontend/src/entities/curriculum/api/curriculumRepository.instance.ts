import type { CurriculumRepository } from './CurriculumRepository';
import { HttpCurriculumRepository } from './HttpCurriculumRepository';

export const curriculumRepository: CurriculumRepository = new HttpCurriculumRepository();
