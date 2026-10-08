import { ArrowDownWideNarrow, ArrowUpNarrowWide, ChevronDown, ListFilter } from 'lucide-react';
import { useMemo, type JSX } from 'react';
import { useSearchParams } from 'react-router';
import {
    VariantCard, useVariants, type Variant, type VariantKindFilter, type VariantSort, type VariantStatusFilter,
} from '../../../../entities/variant';
import { cn } from '../../../../shared/lib';
import { Container, Tabs } from '../../../../shared/ui';
import type { TabItem } from '../../../../shared/ui/Tabs/Tabs.props';
import { PageHeader } from '../../../../widgets/page-header';
import styles from './VariantsPage.module.css';

const KINDS: { id: VariantKindFilter; label: string }[] = [
    { id: 'all', label: 'Все' },
    { id: 'variant', label: 'Как на ЕГЭ' },
    { id: 'drill', label: 'Отработка' },
];

const STATUSES: { id: VariantStatusFilter; label: string }[] = [
    { id: 'all', label: 'Все' },
    { id: 'todo', label: 'Не решённые' },
    { id: 'done', label: 'Решённые' },
];

const SORTS: Record<VariantSort, { label: string; key: (v: Variant) => number; desc: string; asc: string }> = {
    date: { label: 'По дате', key: (v) => new Date(v.publishedAt).getTime(), desc: 'Сначала новые', asc: 'Сначала старые' },
    difficulty: { label: 'По сложности', key: (v) => v.difficulty ?? 0, desc: 'Сначала сложные', asc: 'Сначала простые' },
    popular: { label: 'По популярности', key: (v) => v.solvedStudents, desc: 'Сначала популярные', asc: 'Сначала редкие' },
};

const pick = <T extends string>(value: string | null, allowed: readonly T[], fallback: T): T =>
    allowed.includes(value as T) ? (value as T) : fallback;


/** Каталог вариантов и отработок. Фильтры и сортировка — в адресе: ?kind=drill&status=todo&sort=popular&order=asc */
export const VariantsPage = (): JSX.Element => {
    const { data: variants, isPending, isError } = useVariants();
    const [params, setParams] = useSearchParams();
    const kind = pick(params.get('kind'), KINDS.map((k) => k.id), 'all');
    const status = pick(params.get('status'), STATUSES.map((s) => s.id), 'all');
    const sort = pick(params.get('sort'), Object.keys(SORTS) as VariantSort[], 'date');
    const order = params.get('order') === 'asc' ? 'asc' : 'desc';

    const change = (key: string, value: string, fallback: string) => {
        const next = new URLSearchParams(params);
        if (value === fallback) next.delete(key);
        else next.set(key, value);
        setParams(next, { replace: true });
    };

    const list = useMemo(() => {
        const { key } = SORTS[sort];
        return (variants ?? [])
            .filter((v) => kind === 'all' || (kind === 'variant' ? v.isStandard : !v.isStandard))
            .filter((v) => status === 'all' || (status === 'done') === (v.lastAttempt !== null))
            .sort((a, b) => {
                const diff = key(a) - key(b);
                // При равенстве выше более новые
                return (order === 'asc' ? diff : -diff) || b.publishedAt.localeCompare(a.publishedAt);
            });
    }, [variants, kind, status, sort, order]);

    const kindTabs: TabItem[] = KINDS.map((k) => ({ id: k.id, label: k.label }));

    return (
        <Container variant='page'>
            <PageHeader />

            <div className={styles.toolbar}>
                <Tabs tabs={kindTabs} activeTab={kind} onChange={(id) => change('kind', id, 'all')} />

                <div className={styles.controls}>
                    <div className={styles.chips}>
                        {STATUSES.map((s) => (
                            <button
                                key={s.id}
                                type="button"
                                className={styles.chip}
                                aria-pressed={status === s.id}
                                onClick={() => change('status', s.id, 'all')}
                            >
                                {s.label}
                            </button>
                        ))}
                    </div>

                    <div className={styles.sort}>
                        <label className={styles.select}>
                            <ListFilter size={16} className={styles.selectIcon} />
                            <select aria-label="Сортировка" value={sort} onChange={(e) => change('sort', e.target.value, 'date')}>
                                {(Object.keys(SORTS) as VariantSort[]).map((id) => <option key={id} value={id}>{SORTS[id].label}</option>)}
                            </select>
                            <ChevronDown size={16} className={styles.selectChevron} />
                        </label>
                        <button
                            type="button"
                            className={styles.order}
                            onClick={() => change('order', order === 'desc' ? 'asc' : 'desc', 'desc')}
                        >
                            {order === 'desc' ? <ArrowDownWideNarrow size={16} /> : <ArrowUpNarrowWide size={16} />}
                            {SORTS[sort][order]}
                        </button>
                    </div>
                </div>
            </div>

            {isError && <p className={cn('glass', styles.empty)}>Не удалось загрузить каталог. Обновите страницу.</p>}
            {isPending && <p className={styles.loading}>Загружаем варианты…</p>}
            {variants && list.length === 0 && <p className={cn('glass', styles.empty)}>Таких вариантов нет.</p>}

            <div className={styles.grid}>
                {list.map((v) => <VariantCard key={v.id} variant={v} />)}
            </div>
        </Container>
    );
};
