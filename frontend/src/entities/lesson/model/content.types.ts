// Содержимое урока: короткие ролики с вопросами и блоки задач на закрепление.
// В тексте вопросов допускается простая разметка: <sub>, <sup>, <b>.

export interface ChoiceItemDto {
    type: 'choice';
    q: string;
    options: string[];
    correct: number;     // индекс верного варианта
    explain: string;
}

export interface InputItemDto {
    type: 'input';
    q: string;
    answer: string[];    // любой из вариантов, сравнение как чисел: «3/2» == «1.5»
    hint?: string;
    explain: string;
}

export type LessonItemDto = ChoiceItemDto | InputItemDto;

export interface VideoStepDto {
    kind: 'video';
    title: string;
    src: string;
    poster: string;
    duration: number;    // секунды
    transcript: string[];
    questions: LessonItemDto[];
}

export interface PracticeStepDto {
    kind: 'practice';
    title: string;
    intro: string;
    tasks: LessonItemDto[];
}

export type LessonStepDto = VideoStepDto | PracticeStepDto;

export interface LessonContentDto {
    title: string;
    goal: string;
    steps: LessonStepDto[];
}
