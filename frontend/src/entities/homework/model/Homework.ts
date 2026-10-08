import { isBlankAnswer, makeExamTask, type ExamTask, type ExamTaskNumber } from '../../exam-task';
import { formatDayMonth, pluralize } from '../../../shared/lib';
import type { HomeworkDto, HomeworkResult, HomeworkSession, HomeworkStatus } from './types';

/** Задача ДЗ: задание ЕГЭ, стоит 1 балл (верно / неверно) */
export type HomeworkTask = ExamTask;

/** Домашнее задание: состав, срок и прогресс ученика */
export class Homework {
    readonly id: string;
    readonly title: string;
    readonly topic: string;
    readonly numbers: ExamTaskNumber[];
    readonly taskCount: number;
    readonly deadline: string;
    readonly session: HomeworkSession | null;
    readonly result: HomeworkResult | null;
    private readonly assigned: HomeworkDto['status'];
    private taskList: HomeworkTask[] | null = null;

    constructor(dto: HomeworkDto) {
        this.id = dto.id;
        this.title = dto.title;
        this.topic = dto.topic;
        this.numbers = dto.numbers;
        this.taskCount = dto.tasks;
        this.deadline = dto.deadline;
        this.assigned = dto.status;
        this.session = dto.session;
        this.result = dto.result;
    }

    /** Сданное ДЗ — выполнено, даже если сдано после срока */
    get status(): HomeworkStatus {
        return this.result ? 'done' : this.assigned;
    }

    get isOverdue(): boolean {
        return this.assigned === 'overdue';
    }

    /**
     * Задачи: `taskCount` заданий по номерам из `numbers`, сгруппированные по номеру.
     * Пока задачи собирает генератор по зерну — одинаковые при каждом открытии.
     */
    get tasks(): HomeworkTask[] {
        this.taskList ??= Array.from({ length: this.taskCount }, (_, i) => this.numbers[i % this.numbers.length])
            .sort((a, b) => a - b)
            .map((n, i) => makeExamTask(n, `${this.id}:${i}`));
        return this.taskList;
    }

    get answeredCount(): number {
        return (this.session?.answers ?? []).filter((a) => !isBlankAnswer(a)).length;
    }

    get correctCount(): number {
        return this.result ? this.result.points.filter((p) => p > 0).length : 0;
    }

    /** «8 задач» */
    get sizeLabel(): string {
        return pluralize(this.taskCount, 'задача', 'задачи', 'задач');
    }

    /** «до 13 октября, 23:59», «сдано 8 октября», «дедлайн истёк 5 октября» */
    get deadlineLabel(): string {
        if (this.result) return `сдано ${formatDayMonth(this.result.date)}${this.result.late ? ' · после срока' : ''}`;
        if (this.isOverdue) return `дедлайн истёк ${formatDayMonth(this.deadline)}`;
        return `до ${formatDayMonth(this.deadline)}, 23:59`;
    }

    /** «Не начато», «3 из 10 решено», «8 из 9 верно» */
    get progressLabel(): string {
        if (this.result) return `${this.correctCount} из ${this.result.points.length} верно`;
        const n = this.answeredCount;
        return n ? `${n} из ${this.taskCount} решено` : 'Не начато';
    }
}
