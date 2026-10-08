import { API, apiClient } from '../../../shared/api';
import { ExamTaskMapper, type ExamTaskDto, type ExamTaskNumber, type TaskRevealDto } from '../../exam-task';
import { levelOf } from '../model/levels';
import type { BankNumber, BankNumberTasks, BankTask } from '../model/types';
import type { BankRepository } from './BankRepository';

interface BankNumberDto {
    number: number;
    title: string | null;
    part: number;
    task_count: number;
    solved_count: number;
    topics: { id: number; name: string; task_count: number; solved_count: number }[];
}

interface BankTaskDto {
    index: number;
    task: ExamTaskDto;
    reveal: TaskRevealDto;
    is_solved: boolean;
    is_marked: boolean;
    solved_students: number;
    created_at: string;
}

interface BankNumberDetailDto {
    number: number;
    title: string | null;
    part: number;
    topics: { id: number; name: string; tasks: BankTaskDto[] }[];
}

const part = (p: number): 1 | 2 => (p === 2 ? 2 : 1);

const toTask = (n: number, topicId: number, t: BankTaskDto): BankTask => {
    const task = ExamTaskMapper.task(t.task);
    return {
        id: task.id,
        n: n as ExamTaskNumber,
        topic: String(topicId),
        index: t.index,
        task,
        reveal: ExamTaskMapper.reveal(t.reveal),
        level: levelOf(task.difficulty),
        autoSolved: t.is_solved,
        marked: t.is_marked,
        solvedBy: t.solved_students,
        date: t.created_at,
    };
};

export class HttpBankRepository implements BankRepository {
    async getNumbers(): Promise<BankNumber[]> {
        const { data } = await apiClient.get<BankNumberDto[]>(API.bank.numbers);
        return data.map((b) => ({
            n: b.number as ExamTaskNumber,
            title: b.title ?? `Задание ${b.number}`,
            part: part(b.part),
            taskCount: b.task_count,
            solvedCount: b.solved_count,
            topics: b.topics.map((t) => ({
                id: String(t.id), name: t.name, taskCount: t.task_count, solvedCount: t.solved_count,
            })),
        }));
    }

    async getNumber(n: number): Promise<BankNumberTasks> {
        const { data } = await apiClient.get<BankNumberDetailDto>(API.bank.number(n));
        return {
            n: data.number as ExamTaskNumber,
            title: data.title ?? `Задание ${data.number}`,
            part: part(data.part),
            topics: data.topics.map((t) => ({
                id: String(t.id),
                name: t.name,
                tasks: t.tasks.map((task) => toTask(data.number, t.id, task)),
            })),
        };
    }

    async setMarked(taskId: number, marked: boolean): Promise<void> {
        if (marked) await apiClient.put(API.bank.mark(taskId));
        else await apiClient.delete(API.bank.mark(taskId));
    }
}
