import { API, apiClient } from '../../../shared/api';
import { Curriculum } from '../model/Curriculum';
import type { CurriculumDto, LessonSummaryData } from '../model/types';
import type { CurriculumRepository, CurriculumWithProgress } from './CurriculumRepository';

interface CurriculumResponse {
    curriculum: CurriculumDto;
    completed_lesson_ids: string[];
}

interface LessonResponse {
    summary: LessonSummaryData | null;
}

export class HttpCurriculumRepository implements CurriculumRepository {
    async getCurriculum(): Promise<CurriculumWithProgress> {
        const { data } = await apiClient.get<CurriculumResponse>(API.curriculum);
        return { curriculum: new Curriculum(data.curriculum), completedLessonIds: data.completed_lesson_ids };
    }

    async getSummary(lessonId: string): Promise<LessonSummaryData | null> {
        const { data } = await apiClient.get<LessonResponse>(API.lessons.one(lessonId));
        return data.summary;
    }

    async completeLesson(lessonId: string, percent = 100): Promise<void> {
        await apiClient.post(API.lessons.complete(lessonId), { percent });
    }
}
