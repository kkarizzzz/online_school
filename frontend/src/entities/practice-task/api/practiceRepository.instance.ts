import { API, apiClient } from '../../../shared/api';
import { HttpPracticeRepository } from './HttpPracticeRepository';
import type { PracticeRepository } from './PracticeRepository';

export const practiceRepository: PracticeRepository = new HttpPracticeRepository(apiClient, API.practice.root);
