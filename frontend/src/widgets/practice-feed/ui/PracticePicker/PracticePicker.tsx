import { ArrowUpRight, CircleCheck, History, Layers, Tornado } from 'lucide-react';
import type { JSX, ReactNode } from 'react';
import { cn, pluralize } from '../../../../shared/lib';
import { TopicMode, TornadoMode } from '../../model/FeedMode';
import styles from './PracticePicker.module.css';
import type { PracticePickerProps } from './PracticePicker.props';


/** Экран выбора: продолжить последнюю тему, «Торнадо» или любая тема */
export const PracticePicker = ({ data, onPick }: PracticePickerProps): JSX.Element => {
    const last = data.topics.find((t) => t.id === data.lastTopicId);

    return (
        <section className={styles.picker}>
            <div className={cn(styles.hero, { [styles.two]: !!last })}>
                {last && (
                    <HeroCard
                        icon={<History size={24} />}
                        eyebrow={`Продолжить · №${last.taskNumber}`}
                        title={last.name}
                        description={`Вы остановились на этой теме. ${last.subtopics.join(', ')}`}
                        onClick={() => onPick(new TopicMode(last))}
                    />
                )}
                <HeroCard
                    accent
                    icon={<Tornado size={24} />}
                    eyebrow="Все темы"
                    title="Нарешка «Торнадо»"
                    description="Задачи по всем темам вперемешку — как на экзамене, где не знаешь, что попадётся следующим."
                    onClick={() => onPick(new TornadoMode())}
                />
            </div>

            <h2 className={styles.sectionTitle}>Выберите тему</h2>
            <div className={styles.grid}>
                {data.topics.map((topic) => {
                    const isLast = topic.id === data.lastTopicId;
                    return (
                        <button
                            key={topic.id}
                            type="button"
                            className={cn(styles.topic, { [styles.topicLast]: isLast })}
                            onClick={() => onPick(new TopicMode(topic))}
                        >
                            <span className={styles.badge}>№{topic.taskNumber}</span>
                            <span className={styles.info}>
                                <span className={styles.name}>{topic.name}</span>
                                <span className={styles.subs}>{topic.subtopics.join(' · ')}</span>
                                <span className={styles.foot}>
                                    <span><Layers size={14} />{pluralize(topic.taskCount, 'задание', 'задания', 'заданий')}</span>
                                    {topic.solvedCount > 0 && (
                                        <span className={styles.solved}><CircleCheck size={14} />решено {topic.solvedCount}</span>
                                    )}
                                    {isLast && <span className={styles.chipLast}>Последняя тема</span>}
                                </span>
                            </span>
                        </button>
                    );
                })}
            </div>
        </section>
    );
};


interface HeroCardProps {
    icon: ReactNode;
    eyebrow: string;
    title: string;
    description: string;
    accent?: boolean;
    onClick: () => void;
}

const HeroCard = ({ icon, eyebrow, title, description, accent, onClick }: HeroCardProps): JSX.Element => (
    <button type="button" className={cn(styles.card, { [styles.accent]: accent })} onClick={onClick}>
        <span className={styles.glow} />
        <span className={styles.cardHead}>
            <span className={styles.cardIcon}>{icon}</span>
            <span className={styles.cardArrow}><ArrowUpRight size={22} /></span>
        </span>
        <span>
            <span className={styles.cardEyebrow}>{eyebrow}</span>
            <span className={styles.cardTitle}>{title}</span>
            <span className={styles.cardDesc}>{description}</span>
        </span>
    </button>
);
