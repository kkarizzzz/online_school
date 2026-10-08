import { API, apiClient } from '../../../shared/api';
import { AttemptMapper, type AttemptData, type AttemptDto } from '../../attempt';
import type { HomeworkData, HomeworkDto, HomeworkList, HomeworkListDto } from '../model/types';
import type { HomeworkRepository } from './HomeworkRepository';

const toHomework = (h: HomeworkDto): HomeworkData => ({
    id: h.id,
    setId: h.set_id,
    title: h.title,
    topic: h.topic,
    note: h.note,
    numbers: h.numbers,
    taskCount: h.task_count,
    maxScore: h.max_score,
    deadlineAt: h.deadline_at,
    assignedAt: h.assigned_at,
    status: h.status,
    attempt: h.attempt && AttemptMapper.brief(h.attempt),
});

export class HttpHomeworkRepository implements HomeworkRepository {
    async getAll(): Promise<HomeworkList> {
        const { data } = await apiClient.get<HomeworkListDto>(API.homework.list);
        return { items: data.items.map(toHomework), counts: data.counts };
    }

    async start(homeworkId: number): Promise<AttemptData> {
        const { data } = await apiClient.post<AttemptDto>(API.homework.start(homeworkId));
        return AttemptMapper.attempt(data);
    }
}
