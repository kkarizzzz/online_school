// Данные программы курса в том виде, в каком их отдаёт источник (сейчас — curriculum.data.ts, позже — API)

export interface OutlineNodeDto {
    t: string;
    c?: OutlineNodeDto[];
}

export interface LessonDto {
    id: string;          // x.y.z
    name: string;
    note: string;        // уточнение из скобок в плане
    outline: OutlineNodeDto[];
}

export interface TopicDto {
    id: string;          // x.y
    b: number;           // индекс ветки
    l: number;           // уровень 0–3
    name: string;
    tasks: number[];     // номера заданий ЕГЭ
    lessons: LessonDto[];
}

export interface LevelDto {
    name: string;
    desc: string;
    order: number[];     // порядок веток на уровне
}

export interface CurriculumDto {
    branches: string[];
    levels: LevelDto[];
    topics: TopicDto[];
}

/** Мини-конспект урока */
export interface LessonSummaryData {
    intro: string;
    formulas?: [label: string, formula: string][];
    points?: string[];
    steps?: boolean;     // points — это шаги
    tip?: { kind: 'tip' | 'warn'; text: string };
    example?: { q: string; a: string };
}

export type TopicStatus = 'done' | 'progress' | 'todo';

export interface ProgressCount {
    done: number;
    total: number;
}
