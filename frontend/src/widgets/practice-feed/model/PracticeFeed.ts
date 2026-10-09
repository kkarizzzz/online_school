import type { PracticeRepository, PracticeTask, SubmitResult, TaskSolution } from '../../../entities/practice-task';
import { Observable, parseApiError } from '../../../shared/lib';
import { difficultyFilter, type PracticeScope } from './scope';

/** Сколько последних заданий не повторять */
const SEEN_LIMIT = 30;

/** Попытка ответить на текущее задание */
export interface TaskAttempt {
    result: SubmitResult | null;
    /** Последний ответ был неверным — можно попробовать снова или открыть решение */
    wrong: boolean;
    /** Ответ и решение — из проверки ответа или открытые без попытки */
    solution: TaskSolution | null;
    /** Решение раскрыто */
    revealed: boolean;
    submitting: boolean;
    /** Решение загружается */
    revealing: boolean;
    error: string | null;
}

/** Дольше этого время на задание не засчитываем — ученик, скорее всего, отошёл */
const MAX_TASK_SECONDS = 30 * 60;

const freshAttempt = (): TaskAttempt => ({
    result: null, wrong: false, solution: null, revealed: false, submitting: false, revealing: false, error: null,
});

/**
 * Бесконечная лента «Нарешки»: задания «Торнадо» или подборки, ответы, серия верных ответов.
 * Ответы проверяет сервер; лента лишь следит, чтобы задания не повторялись, пока есть новые.
 */
export class PracticeFeed extends Observable {
    scope: PracticeScope | null = null;
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
    /** С какого момента идёт время на текущий ответ, мс */
    private since = Date.now();

    constructor(repository: PracticeRepository) {
        super();
        this.repository = repository;
    }

    /** Ответ принят (верно или на проверке у преподавателя) — поле ответа больше не нужно */
    get isAccepted(): boolean {
        const { result } = this.attempt;
        return !!result && result.isCorrect !== false;
    }

    /** «Похожее» появляется после любого ответа или после просмотра решения */
    get canTakeSimilar(): boolean {
        return !!this.attempt.result || this.attempt.revealed;
    }

    async start(scope: PracticeScope, taskId: number | null = null): Promise<void> {
        this.scope = scope;
        this.task = null;
        this.seen = [];
        await this.load(async () => {
            const restored = taskId ? await this.repository.getTask(taskId).catch(() => null) : null;
            return restored ?? this.fetchNext();
        });
    }

    exit(): void {
        this.request += 1;
        this.scope = null;
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
        return this.load(() => this.repository.similarTask(task.id, this.recentSeen(), this.difficulties()));
    }

    async submit(answer: string): Promise<void> {
        const task = this.task;
        if (!task || this.attempt.submitting || this.isAccepted) return;

        this.attempt = { ...this.attempt, submitting: true, error: null };
        this.notify();
        const seconds = Math.min(Math.round((Date.now() - this.since) / 1000), MAX_TASK_SECONDS);
        this.since = Date.now();
        try {
            const result = await this.repository.submit(task.id, answer, seconds);
            if (this.task !== task) return;
            if (result.isCorrect) {
                this.solved += 1;
                this.streak += 1;
            } else if (result.isCorrect === false) {
                this.streak = 0;
            }
            this.attempt = {
                ...this.attempt,
                result,
                wrong: result.isCorrect === false,
                solution: { correctAnswer: result.correctAnswer, solution: result.solution },
                submitting: false,
            };
        } catch (e) {
            if (this.task !== task) return;
            this.attempt = { ...this.attempt, submitting: false, error: parseApiError(e, 'Не удалось связаться с сервером') };
        }
        this.notify();
    }

    /** Показать или скрыть решение; до ответа решение загружается отдельно */
    async toggleSolution(): Promise<void> {
        const task = this.task;
        if (!task || this.attempt.revealing) return;
        if (this.attempt.revealed || this.attempt.solution) {
            this.attempt = { ...this.attempt, revealed: !this.attempt.revealed };
            this.notify();
            return;
        }

        this.attempt = { ...this.attempt, revealing: true, error: null };
        this.notify();
        try {
            const solution = await this.repository.getSolution(task.id);
            if (this.task !== task) return;
            this.attempt = { ...this.attempt, solution, revealed: true, revealing: false };
        } catch (e) {
            if (this.task !== task) return;
            this.attempt = { ...this.attempt, revealing: false, error: parseApiError(e, 'Не удалось загрузить решение') };
        }
        this.notify();
    }

    private difficulties() {
        return difficultyFilter(this.scope?.difficulties ?? []);
    }

    private fetchNext(): Promise<PracticeTask> {
        const scope = this.scope;
        return this.repository.nextTask({
            topicIds: scope?.topicIds ?? [],
            part: scope?.kind === 'tornado' ? 1 : null,
            difficulties: this.difficulties(),
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
            this.since = Date.now();
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
