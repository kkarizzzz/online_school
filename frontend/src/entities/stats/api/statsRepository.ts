import { API, apiClient } from '../../../shared/api';
import type { StudentStats } from '../model/types';

interface StudentStatsDto {
    streak: number;
    rank_percent: number | null;
    subjects: { subject: string; tasks_solved: number; task_count: number }[];
    totals: {
        answered: number; correct: number; accuracy: number | null;
        tasks_solved: number; seconds: number; lessons_done: number;
    };
    week: { day: string; answered: number; correct: number; seconds: number; lessons_done: number }[];
    homework: { current: number; overdue: number; done: number; late: number; avg_percent: number | null };
    mock_exams: {
        attempt_id: number; title: string; subject: string; primary_score: number | null;
        secondary_score: number | null; max_score: number | null; submitted_at: string;
    }[];
    achievements: { code: string; title: string; description: string; unlocked_at: string | null }[];
}

const toStats = (d: StudentStatsDto): StudentStats => ({
    streak: d.streak,
    rankPercent: d.rank_percent,
    subjects: d.subjects.map((s) => ({ subject: s.subject, tasksSolved: s.tasks_solved, taskCount: s.task_count })),
    totals: {
        answered: d.totals.answered,
        correct: d.totals.correct,
        accuracy: d.totals.accuracy,
        tasksSolved: d.totals.tasks_solved,
        seconds: d.totals.seconds,
        lessonsDone: d.totals.lessons_done,
    },
    week: d.week.map((w) => ({
        day: w.day, answered: w.answered, correct: w.correct, seconds: w.seconds, lessonsDone: w.lessons_done,
    })),
    homework: { ...d.homework, avgPercent: d.homework.avg_percent },
    mockExams: d.mock_exams.map((e) => ({
        attemptId: e.attempt_id,
        title: e.title,
        subject: e.subject,
        primaryScore: e.primary_score,
        secondaryScore: e.secondary_score,
        maxScore: e.max_score,
        submittedAt: e.submitted_at,
    })),
    achievements: d.achievements.map((a) => ({
        code: a.code, title: a.title, description: a.description, unlockedAt: a.unlocked_at,
    })),
});

export const statsRepository = {
    async getMine(): Promise<StudentStats> {
        const { data } = await apiClient.get<StudentStatsDto>(API.stats.me);
        return toStats(data);
    },
};
