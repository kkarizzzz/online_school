import axios from 'axios';
import { API, apiClient } from '../../../shared/api';
import { HttpPracticeRepository } from './HttpPracticeRepository';
import type { PracticeRepository } from './PracticeRepository';

// VITE_PRACTICE_API_URL задан — работаем с отдельным сервером нарешки (концепт concepts/tasks_page,
// в dev проксируется Vite). Иначе — роутер нарешки основного бэкенда.
const standaloneUrl = import.meta.env.VITE_PRACTICE_API_URL;

export const practiceRepository: PracticeRepository = standaloneUrl
    ? new HttpPracticeRepository(axios.create({ baseURL: standaloneUrl }))
    : new HttpPracticeRepository(apiClient, API.practice.root);
