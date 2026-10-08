import {
    ArrowDownWideNarrow, ArrowLeft, ArrowUpNarrowWide, ChevronDown, ChevronLeft, ChevronRight,
    CircleCheck, CircleDashed, ListFilter, SearchX, type LucideIcon,
} from 'lucide-react';
import { useMemo, useState, type JSX, type ReactNode } from 'react';
import { Link, useSearchParams } from 'react-router';
import {
    BANK_PART_LABEL, BANK_ROUTE, BankTaskCard, bankNumberRoute, useSolvedTasks, useToggleSolved, type BankTask,
} from '../../../../entities/bank-task';
import { cn, pluralize } from '../../../../shared/lib';
import { Button } from '../../../../shared/ui';
import { PrototypeQuery, SORTS, STATUSES, type SortId, type StatusId } from '../../model/PrototypeQuery';
import styles from './PrototypeTasks.module.css';
import type { PrototypeTasksProps } from './PrototypeTasks.props';

const PAGE_SIZE = 12;
const NO_SOLVED: ReadonlySet<string> = new Set();
const STATUS_ICONS: Record<StatusId, LucideIcon> = { todo: CircleDashed, done: CircleCheck };
const tasksLabel = (n: number) => pluralize(n, 'задание', 'задания', 'заданий');


/**
 * Задания номера: темы — чипы с множественным выбором, статус «Не решённые / Решённые»,
 * сортировка по дате, сложности или числу решений. Всё состояние — в адресе.
 */
export const PrototypeTasks = ({ number, numbers }: PrototypeTasksProps): JSX.Element => {
    const [params, setParams] = useSearchParams();
    const query = useMemo(() => PrototypeQuery.fromParams(number, params), [number, params]);
    const { data: solved = NO_SOLVED } = useSolvedTasks();
    const { mutate: toggleSolved } = useToggleSolved();
    const [shown, setShown] = useState(PAGE_SIZE);
    // Отметка «решено» не убирает карточку из списка сразу, чтобы список не прыгал:
    // фильтр по статусу смотрит на отметки, какими они были до изменения, — до следующей смены фильтров
    const [frozen, setFrozen] = useState<ReadonlySet<string> | null>(null);

    const allTasks = useMemo(() => number.topics.flatMap((t) => t.tasks), [number]);
    const topicIndex = useMemo(() => new Map(number.topics.map((t, i) => [t.id, i + 1])), [number]);
    const topicName = useMemo(() => new Map(number.topics.map((t) => [t.id, t.name])), [number]);

    const list = query.apply(allTasks, frozen ?? solved);
    const page = list.slice(0, shown);
    const rest = list.length - page.length;
    // Всего в выбранных темах — без учёта статуса, чтобы не выдавать число решённых
    const total = allTasks.filter((t) => query.inTopics(t)).length;
    const allDone = list.length === 0 && query.status === 'todo' && total > 0;

    const change = (next: PrototypeQuery) => {
        setFrozen(null);
        setShown(PAGE_SIZE);
        setParams(next.toParams(), { replace: true });
    };

    const toggle = (task: BankTask) => {
        if (!frozen) setFrozen(solved);
        toggleSolved({ taskId: task.id, solved: !solved.has(task.id) });
    };

    const i = numbers.indexOf(number);
    const prev = numbers[i - 1];
    const next = numbers[i + 1];
    const codeOf = (t: BankTask) => `${number.n}.${topicIndex.get(t.topic)}.${String(t.index).padStart(2, '0')}`;

    return (
        <div className={styles.page}>
            <div className={styles.crumbs}>
                <Link className={styles.back} to={`${BANK_ROUTE}?n=${number.n}`}>
                    <ArrowLeft size={17} />Банк заданий
                </Link>
                <div className={styles.switch}>
                    <NumberLink to={prev && bankNumberRoute(prev.n)} title={prev && `№${prev.n} · ${prev.title}`} label="Предыдущий номер">
                        <ChevronLeft size={20} />
                    </NumberLink>
                    <NumberLink to={next && bankNumberRoute(next.n)} title={next && `№${next.n} · ${next.title}`} label="Следующий номер">
                        <ChevronRight size={20} />
                    </NumberLink>
                </div>
            </div>

            <div>
                <p className={styles.eyebrow}>Задание №{number.n} · {BANK_PART_LABEL[number.part]}</p>
                <h1 className={styles.title}>{number.title}</h1>
            </div>

            <div className={cn('glass', styles.filters)}>
                <div className={styles.filterRow}>
                    <span className={styles.filterLabel}>Темы</span>
                    <div className={styles.chips}>
                        <Chip pressed={query.allTopics} onClick={() => change(query.withTopic(null))}>
                            Все темы <span className={styles.chipCount}>{allTasks.length}</span>
                        </Chip>
                        {number.topics.map((t) => (
                            <Chip key={t.id} pressed={query.topics.has(t.id)} onClick={() => change(query.withTopic(t.id))}>
                                {t.name} <span className={styles.chipCount}>{t.tasks.length}</span>
                            </Chip>
                        ))}
                    </div>
                </div>
                <div className={styles.filterRow}>
                    <span className={styles.filterLabel}>Статус</span>
                    <div className={styles.chips}>
                        <Chip pressed={!query.status} onClick={() => change(query.withStatus(null))}>Все</Chip>
                        {(Object.keys(STATUSES) as StatusId[]).map((id) => {
                            const Icon = STATUS_ICONS[id];
                            return (
                                <Chip key={id} pressed={query.status === id} onClick={() => change(query.withStatus(id))}>
                                    <Icon size={14} />{STATUSES[id].label}
                                </Chip>
                            );
                        })}
                    </div>
                </div>
            </div>

            <div className={styles.listHead}>
                <div className={styles.sort}>
                    <label className={styles.select}>
                        <ListFilter size={16} className={styles.selectIcon} />
                        <select
                            aria-label="Сортировка"
                            value={query.sort}
                            onChange={(e) => change(query.withSort(e.target.value as SortId))}
                        >
                            {(Object.keys(SORTS) as SortId[]).map((id) => <option key={id} value={id}>{SORTS[id].label}</option>)}
                        </select>
                        <ChevronDown size={16} className={styles.selectChevron} />
                    </label>
                    <button
                        type="button"
                        className={styles.order}
                        aria-label={`Порядок: ${query.orderLabel.toLowerCase()}`}
                        onClick={() => change(query.withToggledOrder())}
                    >
                        {query.order === 'desc' ? <ArrowDownWideNarrow size={16} /> : <ArrowUpNarrowWide size={16} />}
                        <span className={styles.orderLabel}>{query.orderLabel}</span>
                    </button>
                </div>
                <p className={styles.found}>{tasksLabel(total)}</p>
            </div>

            {list.length > 0 ? (
                <ul className={styles.list}>
                    {page.map((t) => (
                        <BankTaskCard
                            key={t.id}
                            task={t}
                            code={codeOf(t)}
                            topicName={topicName.get(t.topic) ?? ''}
                            solved={solved.has(t.id)}
                            onToggleSolved={() => toggle(t)}
                        />
                    ))}
                </ul>
            ) : (
                <div className={cn('glass', styles.empty)}>
                    {allDone ? <CircleCheck size={32} /> : <SearchX size={32} />}
                    <p className={styles.emptyTitle}>{allDone ? 'Все задания решены' : 'Таких заданий нет'}</p>
                    <p className={styles.emptyText}>
                        {allDone ? 'В выбранных темах не осталось нерешённых заданий.' : 'Попробуйте выбрать другие темы или статус.'}
                    </p>
                    <Button variant="outline" size="s" radius={12} onClick={() => change(query.withTopic(null).withStatus(null))}>
                        Сбросить фильтры
                    </Button>
                </div>
            )}

            {rest > 0 && (
                <Button variant="outline" size="m" radius={12} className={styles.more} onClick={() => setShown(shown + PAGE_SIZE)}>
                    Показать ещё {Math.min(rest, PAGE_SIZE)} из {rest}
                </Button>
            )}
        </div>
    );
};


const Chip = ({ pressed, onClick, children }: { pressed: boolean; onClick: () => void; children: ReactNode }): JSX.Element => (
    <button type="button" className={styles.chip} aria-pressed={pressed} onClick={onClick}>{children}</button>
);


interface NumberLinkProps {
    to?: string;
    title?: string;
    label: string;
    children: ReactNode;
}

/** Стрелка к соседнему номеру; у первого и последнего — неактивная */
const NumberLink = ({ to, title, label, children }: NumberLinkProps): JSX.Element =>
    to ? (
        <Link className={styles.arrow} to={to} title={title} aria-label={label}>{children}</Link>
    ) : (
        <span className={cn(styles.arrow, styles.arrowDisabled)} aria-hidden="true">{children}</span>
    );
