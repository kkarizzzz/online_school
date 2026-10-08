// Задание в ответах сервера (snake_case) и перевод в модель фронтенда

import type { AnswerType, Difficulty, ExamTask, TaskReveal } from './types';

export interface ExamTaskDto {
    id: number;
    task_number: number;
    part: number;
    difficulty: number;
    max_score: number;
    answer_type: AnswerType;
    topic_id: number | null;
    topic: string | null;
    subtopic: string | null;
    sources: string[];
    shared_text: string | null;
    condition: string;
    attachments: { filename: string; url: string }[];
    similar_count: number;
}

export interface TaskRevealDto {
    correct_answer: string;
    solution: string | null;
    solution_video_url: string | null;
    grade_criteria: string | null;
}

export const ExamTaskMapper = {
    task: (t: ExamTaskDto): ExamTask => ({
        id: t.id,
        taskNumber: t.task_number,
        part: t.part,
        difficulty: Math.min(Math.max(t.difficulty, 1), 4) as Difficulty,
        maxScore: t.max_score,
        answerType: t.answer_type,
        topicId: t.topic_id,
        topic: t.topic,
        subtopic: t.subtopic,
        sources: t.sources,
        sharedText: t.shared_text,
        condition: t.condition,
        attachments: t.attachments,
        similarCount: t.similar_count,
    }),

    reveal: (r: TaskRevealDto): TaskReveal => ({
        correctAnswer: r.correct_answer,
        solution: r.solution,
        solutionVideoUrl: r.solution_video_url,
        gradeCriteria: r.grade_criteria,
    }),
};
