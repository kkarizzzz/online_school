export type ItemStatus = 'ok' | 'shown';

export interface ItemProgressData {
    tries: number;
    wrong: number[];
    hint: boolean;
    status?: ItemStatus;
    value?: string;
    error?: string | null;
}

/** Состояние ответа на один вопрос или задачу урока */
export class ItemProgress {
    tries: number;
    /** Неверно выбранные варианты */
    wrong: number[];
    hint: boolean;
    /** undefined — ещё не решено; ok — решено; shown — открыто решение */
    status?: ItemStatus;
    /** Последний введённый ответ */
    value: string;
    error: string | null;

    constructor(data?: Partial<ItemProgressData>) {
        this.tries = data?.tries ?? 0;
        this.wrong = data?.wrong ?? [];
        this.hint = data?.hint ?? false;
        this.status = data?.status;
        this.value = data?.value ?? '';
        this.error = data?.error ?? null;
    }

    get isResolved(): boolean {
        return this.status === 'ok' || this.status === 'shown';
    }

    get isSolved(): boolean {
        return this.status === 'ok';
    }

    get isSolvedFirstTry(): boolean {
        return this.status === 'ok' && this.tries === 0;
    }

    toJSON(): ItemProgressData {
        return { tries: this.tries, wrong: this.wrong, hint: this.hint, status: this.status, value: this.value, error: this.error };
    }
}
