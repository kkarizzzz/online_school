import { isAxiosError } from 'axios';
import type { AttemptData, AttemptItem, AttemptRepository } from '../../../entities/attempt';
import { isBlankAnswer, type TaskAttachment } from '../../../entities/exam-task';
import { Observable, parseApiError } from '../../../shared/lib';

/** Ответ уходит на сервер через столько мс после последнего нажатия клавиши */
const SAVE_DELAY = 600;

/**
 * Прохождение набора: ответы, приложенные фото и открытое задание.
 * Ответы сохраняются на сервере черновиком (с задержкой после ввода), поэтому закрытая вкладка
 * ничего не теряет: при следующем открытии попытка продолжится с того же задания.
 * Проверяются ответы только при сдаче.
 */
export class AttemptSession extends Observable {
    readonly data: AttemptData;
    private readonly repository: AttemptRepository;
    private readonly answers: string[];
    private readonly files: TaskAttachment[][];
    private readonly timers = new Map<number, ReturnType<typeof setTimeout>>();
    private readonly saving = new Set<Promise<void>>();
    private index: number;

    /** Последняя ошибка сохранения — показываем, пока следующее сохранение не пройдёт */
    saveError: string | null = null;
    /** Сервер больше не принимает ответы: время вышло или попытку сдали в другой вкладке */
    closed = false;
    uploading = false;

    constructor(data: AttemptData, repository: AttemptRepository) {
        super();
        this.data = data;
        this.repository = repository;
        this.answers = data.items.map((i) => i.answer ?? '');
        this.files = data.items.map((i) => [...i.files]);
        this.index = Math.min(Math.max(data.currentPosition, 0), data.items.length - 1);
    }

    get items(): AttemptItem[] {
        return this.data.items;
    }

    get current(): number {
        return this.index;
    }

    get item(): AttemptItem {
        return this.items[this.index];
    }

    get isFirst(): boolean {
        return this.index === 0;
    }

    get isLast(): boolean {
        return this.index === this.items.length - 1;
    }

    /** Начало и конец по часам браузера, мс */
    get startedAt(): number {
        return new Date(this.data.startedAt).getTime() - this.data.clockOffset;
    }

    get expiresAt(): number | null {
        return this.data.expiresAt ? new Date(this.data.expiresAt).getTime() - this.data.clockOffset : null;
    }

    answerOf(i: number): string {
        return this.answers[i] ?? '';
    }

    filesOf(i: number): TaskAttachment[] {
        return this.files[i] ?? [];
    }

    isAnswered(i: number): boolean {
        return !isBlankAnswer(this.answers[i]) || this.filesOf(i).length > 0;
    }

    get answeredCount(): number {
        return this.items.filter((_, i) => this.isAnswered(i)).length;
    }

    get unansweredCount(): number {
        return this.items.length - this.answeredCount;
    }

    setAnswer(value: string): void {
        const i = this.index;
        this.answers[i] = value;
        clearTimeout(this.timers.get(i));
        this.timers.set(i, setTimeout(() => this.saveAnswer(i), SAVE_DELAY));
        this.notify();
    }

    goTo(i: number): void {
        if (i < 0 || i >= this.items.length || i === this.index) return;
        this.flushAnswer(this.index);
        this.index = i;
        this.track(this.repository.savePosition(this.data.id, i, (Date.now() - this.startedAt) / 1000));
        this.notify();
    }

    async upload(file: File): Promise<void> {
        const i = this.index;
        this.uploading = true;
        this.notify();
        try {
            const saved = await this.repository.uploadFile(this.data.id, this.items[i].task.id, file);
            this.files[i] = [...this.filesOf(i), saved];
            this.saveError = null;
        } catch (error) {
            this.fail(error, 'Не удалось загрузить файл');
        } finally {
            this.uploading = false;
            this.notify();
        }
    }

    /** Дождаться, пока все ответы дойдут до сервера */
    async flush(): Promise<void> {
        for (const i of [...this.timers.keys()]) this.flushAnswer(i);
        await Promise.allSettled([...this.saving]);
    }

    /** Сдать: сначала досохранить ответы, потом проверка на сервере. Возвращает попытку с разбором */
    async submit(): Promise<AttemptData> {
        await this.flush();
        return this.repository.submit(this.data.id);
    }

    private flushAnswer(i: number): void {
        if (!this.timers.has(i)) return;
        clearTimeout(this.timers.get(i));
        this.saveAnswer(i);
    }

    private saveAnswer(i: number): void {
        this.timers.delete(i);
        this.track(this.repository.saveAnswer(this.data.id, this.items[i].task.id, this.answers[i] ?? ''));
    }

    private track(request: Promise<void>): void {
        const wrapped = request
            .then(() => {
                if (this.saveError) {
                    this.saveError = null;
                    this.notify();
                }
            })
            .catch((error: unknown) => {
                this.fail(error, 'Ответ не сохранился — проверьте интернет');
                this.notify();
            })
            .finally(() => this.saving.delete(wrapped));
        this.saving.add(wrapped);
    }

    private fail(error: unknown, fallback: string): void {
        if (isAxiosError(error) && error.response?.status === 409) this.closed = true;
        this.saveError = parseApiError(error, fallback);
    }
}
