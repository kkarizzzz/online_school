export type ReviewQuestionKind = 'theory' | 'calc';

/** Вопрос быстрого повторения. options[0] — правильный ответ, формулы — LaTeX в $...$ */
export interface ReviewQuestionDto {
    topic: string;
    kind: ReviewQuestionKind;
    q: string;
    options: string[];
    explain: string;
}

export interface ReviewQuestion extends ReviewQuestionDto {
    id: number;
}
