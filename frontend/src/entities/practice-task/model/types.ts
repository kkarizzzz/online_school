// Нарешка: задания банка и темы, как их отдаёт API
import type { AnswerType, ExamTask } from '../../exam-task';

export type { AnswerType };

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

/** Задание без ответа и решения — то, что ученик видит до проверки */
export type PracticeTask = ExamTask;

export interface SubmitResult {
    isCorrect: boolean | null;   // null — ответ проверит преподаватель
    score: number | null;
    maxScore: number;
    correctAnswer: string;
    solution: string | null;
    gradeCriteria: string | null;
}
