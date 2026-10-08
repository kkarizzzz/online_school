/** Номер задания ЕГЭ (профиль): 1–12 — краткий ответ, 13–19 — развёрнутый */
export type ExamTaskNumber = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19;

/** Как проверяется ответ: short — одно значение, digits_set — цифры в любом порядке, sequence — по порядку, detailed — преподавателем */
export type AnswerType = 'short' | 'digits_set' | 'sequence' | 'detailed';

/** Сложность задания и набора: 1 — базовый, 2 — средний, 3 — сложный, 4 — «гроб» */
export type Difficulty = 1 | 2 | 3 | 4;

export interface TaskAttachment {
    filename: string;
    url: string;
}

/** Задание, как его видит ученик до ответа: без ответа и разбора. Тексты — Markdown + LaTeX */
export interface ExamTask {
    id: number;
    taskNumber: number;
    part: number;
    difficulty: Difficulty;
    maxScore: number;
    answerType: AnswerType;
    /** Тема верхнего уровня */
    topicId: number | null;
    topic: string | null;
    subtopic: string | null;
    sources: string[];
    sharedText: string | null;
    condition: string;
    attachments: TaskAttachment[];
    /** Сколько ещё заданий в той же подтеме */
    similarCount: number;
}

/** Ответ и разбор — после ответа ученика или в банке */
export interface TaskReveal {
    correctAnswer: string;
    solution: string | null;
    solutionVideoUrl: string | null;
    gradeCriteria: string | null;
}
