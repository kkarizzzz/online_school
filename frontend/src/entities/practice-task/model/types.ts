// Нарешка: номера ЕГЭ с темами и задания, как их отдаёт API
import type { AnswerType, Difficulty, ExamTask } from '../../exam-task';

export type { AnswerType, Difficulty };

/** Задания темы одной сложности */
export interface PracticeLevel {
    difficulty: Difficulty;
    taskCount: number;
    solvedCount: number;
}

/** Тема номера — в интерфейсе «подтема»: из них собирают персональную подборку */
export interface PracticeTopic {
    id: number;
    name: string;
    /** Только сложности, в которых есть задания */
    levels: PracticeLevel[];
}

export interface PracticeNumber {
    number: number;
    title: string | null;
    part: number;
    topics: PracticeTopic[];
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

/** Ответ и решение, открытые без попытки */
export interface TaskSolution {
    correctAnswer: string;
    solution: string | null;
}
