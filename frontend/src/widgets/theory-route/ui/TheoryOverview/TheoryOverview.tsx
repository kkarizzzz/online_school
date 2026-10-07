import { Trophy } from 'lucide-react';
import type { JSX } from 'react';
import { NextLesson } from '../../../../entities/lesson';
import { cn, pluralize } from '../../../../shared/lib';
import { ProgressBar, ProgressRing } from '../../../../shared/ui';
import { toLessonModel } from '../../lib/toLessonModel';
import styles from './TheoryOverview.module.css';
import type { TheoryOverviewProps } from './TheoryOverview.props';


/** Верхний ряд теории: следующий урок и прогресс по уровням */
export const TheoryOverview = ({ progress, onSelectLevel }: TheoryOverviewProps): JSX.Element => {
    const { curriculum, nextLesson } = progress;
    const topics = progress.countTopics(curriculum.topics);

    return (
        <div className={styles.top}>
            {nextLesson ? (
                <NextLesson lesson={toLessonModel(nextLesson)} />
            ) : (
                <div className={cn('glass', styles.finished)}>
                    <Trophy size={28} />
                    <h2>Все {pluralize(curriculum.topics.length, 'тема', 'темы', 'тем')} закрыты — время для вариантов</h2>
                    <p>{pluralize(curriculum.lessons.length, 'урок', 'урока', 'уроков')} позади</p>
                </div>
            )}

            <section className={cn('glass', styles.card)} aria-labelledby="theory-progress-title">
                <div className={styles.head}>
                    <div>
                        <h2 className={styles.title} id="theory-progress-title">Пройдено</h2>
                        <p className={styles.muted}>
                            {topics.done} из {topics.total} тем &middot; {progress.completedCount} из {curriculum.lessons.length} уроков
                        </p>
                    </div>
                    <ProgressRing value={progress.percent} size={76} stroke={6} compact />
                </div>

                <ul className={styles.levels}>
                    {curriculum.levels.map((level, i) => {
                        const { done, total } = progress.countLessons(curriculum.lessonsOfLevel(i));
                        return (
                            <li key={level.name}>
                                <button type="button" className={styles.level} onClick={() => onSelectLevel(i)}>
                                    <span className={styles.levelName}>
                                        {i}. {level.name} <span>&middot; {level.desc.split(',')[0]}</span>
                                    </span>
                                    <span className={styles.levelCount}>{done}/{total}</span>
                                    <ProgressBar className={styles.levelBar} value={done} max={total} tone={done === total ? 'done' : 'primary'} />
                                </button>
                            </li>
                        );
                    })}
                </ul>
            </section>
        </div>
    );
};
