import { API, apiClient } from '../../../shared/api';
import { percent } from '../../../shared/lib';
import type { ReviewModeId } from './ReviewMode';
import type { ReviewSession, ReviewSessionRecord } from './ReviewSession';

export interface ReviewSummary {
    sessions: number;
    answers: number;
    accuracy: number;
    bestStreak: number;
}

interface ReviewSessionDto {
    id: number;
    mode: ReviewModeId;
    started: number;
    answers: number;
    correct: number;
    best_streak: number;
}

/**
 * История повторений ученика (последние LIMIT). Хранится на сервере:
 * load() — один раз перед стартовым экраном, save() — после каждого ответа.
 */
export class ReviewHistory {
    private static readonly LIMIT = 50;
    private records: ReviewSessionRecord[];

    constructor(records: ReviewSessionRecord[]) {
        this.records = records;
    }

    static async load(): Promise<ReviewHistory> {
        const { data } = await apiClient.get<ReviewSessionDto[]>(API.review.sessions, { params: { limit: ReviewHistory.LIMIT } });
        return new ReviewHistory(data.map((s) => ({
            id: s.id, mode: s.mode, started: s.started, answers: s.answers, correct: s.correct, bestStreak: s.best_streak,
        })));
    }

    list(): ReviewSessionRecord[] {
        return this.records;
    }

    /** Сохраняет повторение после каждого ответа — закрытая вкладка ничего не теряет */
    save(session: ReviewSession): void {
        const record = session.toRecord();
        this.records = [...this.records.filter((s) => s.id !== record.id), record].slice(-ReviewHistory.LIMIT);
        void apiClient.put(API.review.session(record.id), {
            mode: record.mode,
            started: record.started,
            answers: record.answers,
            correct: record.correct,
            best_streak: record.bestStreak,
        }).catch(() => {
            // Не сохранилось — следующий ответ перезапишет повторение целиком
        });
    }

    lastOf(mode: ReviewModeId): ReviewSessionRecord | null {
        return this.records.filter((s) => s.mode === mode).at(-1) ?? null;
    }

    recent(count: number): ReviewSessionRecord[] {
        return this.records.slice(-count).reverse();
    }

    summary(): ReviewSummary | null {
        const list = this.records;
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
