import { scoreLabel, type AttemptBrief } from '../../attempt';
import { formatDayMonth, pluralize } from '../../../shared/lib';
import type { HomeworkData, HomeworkStatus } from './types';

/** «13 октября, 23:59» */
const dayAndTime = (iso: string): string => {
    const time = new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
    return `${formatDayMonth(iso)}, ${time}`;
};

/** Домашнее задание ученика: состав, срок и прогресс. Задачи приходят в попытке (useHomeworkAttempt) */
export class Homework {
    readonly id: number;
    readonly title: string;
    readonly topic: string | null;
    readonly note: string | null;
    readonly numbers: number[];
    readonly taskCount: number;
    readonly deadlineAt: string | null;
    readonly status: HomeworkStatus;
    readonly attempt: AttemptBrief | null;

    constructor(data: HomeworkData) {
        this.id = data.id;
        this.title = data.title;
        this.topic = data.topic;
        this.note = data.note;
        this.numbers = data.numbers;
        this.taskCount = data.taskCount;
        this.deadlineAt = data.deadlineAt;
        this.status = data.status;
        this.attempt = data.attempt;
    }

    get isOverdue(): boolean {
        return this.status === 'overdue';
    }

    get isSubmitted(): boolean {
        return this.attempt?.submittedAt != null;
    }

    get answeredCount(): number {
        return this.attempt?.answered ?? 0;
    }

    /** «8 задач» */
    get sizeLabel(): string {
        return pluralize(this.taskCount, 'задача', 'задачи', 'задач');
    }

    /** «до 13 октября, 23:59», «сдано 8 октября», «дедлайн истёк 5 октября», «без срока» */
    get deadlineLabel(): string {
        const submitted = this.attempt?.submittedAt;
        if (submitted) return `сдано ${formatDayMonth(submitted)}${this.attempt?.isLate ? ' · после срока' : ''}`;
        if (!this.deadlineAt) return 'без срока';
        if (this.isOverdue) return `дедлайн истёк ${formatDayMonth(this.deadlineAt)}`;
        return `до ${dayAndTime(this.deadlineAt)}`;
    }

    /** «Не начато», «3 из 10 решено», «8 из 10 баллов», «на проверке» */
    get progressLabel(): string {
        if (this.attempt && this.isSubmitted) return scoreLabel(this.attempt);
        const n = this.answeredCount;
        return n ? `${n} из ${this.taskCount} решено` : 'Не начато';
    }
}
