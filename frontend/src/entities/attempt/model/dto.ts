// Попытка в ответах сервера (snake_case) и перевод в модели фронтенда

import { ExamTaskMapper, type ExamTaskDto, type TaskRevealDto } from '../../exam-task';
import type { AttemptBrief, AttemptData, AttemptStatus, TaskSetKind } from './types';

export interface AttemptBriefDto {
    id: number;
    status: AttemptStatus;
    answered: number;
    primary_score: number | null;
    secondary_score: number | null;
    max_score: number | null;
    started_at: string;
    submitted_at: string | null;
    time_spent_sec: number;
    is_late: boolean;
}

interface ItemResultDto extends TaskRevealDto {
    is_correct: boolean | null;
    score: number | null;
    needs_review: boolean;
    reviewer_comment: string | null;
}

interface AttemptItemDto {
    position: number;
    max_score: number;
    task: ExamTaskDto;
    answer: string | null;
    files: { filename: string; url: string }[];
    result: ItemResultDto | null;
}

export interface AttemptDto {
    id: number;
    status: AttemptStatus;
    set: { id: number; kind: TaskSetKind; title: string; subject: string; is_standard: boolean; time_limit_sec: number | null };
    student_assignment_id: number | null;
    deadline_at: string | null;
    started_at: string;
    expires_at: string | null;
    submitted_at: string | null;
    server_now: string;
    time_spent_sec: number;
    current_position: number;
    is_late: boolean;
    is_rated: boolean;
    max_score: number | null;
    primary_score: number | null;
    secondary_score: number | null;
    answered: number;
    items: AttemptItemDto[];
}

export const AttemptMapper = {
    brief: (b: AttemptBriefDto): AttemptBrief => ({
        id: b.id,
        status: b.status,
        answered: b.answered,
        primaryScore: b.primary_score,
        secondaryScore: b.secondary_score,
        maxScore: b.max_score,
        startedAt: b.started_at,
        submittedAt: b.submitted_at,
        timeSpentSec: b.time_spent_sec,
        isLate: b.is_late,
    }),

    attempt: (a: AttemptDto): AttemptData => ({
        id: a.id,
        status: a.status,
        set: {
            id: a.set.id,
            kind: a.set.kind,
            title: a.set.title,
            subject: a.set.subject,
            isStandard: a.set.is_standard,
            timeLimitSec: a.set.time_limit_sec,
        },
        studentAssignmentId: a.student_assignment_id,
        deadlineAt: a.deadline_at,
        startedAt: a.started_at,
        expiresAt: a.expires_at,
        submittedAt: a.submitted_at,
        clockOffset: new Date(a.server_now).getTime() - Date.now(),
        timeSpentSec: a.time_spent_sec,
        currentPosition: a.current_position,
        isLate: a.is_late,
        isRated: a.is_rated,
        maxScore: a.max_score,
        primaryScore: a.primary_score,
        secondaryScore: a.secondary_score,
        answered: a.answered,
        items: a.items.map((i) => ({
            position: i.position,
            maxScore: i.max_score,
            task: ExamTaskMapper.task(i.task),
            answer: i.answer,
            files: i.files,
            result: i.result && {
                ...ExamTaskMapper.reveal(i.result),
                isCorrect: i.result.is_correct,
                score: i.result.score,
                needsReview: i.result.needs_review,
                reviewerComment: i.result.reviewer_comment,
            },
        })),
    }),
};
