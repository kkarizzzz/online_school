import type { ReviewQuestion } from '../../../entities/review-question';

export type ReviewModeId = 'theory' | 'calc' | 'mix';

/** Режим повторения: какие вопросы попадают в ленту */
export class ReviewMode {
    readonly id: ReviewModeId;
    readonly label: string;
    readonly description: string;

    private constructor(id: ReviewModeId, label: string, description: string) {
        this.id = id;
        this.label = label;
        this.description = description;
    }

    static readonly all: readonly ReviewMode[] = [
        new ReviewMode('theory', 'Теория', 'Формулы, определения и свойства — проверить, что база в голове.'),
        new ReviewMode('calc', 'Вычисления', 'Короткие примеры на счёт: степени, корни, проценты, производные.'),
        new ReviewMode('mix', 'Микс', 'Теория и вычисления вперемешку по всем темам.'),
    ];

    static find(id: string | null): ReviewMode | null {
        return ReviewMode.all.find((m) => m.id === id) ?? null;
    }

    /** «Микс» — главный режим, выделяется на старте */
    get isMix(): boolean {
        return this.id === 'mix';
    }

    includes(question: ReviewQuestion): boolean {
        return this.isMix || question.kind === this.id;
    }

    poolOf(questions: ReviewQuestion[]): ReviewQuestion[] {
        return questions.filter((q) => this.includes(q));
    }
}
