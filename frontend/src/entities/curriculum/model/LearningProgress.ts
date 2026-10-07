import type { Curriculum } from './Curriculum';
import type { Lesson } from './Lesson';
import type { Topic } from './Topic';
import type { ProgressCount, TopicStatus } from './types';

/**
 * Прогресс ученика по программе. Неизменяемый: после прохождения урока
 * создаётся новый объект, поэтому его удобно класть в кэш react-query.
 */
export class LearningProgress {
    readonly curriculum: Curriculum;
    readonly nextLesson: Lesson | null;

    private readonly done: ReadonlySet<string>;

    constructor(curriculum: Curriculum, completedLessonIds: Iterable<string>) {
        this.curriculum = curriculum;
        this.done = new Set(completedLessonIds);
        this.nextLesson = curriculum.lessons.find((l) => !this.done.has(l.id)) ?? null;
    }

    get completedCount(): number {
        return this.curriculum.lessons.filter((l) => this.done.has(l.id)).length;
    }

    get percent(): number {
        return Math.round((this.completedCount / this.curriculum.lessons.length) * 100);
    }

    get isFinished(): boolean {
        return this.nextLesson === null;
    }

    /** Уровень, на котором ученик сейчас находится */
    get currentLevel(): number {
        return (this.nextLesson ?? this.curriculum.lessons.at(-1))?.topic.level ?? 0;
    }

    isDone(lesson: Lesson): boolean {
        return this.done.has(lesson.id);
    }

    isNext(lesson: Lesson): boolean {
        return this.nextLesson === lesson;
    }

    isNextTopic(topic: Topic): boolean {
        return this.nextLesson?.topic === topic;
    }

    doneIn(topic: Topic): number {
        return topic.lessons.filter((l) => this.done.has(l.id)).length;
    }

    /** Тема со следующим уроком считается «в процессе», даже если в ней ещё ничего не пройдено */
    statusOf(topic: Topic): TopicStatus {
        const done = this.doneIn(topic);
        if (done === topic.lessons.length) return 'done';
        return done || this.isNextTopic(topic) ? 'progress' : 'todo';
    }

    countLessons(lessons: Lesson[]): ProgressCount {
        return { done: lessons.filter((l) => this.done.has(l.id)).length, total: lessons.length };
    }

    countTopics(topics: Topic[]): ProgressCount {
        return { done: topics.filter((t) => this.statusOf(t) === 'done').length, total: topics.length };
    }

    withCompleted(lessonId: string): LearningProgress {
        return new LearningProgress(this.curriculum, [...this.done, lessonId]);
    }
}
