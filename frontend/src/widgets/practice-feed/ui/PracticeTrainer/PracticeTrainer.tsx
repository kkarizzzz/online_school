import { useQueryClient } from '@tanstack/react-query';
import { CircleCheck, Flame, RotateCcw, Tornado } from 'lucide-react';
import { useEffect, useRef, useState, type JSX } from 'react';
import { useSearchParams } from 'react-router';
import { practiceKeys, practiceRepository, usePracticeTopics } from '../../../../entities/practice-task';
import { cn, parseApiError, useObservable } from '../../../../shared/lib';
import { Button, FeedBar } from '../../../../shared/ui';
import { FeedMode, TopicMode } from '../../model/FeedMode';
import { PracticeFeed } from '../../model/PracticeFeed';
import { PracticePicker } from '../PracticePicker/PracticePicker';
import { PracticeTaskCard } from '../PracticeTaskCard/PracticeTaskCard';
import styles from './PracticeTrainer.module.css';


/**
 * «Нарешка»: выбор темы → бесконечная лента заданий.
 * Режим и текущее задание живут в адресе (?topic=ID&task=ID или ?mode=tornado), чтобы лента пережила перезагрузку.
 */
export const PracticeTrainer = (): JSX.Element => {
    const topicsQuery = usePracticeTopics();
    const queryClient = useQueryClient();
    const [params, setParams] = useSearchParams();
    const [feed] = useState(() => new PracticeFeed(practiceRepository));
    useObservable(feed);

    const restored = useRef(false);
    const topics = topicsQuery.data;

    // Один раз после загрузки тем продолжаем ленту из адреса
    useEffect(() => {
        if (restored.current || !topics) return;
        restored.current = true;
        const mode = FeedMode.fromSearchParams(params, topics.topics);
        if (mode) feed.start(mode, Number(params.get('task')) || null);
    }, [topics, params, feed]);

    const { mode, task } = feed;
    useEffect(() => {
        if (!restored.current) return;
        const next: Record<string, string> = mode ? { ...mode.toSearchParams() } : {};
        if (mode && task) next.task = String(task.id);
        setParams(next, { replace: true });
    }, [mode, task, setParams]);

    const backToTopics = () => {
        feed.exit();
        queryClient.invalidateQueries({ queryKey: practiceKeys.topics });
        window.scrollTo({ top: 0 });
    };

    const pick = (picked: FeedMode) => {
        feed.start(picked);
        window.scrollTo({ top: 0 });
    };

    if (!mode) {
        if (topicsQuery.isPending) return <p className={styles.empty}>Загружаем темы…</p>;
        if (topicsQuery.isError) {
            return (
                <div className={cn('glass', styles.error)}>
                    <p><b>Не удалось загрузить темы.</b> {parseApiError(topicsQuery.error, 'Сервер нарешки недоступен.')}</p>
                    <Button variant="outline" size="s" onClick={() => topicsQuery.refetch()}><RotateCcw size={16} />Повторить</Button>
                </div>
            );
        }
        return <PracticePicker data={topicsQuery.data} onPick={pick} />;
    }

    return (
        <section className={styles.feed}>
            <FeedBar
                backLabel="Темы"
                onBack={backToTopics}
                modeIcon={mode instanceof TopicMode ? `№${mode.topic.taskNumber}` : <Tornado size={18} />}
                modeAccent={!(mode instanceof TopicMode)}
                modeLabel={mode.label}
                modeTitle={mode.title}
                stats={[
                    { icon: CircleCheck, label: 'Решено', value: feed.solved, title: 'Решено за эту сессию', bumpKey: feed.solved },
                    { icon: Flame, label: 'Серия', value: feed.streak, title: 'Верных ответов подряд', hot: true, bumpKey: feed.streak },
                ]}
            />

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
