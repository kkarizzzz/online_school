import type { AxiosInstance } from 'axios';
import {
    PracticeMapper,
    type PracticeTaskDto,
    type PracticeTopicsDto,
    type SubmitResultDto,
} from '../model/dto';
import type { PracticeTask, PracticeTopics, SubmitResult } from '../model/types';
import type { NextTaskQuery, PracticeRepository } from './PracticeRepository';

/** exclude=1&exclude=2 — так списки принимает FastAPI */
const paramsSerializer = { indexes: null };

export class HttpPracticeRepository implements PracticeRepository {
    private readonly http: AxiosInstance;
    private readonly prefix: string;

    /** prefix — путь роутера нарешки относительно baseURL клиента */
    constructor(http: AxiosInstance, prefix = '') {
        this.http = http;
        this.prefix = prefix;
    }

    async getTopics(): Promise<PracticeTopics> {
        const { data } = await this.http.get<PracticeTopicsDto>(`${this.prefix}/topics`);
        return PracticeMapper.topics(data);
    }

    async getTask(taskId: number): Promise<PracticeTask> {
        const { data } = await this.http.get<PracticeTaskDto>(`${this.prefix}/tasks/${taskId}`);
        return PracticeMapper.task(data);
    }

    async nextTask({ topicId, currentId, exclude }: NextTaskQuery): Promise<PracticeTask> {
        const { data } = await this.http.get<PracticeTaskDto>(`${this.prefix}/tasks/random`, {
            params: { topic_id: topicId ?? undefined, current_id: currentId ?? undefined, exclude },
            paramsSerializer,
        });
        return PracticeMapper.task(data);
    }

    async similarTask(taskId: number, exclude: number[]): Promise<PracticeTask> {
        const { data } = await this.http.get<PracticeTaskDto>(`${this.prefix}/tasks/${taskId}/similar`, {
            params: { exclude },
            paramsSerializer,
        });
        return PracticeMapper.task(data);
    }

    async submit(taskId: number, answer: string): Promise<SubmitResult> {
        const { data } = await this.http.post<SubmitResultDto>(`${this.prefix}/tasks/${taskId}/submit`, { answer });
        return PracticeMapper.result(data);
    }
}
