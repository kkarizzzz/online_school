import type { PracticeRepository, PracticeTask, SubmitResult } from '../../../entities/practice-task';
import { Observable, parseApiError } from '../../../shared/lib';
import type { FeedMode } from './FeedMode';

/** Сколько последних заданий не повторять */
const SEEN_LIMIT = 30;

/** Попытка ответить на текущее задание */
export interface TaskAttempt {
    result: SubmitResult | null;
    /** Последний ответ был неверным — можно попробовать снова или открыть решение */
    wrong: boolean;
    revealed: boolean;
    submitting: boolean;
    error: string | null;
}

const freshAttempt = (): TaskAttempt => ({ result: null, wrong: false, revealed: false, submitting: false, error: null });

/**
 * Бесконечная лента «Нарешки»: задания по теме или «Торнадо», ответы, серия верных ответов.
 * Ответы проверяет сервер; лента лишь следит, чтобы задания не повторялись, пока есть новые.
 */
export class PracticeFeed extends Observable {
    mode: FeedMode | null = null;
    task: PracticeTask | null = null;
    attempt: TaskAttempt = freshAttempt();
    loading = false;
    error: string | null = null;
    /** Решено за сессию */
    solved = 0;
    /** Верных ответов подряд */
    streak = 0;

    private readonly repository: PracticeRepository;
    private seen: number[] = [];
    private request = 0;

    constructor(repository: PracticeRepository) {
        super();
        this.repository = repository;
    }

    /** Ответ принят (верно, на проверке у куратора) или решение открыто — можно идти дальше */
    get isFinished(): boolean {
        const { result, revealed } = this.attempt;
        return revealed || (!!result && result.isCorrect !== false);
    }

    async start(mode: FeedMode, taskId: number | null = null): Promise<void> {
        this.mode = mode;
        this.task = null;
        this.seen = [];
        await this.load(async () => {
            const restored = taskId ? await this.repository.getTask(taskId).catch(() => null) : null;
            return restored ?? this.fetchNext();
        });
    }

    exit(): void {
        this.request += 1;
        this.mode = null;
        this.task = null;
        this.loading = false;
        this.error = null;
        this.notify();
    }

    next(): Promise<void> {
        return this.load(() => this.fetchNext());
    }

    similar(): Promise<void> {
        const task = this.task;
        if (!task) return Promise.resolve();
        return this.load(() => this.repository.similarTask(task.id, this.recentSeen()));
    }

    async submit(answer: string): Promise<void> {
        const task = this.task;
        if (!task || this.attempt.submitting || this.isFinished) return;

        this.attempt = { ...this.attempt, submitting: true, error: null };
        this.notify();
        try {
            const result = await this.repository.submit(task.id, answer);
            if (this.task !== task) return;
            if (result.isCorrect) {
                this.solved += 1;
                this.streak += 1;
            } else if (result.isCorrect === false) {
                this.streak = 0;
            }
            this.attempt = { ...this.attempt, result, wrong: result.isCorrect === false, submitting: false };
        } catch (e) {
            if (this.task !== task) return;
            this.attempt = { ...this.attempt, submitting: false, error: parseApiError(e, 'Не удалось связаться с сервером') };
        }
        this.notify();
    }

    /** Показать ответ и решение после неверной попытки */
    reveal(): void {
        if (!this.attempt.result) return;
        this.attempt = { ...this.attempt, revealed: true };
        this.notify();
    }

    private fetchNext(): Promise<PracticeTask> {
        return this.repository.nextTask({
            topicId: this.mode?.topicId ?? null,
            currentId: this.task?.id ?? null,
            exclude: this.recentSeen(),
        });
    }

    private recentSeen(): number[] {
        return this.seen.slice(-SEEN_LIMIT);
    }

    /** Загружает задание; ответы на устаревшие запросы отбрасываются */
    private async load(fetch: () => Promise<PracticeTask>): Promise<void> {
        const request = ++this.request;
        this.loading = true;
        this.error = null;
        this.notify();
        try {
            const task = await fetch();
            if (request !== this.request) return;
            this.task = task;
            this.seen.push(task.id);
            this.attempt = freshAttempt();
        } catch (e) {
            if (request !== this.request) return;
            this.error = parseApiError(e, 'Не удалось связаться с сервером');
        }
        this.loading = false;
        this.notify();
    }
}
