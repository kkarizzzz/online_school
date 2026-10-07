import { JsonStorage } from '../../../shared/lib';
import { Curriculum } from '../model/Curriculum';
import type { LessonSummaryData } from '../model/types';
import type { CurriculumRepository } from './CurriculumRepository';
import { CURRICULUM_MOCK } from './mock/curriculum.data';
import { LESSON_SUMMARIES_MOCK } from './mock/summaries.data';

/** Демо: всё до этого урока считается пройденным, пока прогресс не приходит с бэкенда */
const DEMO_POSITION = '3.2.3';

/**
 * Программа из сгенерированного файла, прогресс — демо + уроки, пройденные на этом устройстве.
 * Заменяется на HTTP-реализацию, когда появится API программы.
 */
export class MockCurriculumRepository implements CurriculumRepository {
    private readonly completed = new JsonStorage<string[]>('curriculum:completed');
    private curriculum: Curriculum | null = null;

    async getCurriculum(): Promise<Curriculum> {
        this.curriculum ??= new Curriculum(CURRICULUM_MOCK);
        return this.curriculum;
    }

    async getCompletedLessonIds(): Promise<string[]> {
        const curriculum = await this.getCurriculum();
        const demoEnd = curriculum.lesson(DEMO_POSITION)?.seq ?? 0;
        const demo = curriculum.lessons.slice(0, demoEnd).map((l) => l.id);
        return [...new Set([...demo, ...(this.completed.read() ?? [])])];
    }

    async getSummary(lessonId: string): Promise<LessonSummaryData | null> {
        return LESSON_SUMMARIES_MOCK[lessonId] ?? null;
    }

    async completeLesson(lessonId: string): Promise<void> {
        const list = this.completed.read() ?? [];
        if (!list.includes(lessonId)) this.completed.write([...list, lessonId]);
    }
}
