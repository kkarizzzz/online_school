// Формат ответа сервера (snake_case) и перевод в модели фронтенда

import { ExamTaskMapper, type ExamTaskDto } from '../../exam-task';
import type { Difficulty, PracticeNumber, PracticeTask, SubmitResult, TaskSolution } from './types';

export interface PracticeLevelDto {
    difficulty: Difficulty;
    task_count: number;
    solved_count: number;
}

export interface PracticeTopicDto {
    id: number;
    name: string;
    levels: PracticeLevelDto[];
}

export interface PracticeNumberDto {
    number: number;
    title: string | null;
    part: number;
    topics: PracticeTopicDto[];
}

export type PracticeTaskDto = ExamTaskDto;

export interface SubmitResultDto {
    is_correct: boolean | null;
    score: number | null;
    max_score: number;
    correct_answer: string;
    solution: string | null;
    grade_criteria: string | null;
}

export interface TaskSolutionDto {
    correct_answer: string;
    solution: string | null;
}

export const PracticeMapper = {
    numbers: (dto: PracticeNumberDto[]): PracticeNumber[] => dto.map((n) => ({
        number: n.number,
        title: n.title,
        part: n.part,
        topics: n.topics.map((t) => ({
            id: t.id,
            name: t.name,
            levels: t.levels.map((l) => ({ difficulty: l.difficulty, taskCount: l.task_count, solvedCount: l.solved_count })),
        })),
    })),

    task: (t: PracticeTaskDto): PracticeTask => ExamTaskMapper.task(t),

    result: (r: SubmitResultDto): SubmitResult => ({
        isCorrect: r.is_correct,
        score: r.score,
        maxScore: r.max_score,
        correctAnswer: r.correct_answer,
        solution: r.solution,
        gradeCriteria: r.grade_criteria,
    }),

    solution: (s: TaskSolutionDto): TaskSolution => ({ correctAnswer: s.correct_answer, solution: s.solution }),
};
