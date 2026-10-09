import { useQueryClient } from '@tanstack/react-query';
import { CircleCheck, Flame, RotateCcw, Star, Tornado } from 'lucide-react';
import { useEffect, useRef, useState, type JSX } from 'react';
import { useSearchParams } from 'react-router';
import { practiceKeys, practiceRepository, usePracticeNumbers, type PracticeNumber } from '../../../../entities/practice-task';
import { cn, parseApiError, useObservable } from '../../../../shared/lib';
import { Button, FeedBar } from '../../../../shared/ui';
import { usePersonalStorage } from '../../model/PersonalStorage';
import { PracticeFeed } from '../../model/PracticeFeed';
import { numberOfTopic, numbersOfTopics, scopeFromParams, scopeTitle, scopeToParams, type PracticeScope } from '../../model/scope';
import { PracticeHome } from '../PracticeHome/PracticeHome';
import { PracticeTaskCard } from '../PracticeTaskCard/PracticeTaskCard';
import styles from './PracticeTrainer.module.css';


/**
 * «Нарешка»: главная («Торнадо», персональный режим, последние подборки) → бесконечная лента заданий.
 * Подборка и текущее задание живут в адресе (?mode=tornado&task=ID, ?mode=personal, ?topics=1,2&levels=2,3),
 * чтобы лента пережила перезагрузку.
 */
export const PracticeTrainer = (): JSX.Element => {
    const numbersQuery = usePracticeNumbers();
    const storage = usePersonalStorage();
    const queryClient = useQueryClient();
    const [params, setParams] = useSearchParams();
    const [feed] = useState(() => new PracticeFeed(practiceRepository));
    useObservable(feed);

    const restored = useRef(false);
    const numbers = numbersQuery.data;

    // Один раз после загрузки номеров продолжаем ленту из адреса
    useEffect(() => {
        if (restored.current || !numbers) return;
        restored.current = true;
        const scope = scopeFromParams(params, storage.scope());
        if (scope) start(scope, Number(params.get('task')) || null);
        // eslint-disable-next-line react-hooks/exhaustive-deps -- только при первой загрузке
    }, [numbers]);

    const { scope, task } = feed;
    useEffect(() => {
        if (!restored.current) return;
        const next: Record<string, string> = scope ? scopeToParams(scope) : {};
        if (scope && task) next.task = String(task.id);
        setParams(next, { replace: true });
    }, [scope, task, setParams]);

    function start(next: PracticeScope, taskId: number | null = null) {
        if (next.kind === 'personal') storage.pushRecent(next);
        feed.start(next, taskId);
        window.scrollTo({ top: 0 });
    }

    const backHome = () => {
        feed.exit();
        queryClient.invalidateQueries({ queryKey: practiceKeys.numbers });
        window.scrollTo({ top: 0 });
    };

    if (!scope) {
        if (numbersQuery.isPending) return <p className={styles.empty}>Загружаем номера…</p>;
        if (numbersQuery.isError) {
            return (
                <div className={cn('glass', styles.error)}>
                    <p><b>Не удалось загрузить номера.</b> {parseApiError(numbersQuery.error, 'Сервер нарешки недоступен.')}</p>
                    <Button variant="outline" size="s" onClick={() => numbersQuery.refetch()}><RotateCcw size={16} />Повторить</Button>
                </div>
            );
        }
        return <PracticeHome numbers={numbersQuery.data} storage={storage} onStart={(s) => start(s)} />;
    }

    const { label, title } = scopeTitle(scope, numbers ?? []);

    return (
        <section className={styles.feed}>
            <FeedBar
                backLabel="Нарешка"
                onBack={backHome}
                modeIcon={scope.kind === 'tornado' ? <Tornado size={18} /> : <Star size={18} />}
                modeAccent={scope.kind === 'tornado'}
                modeLabel={label}
                modeTitle={title}
                stats={[
                    { icon: CircleCheck, label: 'Решено', value: feed.solved, title: 'Решено за эту сессию', bumpKey: feed.solved },
                    { icon: Flame, label: 'Серия', value: feed.streak, title: 'Верных ответов подряд', hot: true, bumpKey: feed.streak },
                ]}
            />

            {/* В «Торнадо» выбора тем нет — только задание */}
            {scope.kind !== 'tornado' && numbers && (
                <ScopeChips scope={scope} numbers={numbers} currentTopicId={task?.topicId ?? null} onChange={(s) => start(s)} />
            )}

            {feed.error && (
                <div className={cn('glass', styles.error)}>
                    <p><b>Не удалось загрузить задание.</b> {feed.error}</p>
                    <Button variant="outline" size="s" onClick={() => feed.next()}><RotateCcw size={16} />Повторить</Button>
                </div>
            )}

            {task ? (
                <PracticeTaskCard key={task.id} feed={feed} task={task} />
            ) : (
                feed.loading && <p className={styles.empty}>Подбираем задание…</p>
            )}
        </section>
    );
};


interface ScopeChipsProps {
    scope: PracticeScope;
    numbers: PracticeNumber[];
    currentTopicId: number | null;
    onChange: (scope: PracticeScope) => void;
}

/**
 * Состав подборки. Несколько номеров — чипы номеров, клик оставляет только этот номер.
 * Один номер — чипы его подтем: их можно включать и выключать, хотя бы одна остаётся.
 * Сколько всего заданий, здесь не показываем.
 */
const ScopeChips = ({ scope, numbers, currentTopicId, onChange }: ScopeChipsProps): JSX.Element => {
    const inScope = numbersOfTopics(numbers, scope.topicIds);
    const current = currentTopicId ? numberOfTopic(numbers, currentTopicId) : undefined;
    const custom = (topicIds: number[]): PracticeScope => ({ kind: 'custom', topicIds, difficulties: scope.difficulties });

    if (inScope.length === 1) {
        const [n] = inScope;
        return (
            <div className={styles.chips} role="group" aria-label="Подтемы">
                {n.topics.map((t) => {
                    const on = scope.topicIds.includes(t.id);
                    return (
                        <button
                            key={t.id}
                            type="button"
                            className={cn(styles.chip, { [styles.chipCurrent]: t.id === currentTopicId })}
                            aria-pressed={on}
                            onClick={() => {
                                const next = on ? scope.topicIds.filter((id) => id !== t.id) : [...scope.topicIds, t.id];
                                if (next.length) onChange(custom(next));
                            }}
                        >
                            {t.name}
                        </button>
                    );
                })}
            </div>
        );
    }

    return (
        <div className={styles.chips} role="group" aria-label="Номера подборки">
            {inScope.map((n) => (
                <button
                    key={n.number}
                    type="button"
                    className={cn(styles.chip, { [styles.chipCurrent]: n === current })}
                    title={`Решать только №${n.number}`}
                    onClick={() => onChange(custom(n.topics.map((t) => t.id).filter((id) => scope.topicIds.includes(id))))}
                >
                    <b>№{n.number}</b> {n.title}
                </button>
            ))}
        </div>
    );
};
