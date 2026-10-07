// Нарешка: задания банка и темы, как их отдаёт API

export type AnswerType = 'short' | 'digits_set' | 'sequence' | 'detailed';

export interface PracticeTopic {
    id: number;
    taskNumber: number;
    name: string;
    subtopics: string[];
    taskCount: number;
    solvedCount: number;
}

export interface PracticeTopics {
    topics: PracticeTopic[];
    /** Тема последней попытки — её предлагаем продолжить */
    lastTopicId: number | null;
}

export interface PracticeAttachment {
    filename: string;
    url: string;
}

/** Задание без ответа и решения — то, что ученик видит до проверки */
export interface PracticeTask {
    id: number;
    taskNumber: number;
    part: number;
    difficulty: number;
    maxScore: number;
    answerType: AnswerType;
    topicId: number | null;
    topic: string | null;
    subtopic: string | null;
    sources: string[];
    sharedText: string | null;
    condition: string;           // Markdown + LaTeX
    attachments: PracticeAttachment[];
    similarCount: number;
}

export interface SubmitResult {
    isCorrect: boolean | null;   // null — ответ проверит куратор
    score: number | null;
    maxScore: number;
    correctAnswer: string;
    solution: string | null;
    gradeCriteria: string | null;
}
