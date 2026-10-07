import type { LessonContentDto } from '../../../entities/lesson';
import { JsonStorage, Observable } from '../../../shared/lib';
import { ItemProgress, type ItemProgressData } from './ItemProgress';
import { ChoiceItem, InputItem, type LessonItem } from './LessonItem';
import { LessonStep, VideoStep } from './LessonStep';

interface SessionData {
    step: number;
    /** Самый дальний открытый шаг */
    max: number;
    watched: Record<number, boolean>;
    items: Record<string, ItemProgressData>;
}

export interface LessonStats {
    questions: number;
    questionsFirstTry: number;
    tasks: number;
    tasksSolved: number;
    videosWatched: number;
}

export interface WeakItem {
    stepIndex: number;
    step: LessonStep;
    item: LessonItem;
}

/**
 * Прохождение урока: шаги по порядку, следующий открывается после ответа на все вопросы текущего.
 * Последний виртуальный шаг (finishIndex) — итог. Прогресс хранится на устройстве.
 */
export class LessonSession extends Observable {
    readonly steps: LessonStep[];
    readonly videos: VideoStep[];
    /** Индекс виртуального шага «Итог» */
    readonly finishIndex: number;

    private readonly storage: JsonStorage<SessionData>;
    private readonly onFinish: () => void;
    private data: SessionData;
    private readonly progressCache = new Map<string, ItemProgress>();
    private resets = 0;

    constructor(lessonId: string, content: LessonContentDto, onFinish: () => void) {
        super();
        this.steps = content.steps.map(LessonStep.from);
        this.videos = this.steps.filter((s): s is VideoStep => s instanceof VideoStep);
        this.finishIndex = this.steps.length;
        this.onFinish = onFinish;
        this.storage = new JsonStorage(`lesson:${lessonId}`);
        this.data = { ...LessonSession.empty(), ...this.storage.read() };
    }

    private static empty(): SessionData {
        return { step: 0, max: 0, watched: {}, items: {} };
    }

    // ------------------------------- чтение -------------------------------

    get current(): number {
        return this.data.step;
    }

    /** Меняется при сбросе урока — по нему пересоздаются поля ввода */
    get epoch(): number {
        return this.resets;
    }

    get isFinished(): boolean {
        return this.data.max === this.finishIndex;
    }

    get videoSeconds(): number {
        return this.videos.reduce((sum, v) => sum + v.duration, 0);
    }

    get practiceTaskCount(): number {
        return this.steps.filter((s) => s.kind === 'practice').reduce((sum, s) => sum + s.items.length, 0);
    }

    progress(stepIndex: number, itemIndex: number): ItemProgress {
        const key = `${stepIndex}:${itemIndex}`;
        let progress = this.progressCache.get(key);
        if (!progress) {
            progress = new ItemProgress(this.data.items[key]);
            this.progressCache.set(key, progress);
        }
        return progress;
    }

    stepCounts(stepIndex: number): { done: number; total: number } {
        const items = this.steps[stepIndex].items;
        const done = items.filter((_, ii) => this.progress(stepIndex, ii).isResolved).length;
        return { done, total: items.length };
    }

    isStepDone(stepIndex: number): boolean {
        if (stepIndex === this.finishIndex) return this.isFinished;
        const { done, total } = this.stepCounts(stepIndex);
        return done === total;
    }

    isReachable(stepIndex: number): boolean {
        return stepIndex <= this.data.max;
    }

    isWatched(stepIndex: number): boolean {
        return !!this.data.watched[stepIndex];
    }

    /** Подпись шага на шкале: «Ролик 2», «Практика», «Итог» */
    stepLabel(stepIndex: number): string {
        if (stepIndex === this.finishIndex) return 'Итог';
        const step = this.steps[stepIndex];
        return step instanceof VideoStep ? `Ролик ${this.videos.indexOf(step) + 1}` : 'Практика';
    }

    stats(): LessonStats {
        const stats: LessonStats = { questions: 0, questionsFirstTry: 0, tasks: 0, tasksSolved: 0, videosWatched: 0 };
        this.steps.forEach((step, si) => step.items.forEach((_, ii) => {
            const p = this.progress(si, ii);
            if (step.kind === 'video') {
                stats.questions += 1;
                if (p.isSolvedFirstTry) stats.questionsFirstTry += 1;
            } else {
                stats.tasks += 1;
                if (p.isSolved) stats.tasksSolved += 1;
            }
        }));
        stats.videosWatched = this.videos.filter((v) => this.isWatched(this.steps.indexOf(v))).length;
        return stats;
    }

    /** Процент усвоения: вопросы с первой попытки + задачи без открытого решения */
    get score(): number {
        const s = this.stats();
        const total = s.questions + s.tasks;
        return total ? Math.round(((s.questionsFirstTry + s.tasksSolved) / total) * 100) : 0;
    }

    /** Что стоит повторить: открытые решения и вопросы с ошибками */
    weakItems(): WeakItem[] {
        const weak: WeakItem[] = [];
        this.steps.forEach((step, si) => step.items.forEach((item, ii) => {
            const p = this.progress(si, ii);
            if (p.status === 'shown' || (step.kind === 'video' && p.tries)) weak.push({ stepIndex: si, step, item });
        }));
        return weak;
    }

    // ------------------------------- действия -------------------------------

    /** Переход на шаг; вперёд — только через пройденный шаг */
    go(stepIndex: number): boolean {
        if (stepIndex < 0 || stepIndex > this.finishIndex) return false;
        if (stepIndex > this.data.max) {
            if (stepIndex !== this.data.max + 1 || !this.isStepDone(this.data.max)) return false;
            this.data.max = stepIndex;
            if (stepIndex === this.finishIndex) this.onFinish();
        }
        this.data.step = stepIndex;
        this.commit();
        return true;
    }

    /** true — ответ верный */
    answerChoice(stepIndex: number, itemIndex: number, option: number): boolean {
        const item = this.steps[stepIndex].items[itemIndex];
        const progress = this.progress(stepIndex, itemIndex);
        if (!(item instanceof ChoiceItem) || progress.isResolved) return false;
        const ok = item.answer(option, progress);
        this.commit();
        return ok;
    }

    /** true — ответ верный */
    answerInput(stepIndex: number, itemIndex: number, value: string): boolean {
        const item = this.steps[stepIndex].items[itemIndex];
        const progress = this.progress(stepIndex, itemIndex);
        if (!(item instanceof InputItem) || progress.isResolved) return false;
        const ok = item.answer(value, progress);
        this.commit();
        return ok;
    }

    showHint(stepIndex: number, itemIndex: number): void {
        this.progress(stepIndex, itemIndex).hint = true;
        this.commit();
    }

    showSolution(stepIndex: number, itemIndex: number): void {
        this.progress(stepIndex, itemIndex).status = 'shown';
        this.commit();
    }

    markWatched(stepIndex: number): void {
        if (this.data.watched[stepIndex]) return;
        this.data.watched[stepIndex] = true;
        this.commit();
    }

    reset(): void {
        this.data = LessonSession.empty();
        this.progressCache.clear();
        this.resets += 1;
        this.commit();
    }

    private commit(): void {
        this.progressCache.forEach((p, key) => {
            this.data.items[key] = p.toJSON();
        });
        this.storage.write(this.data);
        this.notify();
    }
}
