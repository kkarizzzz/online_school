import type { LessonStepDto, PracticeStepDto, VideoStepDto } from '../../../entities/lesson';
import { LessonItem } from './LessonItem';

/** Шаг урока: ролик с вопросами или блок практики */
export abstract class LessonStep {
    abstract readonly kind: LessonStepDto['kind'];
    readonly title: string;
    readonly items: LessonItem[];

    constructor(title: string, items: LessonItem[]) {
        this.title = title;
        this.items = items;
    }

    /** «вопрос / вопроса / вопросов» или «задача / задачи / задач» */
    abstract get itemWords(): [one: string, few: string, many: string];

    static from(dto: LessonStepDto): LessonStep {
        return dto.kind === 'video' ? new VideoStep(dto) : new PracticeStep(dto);
    }
}

export class VideoStep extends LessonStep {
    readonly kind = 'video';
    readonly src: string;
    readonly poster: string;
    readonly duration: number;
    readonly transcript: string[];

    constructor(dto: VideoStepDto) {
        super(dto.title, dto.questions.map(LessonItem.from));
        this.src = dto.src;
        this.poster = dto.poster;
        this.duration = dto.duration;
        this.transcript = dto.transcript;
    }

    get itemWords(): [string, string, string] {
        return ['вопрос', 'вопроса', 'вопросов'];
    }
}

export class PracticeStep extends LessonStep {
    readonly kind = 'practice';
    readonly intro: string;

    constructor(dto: PracticeStepDto) {
        super(dto.title, dto.tasks.map(LessonItem.from));
        this.intro = dto.intro;
    }

    get itemWords(): [string, string, string] {
        return ['задача', 'задачи', 'задач'];
    }
}
