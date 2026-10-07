import { randInt, shuffle } from '../../../shared/lib';

export interface QueueItem {
    id: number;
    /** Вопрос вернулся после ошибки */
    retry: boolean;
}

/**
 * Очередь вопросов: случайные круги по пулу режима,
 * вопрос с ошибкой возвращается через несколько карточек.
 * Позже порядок будет строить алгоритм интервального повторения на сервере.
 */
export class ReviewQueue {
    private readonly pool: number[];
    private readonly retryAfter: [min: number, max: number];
    private queue: QueueItem[] = [];
    private lastId: number | null = null;

    constructor(pool: number[], retryAfter: [number, number] = [3, 5]) {
        this.pool = pool;
        this.retryAfter = retryAfter;
    }

    next(): QueueItem {
        if (!this.queue.length) {
            // Новый круг; первым не ставим только что показанный вопрос
            const ids = shuffle(this.pool);
            if (ids[0] === this.lastId && ids.length > 1) ids.push(ids.shift() as number);
            this.queue = ids.map((id) => ({ id, retry: false }));
        }
        const item = this.queue.shift() as QueueItem;
        this.lastId = item.id;
        return item;
    }

    /** Убирает вопрос из текущего круга и ставит его поближе */
    scheduleRetry(id: number): void {
        this.queue = this.queue.filter((q) => q.id !== id);
        const position = Math.min(randInt(...this.retryAfter) - 1, this.queue.length);
        this.queue.splice(position, 0, { id, retry: true });
    }
}
