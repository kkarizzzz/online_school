import type { ReviewQuestion } from '../../../entities/review-question';
import { Observable, shuffle } from '../../../shared/lib';
import type { ReviewHistory } from './ReviewHistory';
import type { ReviewMode } from './ReviewMode';
import { ReviewQueue } from './ReviewQueue';
import { ReviewSession } from './ReviewSession';

/** «Не знаю» — засчитывается как ошибка и показывает правильный ответ */
export const DONT_KNOW = -1;

/** Карточка ленты. options вопроса перемешаны: order — индексы в банке, 0 — правильный */
export class ReviewCard {
    readonly number: number;
    readonly question: ReviewQuestion;
    readonly retry: boolean;
    readonly order: number[];
    picked: number | null = null;

    constructor(number: number, question: ReviewQuestion, retry: boolean) {
        this.number = number;
        this.question = question;
        this.retry = retry;
        this.order = shuffle(question.options.map((_, i) => i));
    }

    get isAnswered(): boolean {
        return this.picked !== null;
    }

    get isCorrect(): boolean {
        return this.picked === 0;
    }

    get isDontKnow(): boolean {
        return this.picked === DONT_KNOW;
    }
}

/** Лента быстрого повторения в выбранном режиме */
export class ReviewFeed extends Observable {
    mode: ReviewMode | null = null;
    session: ReviewSession | null = null;
    card: ReviewCard | null = null;

    private readonly questions: ReviewQuestion[];
    private readonly byId: Map<number, ReviewQuestion>;
    private readonly history: ReviewHistory;
    private queue: ReviewQueue | null = null;
    private count = 0;

    constructor(questions: ReviewQuestion[], history: ReviewHistory) {
        super();
        this.questions = questions;
        this.byId = new Map(questions.map((q) => [q.id, q]));
        this.history = history;
    }

    start(mode: ReviewMode): void {
        this.mode = mode;
        this.session = new ReviewSession(mode.id);
        this.queue = new ReviewQueue(mode.poolOf(this.questions).map((q) => q.id));
        this.count = 0;
        this.showNext();
    }

    exit(): void {
        this.mode = null;
        this.session = null;
        this.card = null;
        this.queue = null;
        this.notify();
    }

    /** option — индекс варианта в банке (0 — правильный) или DONT_KNOW */
    answer(option: number): void {
        const { card, session, queue } = this;
        if (!card || !session || !queue || card.isAnswered) return;
        card.picked = option;
        session.record(card.isCorrect);
        if (!card.isCorrect) queue.scheduleRetry(card.question.id);
        this.history.save(session);
        this.notify();
    }

    next(): void {
        if (this.card?.isAnswered) this.showNext();
    }

    private showNext(): void {
        if (!this.queue) return;
        const item = this.queue.next();
        this.count += 1;
        this.card = new ReviewCard(this.count, this.byId.get(item.id) as ReviewQuestion, item.retry);
        this.notify();
    }
}
