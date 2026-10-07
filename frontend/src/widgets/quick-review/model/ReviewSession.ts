import { percent } from '../../../shared/lib';
import type { ReviewModeId } from './ReviewMode';

/** Итог повторения, как он хранится в истории */
export interface ReviewSessionRecord {
    id: number;
    mode: ReviewModeId;
    started: number;
    answers: number;
    correct: number;
    bestStreak: number;
}

/** Статистика одного повторения: ответы, точность, серия */
export class ReviewSession {
    readonly id: number;
    readonly mode: ReviewModeId;
    readonly started: number;
    answers = 0;
    correct = 0;
    streak = 0;
    bestStreak = 0;

    constructor(mode: ReviewModeId) {
        this.id = Date.now();
        this.started = this.id;
        this.mode = mode;
    }

    get accuracy(): number {
        return percent(this.correct, this.answers);
    }

    record(isCorrect: boolean): void {
        this.answers += 1;
        if (isCorrect) {
            this.correct += 1;
            this.streak += 1;
            this.bestStreak = Math.max(this.bestStreak, this.streak);
        } else {
            this.streak = 0;
        }
    }

    toRecord(): ReviewSessionRecord {
        const { id, mode, started, answers, correct, bestStreak } = this;
        return { id, mode, started, answers, correct, bestStreak };
    }
}
