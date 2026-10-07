import { Lesson } from './Lesson';
import type { TopicDto } from './types';

/** Тема программы (x.y) — модуль из нескольких уроков */
export class Topic {
    readonly id: string;
    readonly name: string;
    readonly branch: number;
    readonly level: number;
    /** Номера заданий ЕГЭ, к которым готовит тема */
    readonly examTasks: number[];
    /** Порядковый номер в маршруте, с 1 */
    readonly order: number;
    readonly lessons: Lesson[];

    constructor(dto: TopicDto, order: number, firstSeq: number) {
        this.id = dto.id;
        this.name = dto.name;
        this.branch = dto.b;
        this.level = dto.l;
        this.examTasks = dto.tasks;
        this.order = order;
        this.lessons = dto.lessons.map((l, i) => new Lesson(l, this, i + 1, firstSeq + i));
    }

    get title(): string {
        return `${this.id}. ${this.name}`;
    }

    /** Совпадение с поиском — по названию темы или любого её урока */
    matches(query: string): boolean {
        if (!query) return true;
        const q = query.toLowerCase();
        return `${this.id} ${this.name}`.toLowerCase().includes(q) || this.lessons.some((l) => l.matches(q));
    }
}
