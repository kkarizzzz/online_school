import type { ChoiceItemDto, InputItemDto, LessonItemDto } from '../../../entities/lesson';
import type { ItemProgress } from './ItemProgress';
import { NumericAnswer } from './NumericAnswer';

/** Вопрос под роликом или задача практики */
export abstract class LessonItem {
    abstract readonly type: LessonItemDto['type'];
    readonly question: string;
    readonly explain: string;
    readonly hint: string | null;

    constructor(question: string, explain: string, hint?: string) {
        this.question = question;
        this.explain = explain;
        this.hint = hint ?? null;
    }

    /** Правильный ответ для «Показать решение» */
    abstract get answerText(): string;

    static from(dto: LessonItemDto): LessonItem {
        return dto.type === 'choice' ? new ChoiceItem(dto) : new InputItem(dto);
    }
}

export class ChoiceItem extends LessonItem {
    readonly type = 'choice';
    readonly options: string[];
    readonly correct: number;

    constructor(dto: ChoiceItemDto) {
        super(dto.q, dto.explain);
        this.options = dto.options;
        this.correct = dto.correct;
    }

    get answerText(): string {
        return this.options[this.correct];
    }

    /** Отмечает выбор в progress; true — ответ верный */
    answer(option: number, progress: ItemProgress): boolean {
        if (option === this.correct) {
            progress.status = 'ok';
            return true;
        }
        progress.tries += 1;
        progress.wrong.push(option);
        return false;
    }
}

export class InputItem extends LessonItem {
    readonly type = 'input';
    readonly answers: string[];

    constructor(dto: InputItemDto) {
        super(dto.q, dto.explain, dto.hint);
        this.answers = dto.answer;
    }

    get answerText(): string {
        return this.answers[0];
    }

    /** Проверяет ввод и пишет результат в progress; true — ответ верный */
    answer(value: string, progress: ItemProgress): boolean {
        progress.value = value;
        progress.error = null;
        if (NumericAnswer.parse(value) === null) {
            progress.error = value.trim()
                ? 'Ответ должен быть числом: целым, десятичным (2,5) или дробью (5/2).'
                : 'Введите ответ.';
            return false;
        }
        if (NumericAnswer.matches(value, this.answers)) {
            progress.status = 'ok';
            return true;
        }
        progress.tries += 1;
        return false;
    }
}
