import { Check, ChevronDown, Circle, CircleCheck, CirclePlay, Play, Sparkles } from 'lucide-react';
import type { CSSProperties, JSX } from 'react';
import { cn, pluralize } from '../../../../shared/lib';
import { ProgressBar } from '../../../../shared/ui';
import { Highlight } from '../Highlight/Highlight';
import styles from './TopicItem.module.css';
import type { TopicItemProps } from './TopicItem.props';


/** Шаг маршрута: тема с прогрессом, по клику раскрывает список уроков */
export const TopicItem = ({ topic, progress, state, onOpenLesson }: TopicItemProps): JSX.Element => {
    const status = progress.statusOf(topic);
    const done = progress.doneIn(topic);
    const total = topic.lessons.length;
    const isNext = progress.isNextTopic(topic);
    const isOpen = state.isOpen(topic);
    const query = state.query;
    const topicsTotal = progress.curriculum.topics.length;

    return (
        <li
            id={`topic-${topic.id}`}
            className={cn(styles.topic, styles[status], { [styles.next]: isNext, [styles.open]: isOpen })}
            style={{ '--p': `${(done / total) * 100}%` } as CSSProperties}
        >
            <button type="button" className={styles.row} aria-expanded={isOpen} onClick={() => state.toggleTopic(topic)}>
                <span className={styles.step} aria-hidden="true">
                    {status === 'done' ? <Check size={18} /> : isNext ? <Play size={18} /> : String(topic.order).padStart(2, '0')}
                </span>

                <span className={styles.main}>
                    <span className={styles.title}>
                        <span className={styles.id}>{topic.id}</span>
                        <Highlight text={topic.name} query={query} />
                    </span>
                    <span className={styles.meta}>
                        {isNext && <span className={cn(styles.pill, styles.pillNext)}><Sparkles size={12} />Сейчас</span>}
                        {!isNext && status === 'done' && <span className={cn(styles.pill, styles.pillDone)}>Завершена</span>}
                        <span>Тема {topic.order} из {topicsTotal}</span>
                        <span>{pluralize(total, 'урок', 'урока', 'уроков')}</span>
                        {topic.examTasks.map((n) => <span key={n} className={styles.tag}>№{n}</span>)}
                    </span>
                </span>

                <span className={styles.prog}>
                    <ProgressBar className={styles.bar} value={done} max={total} tone={status === 'done' ? 'done' : 'primary'} />
                    <span className={styles.num}>{done}/{total}</span>
                </span>

                <ChevronDown size={20} className={styles.chev} />
            </button>

            {isOpen && (
                <ul className={styles.lessons}>
                    {topic.lessons.map((lesson) => {
                        const ok = progress.isDone(lesson);
                        const next = progress.isNext(lesson);
                        const hit = !!query && lesson.matches(query);
                        const Icon = ok ? CircleCheck : next ? CirclePlay : Circle;
                        return (
                            <li key={lesson.id}>
                                <button
                                    type="button"
                                    className={cn(styles.lesson, { [styles.lessonDone]: ok, [styles.lessonNext]: next })}
                                    onClick={() => onOpenLesson(lesson)}
                                >
                                    <Icon size={20} className={styles.lessonIcon} />
                                    <span className={styles.lessonName}>
                                        <span className={styles.lessonId}>{lesson.id}</span>
                                        <Highlight text={lesson.name} query={query} />
                                        {lesson.note && (
                                            <span className={styles.lessonNote}>
                                                <Highlight text={lesson.note} query={hit ? query : ''} />
                                            </span>
                                        )}
                                    </span>
                                    <span className={styles.lessonSide}>
                                        {ok ? 'пройден' : next ? 'следующий →' : `${lesson.minutes} мин`}
                                    </span>
                                </button>
                            </li>
                        );
                    })}
                </ul>
            )}
        </li>
    );
};
