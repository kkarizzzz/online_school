import type { Lesson } from '../../../entities/curriculum';
import type { LessonModel } from '../../../entities/lesson';

/** Урок программы → карточка урока (NextLesson, UpcomingLessons) */
export const toLessonModel = (lesson: Lesson): LessonModel => ({
    id: lesson.id,
    title: lesson.name,
    moduleNumber: lesson.topic.order,
    moduleTopic: lesson.topic.title,
    lessonNumber: lesson.index,
    lessonTotal: lesson.topic.lessons.length,
    duration: lesson.minutes,
});
