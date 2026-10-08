import { API, apiClient } from '../../../shared/api';
import type { TaskAttachment } from '../../exam-task';
import { AttemptMapper, type AttemptDto } from '../model/dto';
import type { AttemptData } from '../model/types';
import type { AttemptRepository } from './AttemptRepository';

export class HttpAttemptRepository implements AttemptRepository {
    async get(attemptId: number): Promise<AttemptData> {
        const { data } = await apiClient.get<AttemptDto>(API.attempts.one(attemptId));
        return AttemptMapper.attempt(data);
    }

    async saveAnswer(attemptId: number, taskId: number, answer: string): Promise<void> {
        await apiClient.put(API.attempts.answer(attemptId, taskId), { answer });
    }

    async savePosition(attemptId: number, position: number, timeSpentSec: number): Promise<void> {
        await apiClient.put(API.attempts.position(attemptId), { position, time_spent_sec: Math.floor(timeSpentSec) });
    }

    async uploadFile(attemptId: number, taskId: number, file: File): Promise<TaskAttachment> {
        const form = new FormData();
        form.append('file', file);
        // Заголовок multipart с границей выставит сам браузер
        const { data } = await apiClient.post<TaskAttachment>(API.attempts.files(attemptId, taskId), form, {
            headers: { 'Content-Type': undefined },
        });
        return data;
    }

    async submit(attemptId: number): Promise<AttemptData> {
        const { data } = await apiClient.post<AttemptDto>(API.attempts.submit(attemptId));
        return AttemptMapper.attempt(data);
    }

    async abandon(attemptId: number): Promise<void> {
        await apiClient.post(API.attempts.abandon(attemptId));
    }
}
