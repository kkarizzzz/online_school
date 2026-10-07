import { JsonStorage, percent } from '../../../shared/lib';
import type { ReviewModeId } from './ReviewMode';
import type { ReviewSession, ReviewSessionRecord } from './ReviewSession';

export interface ReviewSummary {
    sessions: number;
    answers: number;
    accuracy: number;
    bestStreak: number;
}

/**
 * История повторений на этом устройстве (последние LIMIT).
 * Позже переедет на сервер — интерфейс класса при этом не изменится.
 */
export class ReviewHistory {
    private static readonly LIMIT = 50;
    private readonly storage = new JsonStorage<ReviewSessionRecord[]>('review:sessions');

    list(): ReviewSessionRecord[] {
        const list = this.storage.read();
        return Array.isArray(list) ? list : [];
    }

    /** Сохраняет повторение после каждого ответа — закрытая вкладка ничего не теряет */
    save(session: ReviewSession): void {
        const list = this.list().filter((s) => s.id !== session.id);
        list.push(session.toRecord());
        this.storage.write(list.slice(-ReviewHistory.LIMIT));
    }

    lastOf(mode: ReviewModeId): ReviewSessionRecord | null {
        return this.list().filter((s) => s.mode === mode).at(-1) ?? null;
    }

    recent(count: number): ReviewSessionRecord[] {
        return this.list().slice(-count).reverse();
    }

    summary(): ReviewSummary | null {
        const list = this.list();
        if (!list.length) return null;
        const answers = list.reduce((sum, s) => sum + s.answers, 0);
        const correct = list.reduce((sum, s) => sum + s.correct, 0);
        return {
            sessions: list.length,
            answers,
            accuracy: percent(correct, answers),
            bestStreak: Math.max(...list.map((s) => s.bestStreak)),
        };
    }
}
