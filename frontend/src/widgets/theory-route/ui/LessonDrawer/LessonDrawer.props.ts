import type { LearningProgress, Lesson } from '../../../../entities/curriculum';

export interface LessonDrawerProps {
    /** Последний открытый урок — остаётся, пока панель уезжает */
    lesson: Lesson | null;
    open: boolean;
    progress: LearningProgress;
    /** Должен быть стабильным (useCallback) — от него зависит подписка на Escape */
    onClose: () => void;
}
