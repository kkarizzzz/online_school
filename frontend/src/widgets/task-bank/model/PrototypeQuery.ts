import { BANK_LEVELS, type BankNumberTasks, type BankTask } from '../../../entities/bank-task';

export type StatusId = 'todo' | 'done';
export type SortId = 'date' | 'level' | 'solved';
export type SortOrder = 'asc' | 'desc';

export const STATUSES: Record<StatusId, { label: string; test: (solved: boolean) => boolean }> = {
    todo: { label: 'Не решённые', test: (solved) => !solved },
    done: { label: 'Решённые', test: (solved) => solved },
};

// key — значение для сравнения; desc/asc — подпись направления
export const SORTS: Record<SortId, { label: string; key: (t: BankTask) => string | number; desc: string; asc: string }> = {
    date: { label: 'По дате добавления', key: (t) => t.date, desc: 'Сначала новые', asc: 'Сначала старые' },
    level: { label: 'По сложности', key: (t) => BANK_LEVELS[t.level].rank, desc: 'Сначала сложные', asc: 'Сначала простые' },
    solved: { label: 'По числу решений', key: (t) => t.solvedBy, desc: 'Сначала популярные', asc: 'Сначала редкие' },
};

const DEFAULT_SORT: SortId = 'date';
const DEFAULT_ORDER: SortOrder = 'desc';

const isStatus = (v: string | null): v is StatusId => v !== null && v in STATUSES;
const isSort = (v: string | null): v is SortId => v !== null && v in SORTS;

/**
 * Фильтры и сортировка заданий одного номера. Живут в адресе:
 * ?topics=log,exp&status=todo&sort=level&order=asc. Пустой набор тем — все темы.
 */
export class PrototypeQuery {
    readonly topics: ReadonlySet<string>;
    readonly status: StatusId | null;
    readonly sort: SortId;
    readonly order: SortOrder;
    private readonly number: BankNumberTasks;

    constructor(number: BankNumberTasks, topics: Iterable<string>, status: StatusId | null, sort: SortId, order: SortOrder) {
        this.number = number;
        const known = new Set(number.topics.map((t) => t.id));
        const picked = new Set([...topics].filter((id) => known.has(id)));
        // Выбраны все по одной — то же, что «Все темы»
        this.topics = picked.size === known.size ? new Set() : picked;
        this.status = status;
        this.sort = sort;
        this.order = order;
    }

    static fromParams(number: BankNumberTasks, params: URLSearchParams): PrototypeQuery {
        const status = params.get('status');
        const sort = params.get('sort');
        const order = params.get('order');
        return new PrototypeQuery(
            number,
            (params.get('topics') ?? '').split(',').filter(Boolean),
            isStatus(status) ? status : null,
            isSort(sort) ? sort : DEFAULT_SORT,
            order === 'asc' || order === 'desc' ? order : DEFAULT_ORDER,
        );
    }

    toParams(): Record<string, string> {
        const p: Record<string, string> = {};
        if (this.topics.size) p.topics = [...this.topics].join(',');
        if (this.status) p.status = this.status;
        if (this.sort !== DEFAULT_SORT) p.sort = this.sort;
        if (this.order !== DEFAULT_ORDER) p.order = this.order;
        return p;
    }

    get allTopics(): boolean {
        return this.topics.size === 0;
    }

    /** Переключить тему; null — «Все темы» */
    withTopic(id: string | null): PrototypeQuery {
        const next = new Set(this.topics);
        if (id === null) next.clear();
        else if (next.has(id)) next.delete(id);
        else next.add(id);
        return new PrototypeQuery(this.number, next, this.status, this.sort, this.order);
    }

    /** Повторный выбор того же статуса снимает его */
    withStatus(status: StatusId | null): PrototypeQuery {
        return new PrototypeQuery(this.number, this.topics, this.status === status ? null : status, this.sort, this.order);
    }

    withSort(sort: SortId): PrototypeQuery {
        return new PrototypeQuery(this.number, this.topics, this.status, sort, this.order);
    }

    withToggledOrder(): PrototypeQuery {
        return new PrototypeQuery(this.number, this.topics, this.status, this.sort, this.order === 'desc' ? 'asc' : 'desc');
    }

    get orderLabel(): string {
        return SORTS[this.sort][this.order];
    }

    inTopics(task: BankTask): boolean {
        return this.allTopics || this.topics.has(task.topic);
    }

    /** Задания по фильтрам, отсортированные; при равенстве — новые выше, затем по порядку в теме */
    apply(tasks: BankTask[], solved: ReadonlySet<number>): BankTask[] {
        const { key } = SORTS[this.sort];
        return tasks
            .filter((t) => this.inTopics(t) && (!this.status || STATUSES[this.status].test(solved.has(t.id))))
            .sort((a, b) => {
                const ka = key(a), kb = key(b);
                const diff = ka < kb ? -1 : ka > kb ? 1 : 0;
                return (this.order === 'asc' ? diff : -diff) || b.date.localeCompare(a.date) || a.index - b.index;
            });
    }
}
