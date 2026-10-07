import type { LearningProgress, Topic, TopicStatus } from '../../../entities/curriculum';
import { Observable } from '../../../shared/lib';

export type RouteView = 'route' | 'map';
export type StatusFilter = 'all' | TopicStatus;

export interface BranchGroup {
    branch: number;
    topics: Topic[];
}

export interface LevelGroup {
    level: number;
    branches: BranchGroup[];
}

/**
 * Состояние страницы «Теория»: выбранный уровень, фильтр статуса, поиск, вид (маршрут / карта)
 * и раскрытые темы. Прогресс не хранит — получает его аргументом.
 */
export class TheoryRouteState extends Observable {
    level: number;
    status: StatusFilter = 'progress';
    query = '';
    view: RouteView = 'route';

    private readonly openTopics: Set<string>;

    constructor(progress: LearningProgress) {
        super();
        this.level = progress.currentLevel;
        this.openTopics = new Set(progress.nextLesson ? [progress.nextLesson.topic.id] : []);
    }

    isOpen(topic: Topic): boolean {
        return this.openTopics.has(topic.id);
    }

    toggleTopic(topic: Topic): void {
        if (this.openTopics.has(topic.id)) this.openTopics.delete(topic.id);
        else this.openTopics.add(topic.id);
        this.notify();
    }

    selectLevel(level: number): void {
        this.level = level;
        this.query = '';
        this.view = 'route';
        this.notify();
    }

    setStatus(status: StatusFilter): void {
        this.status = status;
        this.notify();
    }

    setView(view: RouteView): void {
        this.view = view;
        this.notify();
    }

    /** Поиск идёт по всей программе: статус сбрасывается, темы с подходящими уроками раскрываются */
    search(query: string, progress: LearningProgress): void {
        this.query = query.trim();
        if (this.query) {
            this.view = 'route';
            this.status = 'all';
            progress.curriculum.topics
                .filter((t) => t.lessons.some((l) => l.matches(this.query)))
                .forEach((t) => this.openTopics.add(t.id));
        }
        this.notify();
    }

    /** Переход с карты к теме в маршруте */
    goToTopic(topic: Topic): void {
        this.view = 'route';
        this.query = '';
        this.status = 'all';
        this.level = topic.level;
        this.openTopics.add(topic.id);
        this.notify();
    }

    /** Темы под текущие фильтры, сгруппированные по уровню и ветке в порядке маршрута */
    groups(progress: LearningProgress): LevelGroup[] {
        const { curriculum } = progress;
        const pool = curriculum.topics
            .filter((t) => (this.query ? t.matches(this.query) : t.level === this.level))
            .filter((t) => this.status === 'all' || progress.statusOf(t) === this.status);

        const levels = [...new Set(pool.map((t) => t.level))];
        return levels.map((level) => ({
            level,
            branches: curriculum.levels[level].order
                .map((branch) => ({ branch, topics: pool.filter((t) => t.level === level && t.branch === branch) }))
                .filter((g) => g.topics.length > 0),
        }));
    }

    countVisible(progress: LearningProgress): number {
        return this.groups(progress).reduce((sum, l) => sum + l.branches.reduce((s, b) => s + b.topics.length, 0), 0);
    }
}
