import type { Lesson } from './Lesson';
import { Topic } from './Topic';
import type { CurriculumDto, LevelDto } from './types';

/**
 * Программа курса: ветки × уровни → темы → уроки.
 * Порядок тем уже задан источником (уровень → ветка → номер темы).
 */
export class Curriculum {
    readonly branches: string[];
    readonly levels: LevelDto[];
    readonly topics: Topic[];
    readonly lessons: Lesson[];

    private readonly lessonIndex: Map<string, Lesson>;
    private readonly topicIndex: Map<string, Topic>;

    constructor(dto: CurriculumDto) {
        this.branches = dto.branches;
        this.levels = dto.levels;

        let seq = 0;
        this.topics = dto.topics.map((t, i) => {
            const topic = new Topic(t, i + 1, seq);
            seq += topic.lessons.length;
            return topic;
        });
        this.lessons = this.topics.flatMap((t) => t.lessons);

        this.lessonIndex = new Map(this.lessons.map((l) => [l.id, l]));
        this.topicIndex = new Map(this.topics.map((t) => [t.id, t]));
    }

    lesson(id: string): Lesson | undefined {
        return this.lessonIndex.get(id);
    }

    topic(id: string): Topic | undefined {
        return this.topicIndex.get(id);
    }

    /** Следующий урок по программе (или null, если этот последний) */
    lessonAfter(lesson: Lesson): Lesson | null {
        return this.lessons[lesson.seq + 1] ?? null;
    }

    topicsOf(level: number, branch?: number): Topic[] {
        return this.topics.filter((t) => t.level === level && (branch === undefined || t.branch === branch));
    }

    lessonsOfLevel(level: number): Lesson[] {
        return this.lessons.filter((l) => l.topic.level === level);
    }

    lessonsOfBranch(branch: number): Lesson[] {
        return this.lessons.filter((l) => l.topic.branch === branch);
    }
}
