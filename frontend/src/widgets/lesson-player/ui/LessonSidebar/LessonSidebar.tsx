import { Check, Lock, RotateCcw } from 'lucide-react';
import type { JSX } from 'react';
import { cn, formatDuration, plural } from '../../../../shared/lib';
import { ProgressBar } from '../../../../shared/ui';
import { stepIcon } from '../../lib/stepIcon';
import { VideoStep } from '../../model/LessonStep';
import styles from './LessonSidebar.module.css';
import type { LessonSidebarProps } from './LessonSidebar.props';


/** Боковая колонка урока: план шагов и текущий результат */
export const LessonSidebar = ({ session, onGo, className, ...props }: LessonSidebarProps): JSX.Element => {
    const stats = session.stats();
    const scoreRows = [
        { label: 'Ролики просмотрены', value: stats.videosWatched, total: session.videos.length },
        { label: 'Вопросы с первой попытки', value: stats.questionsFirstTry, total: stats.questions },
        { label: 'Задачи решены', value: stats.tasksSolved, total: stats.tasks },
    ];

    return (
        <aside className={cn(styles.side, className)} {...props}>
            <section className={cn('glass', styles.card)} aria-labelledby="lesson-plan-title">
                <h2 className={styles.cardTitle} id="lesson-plan-title">План урока</h2>
                <ol className={styles.plan}>
                    {session.steps.map((step, si) => {
                        const { done, total } = session.stepCounts(si);
                        const isDone = done === total;
                        const reachable = session.isReachable(si);
                        const Icon = isDone ? Check : stepIcon(step);
                        const count = `${done}/${total} ${plural(total, ...step.itemWords)}`;
                        const sub = step instanceof VideoStep ? `${formatDuration(step.duration)} · ${count}` : count;

                        return (
                            <li key={si}>
                                <button
                                    type="button"
                                    className={cn(styles.item, {
                                        [styles.itemDone]: isDone,
                                        [styles.itemCurrent]: si === session.current,
                                        [styles.itemPractice]: step.kind === 'practice',
                                    })}
                                    disabled={!reachable}
                                    onClick={() => onGo(si)}
                                >
                                    <span className={styles.icon}><Icon size={16} /></span>
                                    <span className={styles.text}>
                                        <span className={styles.title}>{step.title}</span>
                                        <span className={styles.sub}>{sub}</span>
                                    </span>
                                    {!reachable && <Lock size={15} className={styles.lock} />}
                                </button>
                            </li>
                        );
                    })}
                </ol>
            </section>

            <section className={cn('glass', styles.card)} aria-labelledby="lesson-score-title">
                <h2 className={styles.cardTitle} id="lesson-score-title">Результат</h2>
                <div className={styles.score}>
                    {scoreRows.map((row) => (
                        <div key={row.label} className={styles.scoreRow}>
                            <span className={styles.scoreLabel}>{row.label}</span>
                            <span className={styles.scoreNum}>{row.value}/{row.total}</span>
                            <ProgressBar className={styles.scoreBar} value={row.value} max={row.total} />
                        </div>
                    ))}
                </div>
                <button type="button" className={styles.reset} onClick={() => session.reset()}>
                    <RotateCcw size={14} />Пройти урок заново
                </button>
            </section>
        </aside>
    );
};
