import type { Curriculum } from '../model/Curriculum';
import type { LessonSummaryData } from '../model/types';

/** Источник программы курса и прогресса ученика */
export interface CurriculumRepository {
    getCurriculum(): Promise<Curriculum>;
    getCompletedLessonIds(): Promise<string[]>;
    /** Ручной конспект урока; null — конспект собирается из плана */
    getSummary(lessonId: string): Promise<LessonSummaryData | null>;
    completeLesson(lessonId: string): Promise<void>;
}

