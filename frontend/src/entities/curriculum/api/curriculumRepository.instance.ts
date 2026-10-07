import type { CurriculumRepository } from './CurriculumRepository';
import { MockCurriculumRepository } from './MockCurriculumRepository';

export const curriculumRepository: CurriculumRepository = new MockCurriculumRepository();
