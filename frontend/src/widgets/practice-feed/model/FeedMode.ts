import type { PracticeTopic } from '../../../entities/practice-task';

/** Откуда лента берёт задания */
export abstract class FeedMode {
    /** Тема для API; null — все темы */
    abstract readonly topicId: number | null;
    abstract readonly label: string;
    abstract readonly title: string;

    /** Параметры адреса, чтобы лента продолжилась после перезагрузки */
    abstract toSearchParams(): Record<string, string>;

    /** Режим из адреса страницы: ?mode=tornado или ?topic=ID */
    static fromSearchParams(params: URLSearchParams, topics: PracticeTopic[]): FeedMode | null {
        if (params.get('mode') === 'tornado') return new TornadoMode();
        const topic = topics.find((t) => t.id === Number(params.get('topic')));
        return topic ? new TopicMode(topic) : null;
    }
}

export class TopicMode extends FeedMode {
    readonly topic: PracticeTopic;
    readonly label = 'Тема';

    constructor(topic: PracticeTopic) {
        super();
        this.topic = topic;
    }

    get topicId(): number {
        return this.topic.id;
    }

    get title(): string {
        return this.topic.name;
    }

    toSearchParams(): Record<string, string> {
        return { topic: String(this.topic.id) };
    }
}

/** «Торнадо»: задачи по всем темам вперемешку */
export class TornadoMode extends FeedMode {
    readonly topicId = null;
    readonly label = 'Нарешка';
    readonly title = 'Торнадо · все темы';

    toSearchParams(): Record<string, string> {
        return { mode: 'tornado' };
    }
}
