import type { AxiosInstance } from 'axios';
import {
    PracticeMapper,
    type PracticeNumberDto,
    type PracticeTaskDto,
    type SubmitResultDto,
    type TaskSolutionDto,
} from '../model/dto';
import type { Difficulty, PracticeNumber, PracticeTask, SubmitResult, TaskSolution } from '../model/types';
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

    async getNumbers(): Promise<PracticeNumber[]> {
        const { data } = await this.http.get<PracticeNumberDto[]>(`${this.prefix}/numbers`);
        return PracticeMapper.numbers(data);
    }

    async getTask(taskId: number): Promise<PracticeTask> {
        const { data } = await this.http.get<PracticeTaskDto>(`${this.prefix}/tasks/${taskId}`);
        return PracticeMapper.task(data);
    }

    async nextTask({ topicIds, part, difficulties, currentId, exclude }: NextTaskQuery): Promise<PracticeTask> {
        const { data } = await this.http.get<PracticeTaskDto>(`${this.prefix}/tasks/random`, {
            params: {
                topic_id: topicIds,
                part: part ?? undefined,
                difficulty: difficulties,
                current_id: currentId ?? undefined,
                exclude,
            },
            paramsSerializer,
        });
        return PracticeMapper.task(data);
    }

    async similarTask(taskId: number, exclude: number[], difficulties: Difficulty[]): Promise<PracticeTask> {
        const { data } = await this.http.get<PracticeTaskDto>(`${this.prefix}/tasks/${taskId}/similar`, {
            params: { exclude, difficulty: difficulties },
            paramsSerializer,
        });
        return PracticeMapper.task(data);
    }

    async getSolution(taskId: number): Promise<TaskSolution> {
        const { data } = await this.http.get<TaskSolutionDto>(`${this.prefix}/tasks/${taskId}/solution`);
        return PracticeMapper.solution(data);
    }

    async submit(taskId: number, answer: string, timeSpentSec?: number): Promise<SubmitResult> {
        const { data } = await this.http.post<SubmitResultDto>(`${this.prefix}/tasks/${taskId}/submit`, {
            answer,
            time_spent_sec: timeSpentSec,
        });
        return PracticeMapper.result(data);
    }
}
