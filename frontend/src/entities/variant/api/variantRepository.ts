import { API, apiClient } from '../../../shared/api';
import { AttemptMapper, type AttemptData, type AttemptDto } from '../../attempt';
import type { Difficulty } from '../../exam-task';
import type { Variant, VariantDto } from '../model/types';

const toVariant = (v: VariantDto): Variant => ({
    id: v.id,
    kind: v.kind,
    title: v.title,
    description: v.description,
    publisher: v.publisher,
    difficulty: v.difficulty as Difficulty | null,
    isStandard: v.is_standard,
    numbers: v.numbers,
    taskCount: v.task_count,
    maxScore: v.max_score,
    timeLimitSec: v.time_limit_sec,
    publishedAt: v.published_at,
    solvedStudents: v.solved_students,
    lastAttempt: v.last_attempt && AttemptMapper.brief(v.last_attempt),
    bestAttempt: v.best_attempt && AttemptMapper.brief(v.best_attempt),
    inProgressAttemptId: v.in_progress_attempt_id,
});

export const variantRepository = {
    /** Весь каталог предмета: фильтры и сортировку делает страница */
    async getAll(): Promise<Variant[]> {
        const { data } = await apiClient.get<VariantDto[]>(API.variants.list);
        return data.map(toVariant);
    },

    /** Один вариант — для стартовой страницы */
    async getOne(variantId: number): Promise<Variant> {
        const { data } = await apiClient.get<VariantDto>(API.variants.one(variantId));
        return toVariant(data);
    },

    /** Приступить к варианту: всегда новая попытка, незаконченная бросается */
    async start(variantId: number): Promise<AttemptData> {
        const { data } = await apiClient.post<AttemptDto>(API.variants.start(variantId));
        return AttemptMapper.attempt(data);
    },
};
