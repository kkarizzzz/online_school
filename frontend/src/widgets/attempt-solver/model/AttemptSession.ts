import { isBlankAnswer, isCorrectAnswer } from '../../../entities/exam-task';
import type { Homework, HomeworkRepository, HomeworkResult, HomeworkSession, HomeworkTask } from '../../../entities/homework';
import { Observable } from '../../../shared/lib';

/**
 * Выполнение ДЗ: ответы по задачам и открытая задача.
 * Каждое изменение сразу уходит в репозиторий — закрытая вкладка ничего не теряет,
 * а при следующем открытии ДЗ продолжится с той же задачи.
 */
export class HomeworkAttempt extends Observable {
    readonly homework: Homework;
    readonly tasks: HomeworkTask[];
    private readonly repository: HomeworkRepository;
    private readonly session: HomeworkSession;

    constructor(homework: Homework, repository: HomeworkRepository) {
        super();
        this.homework = homework;
        this.tasks = homework.tasks;
        this.repository = repository;
        const saved = homework.session;
        this.session = saved
            ? { ...saved, answers: [...saved.answers], current: Math.min(Math.max(saved.current, 0), this.tasks.length - 1) }
            : { startedAt: Date.now(), answers: [], current: 0 };
        this.save();
    }

    get current(): number {
        return this.session.current;
    }

    get task(): HomeworkTask {
        return this.tasks[this.session.current];
    }

    get isFirst(): boolean {
        return this.session.current === 0;
    }

    get isLast(): boolean {
        return this.session.current === this.tasks.length - 1;
    }

    get startedAt(): number {
        return this.session.startedAt;
    }

    answerOf(i: number): string {
        return this.session.answers[i] ?? '';
    }

    isAnswered(i: number): boolean {
        return !isBlankAnswer(this.session.answers[i]);
    }

    get answeredCount(): number {
        return this.tasks.filter((_, i) => this.isAnswered(i)).length;
    }

    get unansweredCount(): number {
        return this.tasks.length - this.answeredCount;
    }

    setAnswer(value: string): void {
        this.session.answers[this.session.current] = value;
        this.save();
        this.notify();
    }

    goTo(i: number): void {
        if (i < 0 || i >= this.tasks.length || i === this.session.current) return;
        this.session.current = i;
        this.save();
        this.notify();
    }

    /** Итог сдачи: каждая задача — 1 (верно) или 0 */
    toResult(): HomeworkResult {
        const answers = this.tasks.map((_, i) => this.answerOf(i));
        return {
            points: this.tasks.map((t, i) => (isCorrectAnswer(answers[i], t.answer) ? 1 : 0)),
            answers,
            seconds: Math.floor((Date.now() - this.session.startedAt) / 1000),
            date: new Date().toISOString(),
            ...(this.homework.isOverdue ? { late: true } : {}),
        };
    }

    private save(): void {
        void this.repository.saveSession(this.homework.id, { ...this.session, answers: [...this.session.answers] });
    }
}
