import { ChevronDown, Lightbulb, MessageSquareText, PlayCircle } from 'lucide-react';
import { useState, type JSX } from 'react';
import type { AttemptItem } from '../../../../entities/attempt';
import { cn, formatLongDate, formatSpentTime, percent, pluralize } from '../../../../shared/lib';
import { MathText, Markdown, ProgressRing } from '../../../../shared/ui';
import styles from './AttemptResults.module.css';
import type { AttemptResultsProps } from './AttemptResults.props';

type Verdict = 'full' | 'part' | 'zero' | 'pending';

const verdictOf = (item: AttemptItem): Verdict => {
    const r = item.result;
    if (!r || r.needsReview) return 'pending';
    if ((r.score ?? 0) >= item.maxScore) return 'full';
    return (r.score ?? 0) > 0 ? 'part' : 'zero';
};

const VERDICT_LABEL: Record<Verdict, string> = {
    full: 'верно',
    part: 'частично',
    zero: 'неверно',
    pending: 'на проверке',
};


/** Результаты сданной попытки: баллы, дата и время, сетка заданий и ответы с разбором */
export const AttemptResults = ({ attempt, justFinished, actions }: AttemptResultsProps): JSX.Element => {
    const items = attempt.items;
    const checking = attempt.status === 'checking';
    const primary = attempt.primaryScore ?? 0;
    const max = attempt.maxScore ?? items.reduce((s, i) => s + i.maxScore, 0);
    const standard = attempt.set.isStandard && attempt.secondaryScore !== null;
    const counts = items.reduce<Record<Verdict, number>>(
        (acc, i) => ({ ...acc, [verdictOf(i)]: acc[verdictOf(i)] + 1 }),
        { full: 0, part: 0, zero: 0, pending: 0 },
    );
    // Аккордеон: открыта одна строка
    const [open, setOpen] = useState<number | null>(null);

    const kicker = justFinished
        ? (checking ? 'Сдано — вторую часть проверит преподаватель' : 'Сдано')
        : `Сдано ${attempt.submittedAt ? formatLongDate(attempt.submittedAt) : ''}`;

    return (
        <section className={styles.results}>
            <div className={cn('glass', styles.card)}>
                <div>
                    <p className={styles.kicker}>{kicker}</p>
                    <h2 className={styles.title}>Результаты</h2>
                </div>

                {checking && (
                    <p className={styles.notice}>
                        {pluralize(counts.pending, 'ответ ждёт', 'ответа ждут', 'ответов ждут')} проверки преподавателем.
                        Баллы ниже — предварительные: итог придёт уведомлением.
                    </p>
                )}

                <div className={styles.score}>
                    {standard ? (
                        <ProgressRing value={attempt.secondaryScore ?? 0} display={String(attempt.secondaryScore)} label="тестовых баллов" />
                    ) : (
                        <ProgressRing value={percent(primary, max)} label="баллов набрано" />
                    )}
                    <div className={styles.legend}>
                        <div className={styles.legendItem}>
                            <span className={cn(styles.dot, styles.dotPrimary)} />
                            {standard ? 'Первичный балл' : 'Баллы'} — {primary} из {max}
                        </div>
                        <div className={styles.legendItem}><span className={styles.dot} />Верно — {counts.full} из {items.length}</div>
                    </div>
                </div>

                <dl className={styles.facts}>
                    {attempt.submittedAt && <div><dt>Сдано</dt><dd>{formatLongDate(attempt.submittedAt)}</dd></div>}
                    <div><dt>Время</dt><dd>{formatSpentTime(attempt.timeSpentSec)}</dd></div>
                    {attempt.deadlineAt && (
                        <div className={styles.factsWide}>
                            <dt>Срок</dt>
                            <dd>до {formatLongDate(attempt.deadlineAt)}{attempt.isLate ? ' · сдано после срока' : ''}</dd>
                        </div>
                    )}
                    {attempt.set.kind !== 'homework' && (
                        <div className={styles.factsWide}>
                            <dt>Попытка</dt>
                            <dd>{attempt.isRated ? 'первая, зачётная' : 'повторная, не идёт в рейтинг'}</dd>
                        </div>
                    )}
                </dl>

                <div className={styles.cellsWrap}>
                    <p className={styles.cellsTitle}>По заданиям</p>
                    <div className={styles.cells}>
                        {items.map((item, i) => {
                            const verdict = verdictOf(item);
                            return (
                                <span
                                    key={item.position}
                                    className={cn(styles.cell, styles[verdict])}
                                    title={`Задание ${i + 1} (№${item.task.taskNumber} ЕГЭ): ${VERDICT_LABEL[verdict]}`}
                                >
                                    <b>{i + 1}</b><small>№{item.task.taskNumber}</small>
                                </span>
                            );
                        })}
                    </div>
                    <p className={styles.cellsLegend}>
                        <span><i className={styles.full} />верно</span>
                        {counts.part > 0 && <span><i className={styles.part} />частично</span>}
                        <span><i className={styles.zero} />неверно или без ответа</span>
                        {counts.pending > 0 && <span><i className={styles.pending} />на проверке</span>}
                    </p>
                </div>

                {actions && <div className={styles.actions}>{actions}</div>}
            </div>

            <div className={cn('glass', styles.card)}>
                <div>
                    <h2 className={styles.cardTitle}>Ответы по заданиям</h2>
                    <p className={styles.cardSub}>Нажмите на задание, чтобы увидеть условие и решение.</p>
                </div>

                <div className={styles.review}>
                    {items.map((item, i) => {
                        const verdict = verdictOf(item);
                        const r = item.result;
                        const isOpen = open === i;
                        const given = item.answer?.trim();
                        return (
                            <div key={item.position} className={cn(styles.row, styles[verdict])}>
                                <button
                                    type="button"
                                    className={styles.summary}
                                    aria-expanded={isOpen}
                                    onClick={() => setOpen(isOpen ? null : i)}
                                >
                                    <span className={styles.rowNum}>{i + 1}</span>
                                    <span className={styles.rowEge}>№{item.task.taskNumber}</span>
                                    <span className={styles.answers}>
                                        <span>
                                            <small>Ваш ответ</small>
                                            {given ? given : <em>{item.files.length ? 'фото решения' : 'нет ответа'}</em>}
                                        </span>
                                        {r && <span><small>Верный</small><MathText text={r.correctAnswer} /></span>}
                                    </span>
                                    <span className={styles.points}>
                                        {r?.needsReview ? '…' : r?.score ?? 0}/{item.maxScore}
                                    </span>
                                    <ChevronDown size={16} className={cn(styles.chevron, { [styles.chevronOpen]: isOpen })} />
                                </button>

                                {isOpen && (
                                    <div className={styles.body}>
                                        <Markdown className={styles.bodyText} source={item.task.condition} />
                                        {item.files.length > 0 && (
                                            <div className={styles.files}>
                                                {item.files.map((f) => (
                                                    <a key={f.url} href={f.url} target="_blank" rel="noreferrer">{f.filename}</a>
                                                ))}
                                            </div>
                                        )}
                                        {r?.reviewerComment && (
                                            <div className={styles.comment}>
                                                <b><MessageSquareText size={14} /> Комментарий преподавателя</b>
                                                {r.reviewerComment}
                                            </div>
                                        )}
                                        {r && (
                                            <div className={styles.solution}>
                                                <p className={styles.solutionTitle}><Lightbulb size={14} />Решение</p>
                                                {r.solution && <Markdown className={styles.solutionText} source={r.solution} />}
                                                {r.solutionVideoUrl && (
                                                    <a href={r.solutionVideoUrl} target="_blank" rel="noreferrer">
                                                        <PlayCircle size={14} /> Видеоразбор
                                                    </a>
                                                )}
                                                <p className={styles.solutionAnswer}>Ответ: <MathText text={r.correctAnswer} /></p>
                                                {r.gradeCriteria && (
                                                    <Markdown className={styles.solutionText} source={`**Критерии оценивания**\n\n${r.gradeCriteria}`} />
                                                )}
                                            </div>
                                        )}
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
