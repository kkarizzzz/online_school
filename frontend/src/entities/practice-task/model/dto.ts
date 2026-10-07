// Формат ответа сервера (snake_case) и перевод в модели фронтенда

import type { AnswerType, PracticeTask, PracticeTopic, PracticeTopics, SubmitResult } from './types';

export interface PracticeTopicDto {
    id: number;
    task_number: number;
    name: string;
    subtopics: string[];
    task_count: number;
    solved_count: number;
}

export interface PracticeTopicsDto {
    topics: PracticeTopicDto[];
    last_topic_id: number | null;
}

export interface PracticeTaskDto {
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

export interface SubmitResultDto {
    is_correct: boolean | null;
    score: number | null;
    max_score: number;
    correct_answer: string;
    solution: string | null;
    grade_criteria: string | null;
}

const toTopic = (t: PracticeTopicDto): PracticeTopic => ({
    id: t.id,
    taskNumber: t.task_number,
    name: t.name,
    subtopics: t.subtopics,
    taskCount: t.task_count,
    solvedCount: t.solved_count,
});

export const PracticeMapper = {
    topics: (dto: PracticeTopicsDto): PracticeTopics => ({
        topics: dto.topics.map(toTopic),
        lastTopicId: dto.last_topic_id,
    }),

    task: (t: PracticeTaskDto): PracticeTask => ({
        id: t.id,
        taskNumber: t.task_number,
        part: t.part,
        difficulty: t.difficulty,
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

    result: (r: SubmitResultDto): SubmitResult => ({
        isCorrect: r.is_correct,
        score: r.score,
        maxScore: r.max_score,
        correctAnswer: r.correct_answer,
        solution: r.solution,
        gradeCriteria: r.grade_criteria,
    }),
};
