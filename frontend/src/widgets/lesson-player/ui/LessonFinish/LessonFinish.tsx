import { ArrowRight, ChevronRight, MapIcon } from 'lucide-react';
import type { JSX } from 'react';
import { Link } from 'react-router';
import { lessonRoute } from '../../../../entities/lesson';
import { cn, percent } from '../../../../shared/lib';
import { Button, HtmlText, ProgressRing } from '../../../../shared/ui';
import { stepIcon } from '../../lib/stepIcon';
import styles from './LessonFinish.module.css';
import type { LessonFinishProps } from './LessonFinish.props';

const verdict = (score: number): string => {
    if (score >= 85) return 'Отлично! Тема усвоена.';
    if (score >= 60) return 'Хорошо, но пару моментов стоит повторить.';
    return 'Урок пройден, но тему лучше закрепить.';
};


/** Итог урока: процент усвоения, что повторить и куда дальше */
export const LessonFinish = ({ session, nextLesson, onGo }: LessonFinishProps): JSX.Element => {
    const stats = session.stats();
    const score = session.score;
    const weak = session.weakItems();

    return (
        <article className={cn('glass', styles.card)}>
            <div className={styles.top}>
                <ProgressRing value={score} size={96} stroke={8} tone="done" compact />
                <div>
                    <p className={styles.kicker}>Урок пройден</p>
                    <h2 className={styles.title}>{verdict(score)}</h2>
                    <p className={styles.muted}>
                        Процент — доля вопросов, решённых с первой попытки, и задач, решённых без открытого решения.
                    </p>
                </div>
            </div>

            <div className={styles.stats}>
                <div><b>{stats.videosWatched}/{session.videos.length}</b><span>роликов просмотрено</span></div>
                <div><b>{percent(stats.questionsFirstTry, stats.questions)}%</b><span>вопросов с первой попытки</span></div>
                <div><b>{percent(stats.tasksSolved, stats.tasks)}%</b><span>задач решено самостоятельно</span></div>
            </div>

            {weak.length > 0 && (
                <div className={styles.weak}>
                    <h3 className={styles.weakTitle}>Стоит повторить</h3>
                    <ul>
                        {weak.map(({ stepIndex, step, item }) => {
                            const Icon = stepIcon(step);
                            return (
                                <li key={`${stepIndex}:${item.question}`}>
                                    <button type="button" className={styles.weakItem} onClick={() => onGo(stepIndex)}>
                                        <Icon size={16} />
                                        <span>{step.title}: <HtmlText html={item.question} /></span>
                                        <ChevronRight size={16} />
                                    </button>
                                </li>
                            );
                        })}
                    </ul>
                </div>
            )}

            <div className={styles.actions}>
                {nextLesson && (
                    <Button as={Link} to={lessonRoute(nextLesson.id)} size="m">
                        Следующий урок: {nextLesson.name}<ArrowRight size={18} />
                    </Button>
                )}
                <Button as={Link} to="/profile/learning/theory" variant="outline" size="m">
                    <MapIcon size={18} />К маршруту
                </Button>
            </div>
        </article>
    );
};
