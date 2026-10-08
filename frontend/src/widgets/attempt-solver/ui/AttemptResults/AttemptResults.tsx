import { ChevronDown, ClipboardList, Lightbulb } from 'lucide-react';
import { useState, type JSX } from 'react';
import { Link } from 'react-router';
import { formatAnswer } from '../../../../entities/exam-task';
import { HOMEWORK_LIST_ROUTE } from '../../../../entities/homework';
import { cn, formatDayMonth, formatLongDate, formatSpentTime, percent } from '../../../../shared/lib';
import { Button, MathText, ProgressRing } from '../../../../shared/ui';
import styles from './HomeworkResults.module.css';
import type { HomeworkResultsProps } from './HomeworkResults.props';


/** Результаты сданного ДЗ: доля верных, дата и время, сетка задач и ответы с разбором */
export const HomeworkResults = ({ homework, result, justFinished }: HomeworkResultsProps): JSX.Element => {
    const tasks = homework.tasks;
    const isCorrect = (i: number) => (result.points[i] ?? 0) > 0;
    const correct = tasks.filter((_, i) => isCorrect(i)).length;
    // Аккордеон: открыта одна строка
    const [open, setOpen] = useState<number | null>(null);

    return (
        <section className={styles.results}>
            <div className={cn('glass', styles.card)}>
                <div>
                    <p className={styles.kicker}>{justFinished ? 'Домашнее задание сдано' : `Сдано ${formatDayMonth(result.date)}`}</p>
                    <h2 className={styles.title}>Результаты</h2>
                </div>

                <div className={styles.score}>
                    <ProgressRing value={percent(correct, tasks.length)} label="решено верно" />
                    <div className={styles.legend}>
                        <div className={styles.legendItem}><span className={cn(styles.dot, styles.dotPrimary)} />Верно — {correct}</div>
                        <div className={styles.legendItem}><span className={styles.dot} />Неверно — {tasks.length - correct}</div>
                    </div>
                </div>

                <dl className={styles.facts}>
                    <div><dt>Сдано</dt><dd>{formatLongDate(result.date)}</dd></div>
                    <div><dt>Время</dt><dd>{formatSpentTime(result.seconds)}</dd></div>
                    <div className={styles.factsWide}>
                        <dt>Срок</dt>
                        <dd>до {formatDayMonth(homework.deadline)}, 23:59{result.late ? ' · сдано после срока' : ''}</dd>
                    </div>
                </dl>

                <div className={styles.cellsWrap}>
                    <p className={styles.cellsTitle}>По задачам</p>
                    <div className={styles.cells}>
                        {tasks.map((t, i) => (
                            <span
                                key={i}
                                className={cn(styles.cell, isCorrect(i) ? styles.full : styles.zero)}
                                title={`Задача ${i + 1} (№${t.number} ЕГЭ): ${isCorrect(i) ? 'верно' : 'неверно'}`}
                            >
                                <b>{i + 1}</b><small>№{t.number}</small>
                            </span>
                        ))}
                    </div>
                    <p className={styles.cellsLegend}>
                        <span><i className={styles.full} />верно</span>
                        <span><i className={styles.zero} />неверно или без ответа</span>
                    </p>
                </div>

                <div className={styles.actions}>
                    <Button as={Link} to={`${HOMEWORK_LIST_ROUTE}?tab=done`} size="m" radius={12}>
                        <ClipboardList size={18} />К домашним заданиям
                    </Button>
                </div>
            </div>

            <div className={cn('glass', styles.card)}>
                <div>
                    <h2 className={styles.cardTitle}>Ответы по задачам</h2>
                    <p className={styles.cardSub}>Нажмите на задачу, чтобы увидеть условие и решение.</p>
                </div>

                <div className={styles.review}>
                    {tasks.map((t, i) => {
                        // У заглушек сданных ДЗ ответов нет — показываем только верный
                        const given = result.answers?.[i];
                        const isOpen = open === i;
                        return (
                            <div key={i} className={cn(styles.row, isCorrect(i) ? styles.full : styles.zero)}>
                                <button
                                    type="button"
                                    className={styles.summary}
                                    aria-expanded={isOpen}
                                    onClick={() => setOpen(isOpen ? null : i)}
                                >
                                    <span className={styles.rowNum}>{i + 1}</span>
                                    <span className={styles.rowEge}>№{t.number}</span>
                                    <span className={styles.answers}>
                                        <span>
                                            <small>Ваш ответ</small>
                                            {given === undefined ? <em>—</em> : given.trim() ? given : <em>нет ответа</em>}
                                        </span>
                                        <span><small>Верный</small>{formatAnswer(t.answer)}</span>
                                    </span>
                                    <span className={styles.points}>{isCorrect(i) ? 1 : 0}/1</span>
                                    <ChevronDown size={16} className={cn(styles.chevron, { [styles.chevronOpen]: isOpen })} />
                                </button>

                                {isOpen && (
                                    <div className={styles.body}>
                                        <MathText className={styles.bodyText} text={t.text} />
                                        <div className={styles.solution}>
                                            <p className={styles.solutionTitle}><Lightbulb size={14} />Решение</p>
                                            <MathText className={styles.solutionText} text={t.solution} />
                                            <p className={styles.solutionAnswer}>Ответ: <b>{formatAnswer(t.answer)}</b></p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </section>
    );
};
