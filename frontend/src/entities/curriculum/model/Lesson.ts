import type { Topic } from './Topic';
import type { LessonDto, OutlineNodeDto } from './types';

const countLeaves = (nodes: OutlineNodeDto[]): number =>
    nodes.reduce((sum, n) => sum + (n.c ? countLeaves(n.c) : 1), 0);

/** Урок программы (подтема x.y.z) */
export class Lesson {
    readonly id: string;
    readonly name: string;
    readonly note: string;
    readonly outline: OutlineNodeDto[];
    readonly topic: Topic;
    /** Номер урока внутри темы, с 1 */
    readonly index: number;
    /** Позиция во всей программе, с 0 */
    readonly seq: number;
    /** Оценка длительности по объёму плана урока */
    readonly minutes: number;

    constructor(dto: LessonDto, topic: Topic, index: number, seq: number) {
        this.id = dto.id;
        this.name = dto.name;
        this.note = dto.note;
        this.outline = dto.outline;
        this.topic = topic;
        this.index = index;
        this.seq = seq;
        this.minutes = 12 + 3 * Math.min(countLeaves(dto.outline), 8);
    }

    matches(query: string): boolean {
        return `${this.name} ${this.note}`.toLowerCase().includes(query.toLowerCase());
    }
}
