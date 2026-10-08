import type { Curriculum } from '../model/Curriculum';
import type { LessonSummaryData } from '../model/types';

export interface CurriculumWithProgress {
    curriculum: Curriculum;
    completedLessonIds: string[];
}

/** Программа курса и прогресс ученика */
export interface CurriculumRepository {
    getCurriculum(): Promise<CurriculumWithProgress>;
    /** Ручной конспект урока; null — конспект собирается из плана */
    getSummary(lessonId: string): Promise<LessonSummaryData | null>;
    completeLesson(lessonId: string, percent?: number): Promise<void>;
}
