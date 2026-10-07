import type { Lesson } from '../../../../entities/curriculum';
import type { LessonContent } from '../../../../entities/lesson';

export interface LessonPlayerProps {
    lesson: Lesson;
    lessonContent: LessonContent;
    nextLesson: Lesson | null;
    /** Ученик дошёл до итога — урок засчитывается пройденным */
    onFinish: () => void;
}
