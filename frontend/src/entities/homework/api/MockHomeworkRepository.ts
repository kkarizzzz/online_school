import { formatAnswer } from '../../exam-task';
import { JsonStorage } from '../../../shared/lib';
import { Homework } from '../model/Homework';
import type { HomeworkDto, HomeworkResult, HomeworkSession } from '../model/types';
import type { HomeworkRepository } from './HomeworkRepository';
import { HOMEWORK_MOCK, type HomeworkMock } from './mock/homework.data';

/**
 * Список ДЗ из файла, прогресс ученика — в localStorage этого браузера.
 * Позже ДЗ будет выдавать преподаватель, а попытки храниться на сервере.
 */
export class MockHomeworkRepository implements HomeworkRepository {
    private readonly sessions = new JsonStorage<Record<string, HomeworkSession>>('homework:sessions');
    private readonly results = new JsonStorage<Record<string, HomeworkResult>>('homework:results');

    async getAll(): Promise<HomeworkDto[]> {
        const sessions = this.sessions.read() ?? {};
        const results = this.results.read() ?? {};
        return HOMEWORK_MOCK.map((mock) => {
            const result = results[mock.id] ?? MockHomeworkRepository.mockResult(mock);
            return {
                ...MockHomeworkRepository.assignment(mock),
                result,
                session: result ? null : sessions[mock.id] ?? MockHomeworkRepository.mockSession(mock),
            };
        });
    }

    async saveSession(id: string, session: HomeworkSession): Promise<void> {
        this.sessions.write({ ...this.sessions.read(), [id]: session });
    }

    async submit(id: string, result: HomeworkResult): Promise<void> {
        this.results.write({ ...this.results.read(), [id]: result });
        const sessions = this.sessions.read() ?? {};
        delete sessions[id];
        this.sessions.write(sessions);
    }

    /** Само задание, без прогресса */
    private static assignment(mock: HomeworkMock): Omit<HomeworkDto, 'session' | 'result'> {
        const { id, title, topic, numbers, tasks, deadline, status } = mock;
        return { id, title, topic, numbers, tasks, deadline, status };
    }

    private static mockResult(mock: HomeworkMock): HomeworkResult | null {
        if (!mock.result) return null;
        return { points: [...mock.result.points].map(Number), seconds: mock.result.minutes * 60, date: mock.result.date };
    }

    /** Начатое ДЗ из заглушки: первые `answered` задач с верными ответами */
    private static mockSession(mock: HomeworkMock): HomeworkSession | null {
        if (!mock.answered) return null;
        const tasks = new Homework({ ...MockHomeworkRepository.assignment(mock), session: null, result: null }).tasks;
        return {
            startedAt: Date.now(),
            answers: tasks.slice(0, mock.answered).map((t) => formatAnswer(t.answer)),
            current: Math.min(mock.answered, tasks.length - 1),
        };
    }
}
