import { ArrowLeft, CalendarClock, Send } from 'lucide-react';
import { useCallback, useEffect, useState, type JSX } from 'react';
import { Link } from 'react-router';
import { attemptRepository, type AttemptData } from '../../../../entities/attempt';
import { cn, formatDayMonth, parseApiError, pluralize, useObservable } from '../../../../shared/lib';
import { Button, ModalWindow } from '../../../../shared/ui';
import { AttemptSession } from '../../model/AttemptSession';
import { AttemptResults } from '../AttemptResults/AttemptResults';
import { AttemptTaskPanel } from '../AttemptTaskPanel/AttemptTaskPanel';
import { CountdownTimer } from '../CountdownTimer/CountdownTimer';
import { ElapsedTimer } from '../ElapsedTimer/ElapsedTimer';
import styles from './AttemptSolver.module.css';
import type { AttemptSolverProps } from './AttemptSolver.props';


/**
 * Прохождение набора — ДЗ, варианта или отработки. Ответы сохраняются на сервере сразу,
 * у варианта на время — обратный отсчёт (когда время выходит, вариант сдаётся сам),
 * иначе секундомер «в работе». «Сдать» → подтверждение → результаты с разбором.
 */
export const AttemptSolver = ({ attempt, back, kicker, resultActions, onSubmitted }: AttemptSolverProps): JSX.Element => {
    const [result, setResult] = useState<AttemptData | null>(attempt.submittedAt ? attempt : null);
    const [justFinished, setJustFinished] = useState(false);
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);
    const [session] = useState(() => (attempt.submittedAt ? null : new AttemptSession(attempt, attemptRepository)));

    // Уходим со страницы — досохраняем ответы, которые ещё ждут отправки
    useEffect(() => () => {
        void session?.flush();
    }, [session]);

    const finish = useCallback(async () => {
        if (!session) return;
        setSubmitting(true);
        setSubmitError(null);
        try {
            const final = await session.submit();
            setConfirmOpen(false);
            setResult(final);
            setJustFinished(true);
            onSubmitted?.(final);
            window.scrollTo({ top: 0 });
        } catch (error) {
            setSubmitError(parseApiError(error, 'Не удалось сдать — проверьте интернет и попробуйте ещё раз'));
            // Время могло выйти, и сервер сдал попытку сам — тогда показываем её
            try {
                const fresh = await attemptRepository.get(attempt.id);
                if (fresh.submittedAt) {
                    setConfirmOpen(false);
                    setResult(fresh);
                    onSubmitted?.(fresh);
                }
            } catch {
                // остаёмся на странице решения с сообщением об ошибке
            }
        } finally {
            setSubmitting(false);
        }
    }, [session, attempt.id, onSubmitted]);

    // Срок проверяем один раз при открытии — пока решают, плашка не перекрашивается
    const [isOverdue] = useState(() => !!attempt.deadlineAt && new Date(attempt.deadlineAt).getTime() < Date.now());

    return (
        <div className={styles.solve}>
            <header className={cn('glass', styles.top, { [styles.topResults]: result })}>
                <Link className={styles.back} to={back.to}>
                    <ArrowLeft size={18} /><span>{back.label}</span>
                </Link>
                <div className={styles.heading}>
                    <p className={styles.kicker}>{kicker}</p>
                    <h1 className={styles.title}>{attempt.set.title}</h1>
                </div>

                {!result && session && (
                    <>
                        {attempt.deadlineAt && (
                            <div className={cn(styles.chip, { [styles.chipDanger]: isOverdue })}>
                                <CalendarClock className={styles.chipIcon} size={20} />
                                <span className={styles.chipText}>
                                    <b>{formatDayMonth(attempt.deadlineAt)}</b>
                                    <span>{isOverdue ? 'срок истёк' : 'срок сдачи'}</span>
                                </span>
                            </div>
                        )}
                        {session.expiresAt !== null ? (
                            <CountdownTimer until={session.expiresAt} onExpire={finish} />
                        ) : (
                            <ElapsedTimer since={session.startedAt} className={styles.timer} />
                        )}
                        <Button size="m" radius={12} className={styles.finish} onClick={() => setConfirmOpen(true)}>
                            <Send size={18} />Сдать
                        </Button>
                    </>
                )}
            </header>

            {result ? (
                <AttemptResults attempt={result} justFinished={justFinished} actions={resultActions} />
            ) : session && (
                <>
                    <AttemptWork session={session} onSubmit={() => setConfirmOpen(true)} />
                    <SubmitDialog
                        open={confirmOpen}
                        unanswered={session.unansweredCount}
                        late={isOverdue}
                        submitting={submitting}
                        error={submitError}
                        onCancel={() => setConfirmOpen(false)}
                        onConfirm={finish}
                    />
                </>
            )}
        </div>
    );
};


const AttemptWork = ({ session, onSubmit }: { session: AttemptSession; onSubmit: () => void }): JSX.Element => {
    useObservable(session);
    const standard = session.data.set.isStandard;

    return (
        <section className={styles.work}>
            <nav className={cn('glass', styles.nav)} aria-label="Задания">
                <div className={styles.navHead}>
                    <span className={styles.navTitle}>Задания</span>
                    <span className={styles.navProgress}>Отвечено {session.answeredCount} из {session.items.length}</span>
                </div>
                <div className={styles.navStrip}>
                    {session.items.map((item, i) => (
                        <button
                            key={item.position}
                            type="button"
                            className={cn(styles.navTask, { [styles.navTaskAnswered]: session.isAnswered(i) })}
                            aria-current={i === session.current ? 'step' : undefined}
                            aria-label={`Задание ${i + 1}${session.isAnswered(i) ? ', есть ответ' : ''}`}
                            title={standard ? `№${item.task.taskNumber}` : undefined}
                            onClick={() => session.goTo(i)}
                        >
                            {i + 1}
                        </button>
                    ))}
                </div>
            </nav>

            {session.saveError && <p className={styles.saveError} role="alert">{session.saveError}</p>}

            <AttemptTaskPanel session={session} onSubmit={onSubmit} />
        </section>
    );
};


interface SubmitDialogProps {
    open: boolean;
    unanswered: number;
    late: boolean;
    submitting: boolean;
    error: string | null;
    onCancel: () => void;
    onConfirm: () => void;
}

const SubmitDialog = ({ open, unanswered, late, submitting, error, onCancel, onConfirm }: SubmitDialogProps): JSX.Element | null => (
    <ModalWindow isOpen={open} onClose={onCancel} title="Сдать работу?">
        <p className={styles.confirmText}>
            {unanswered
                ? `Без ответа ${pluralize(unanswered, 'задание', 'задания', 'заданий')} — они будут засчитаны как неверные.`
                : 'Ответы даны на все задания. После сдачи изменить их будет нельзя.'}
            {late && ' Срок уже прошёл — преподаватель увидит, что работа сдана после дедлайна.'}
        </p>
        {error && <p className={styles.saveError} role="alert">{error}</p>}
        <div className={styles.confirmActions}>
            <Button variant="outline" size="m" radius={12} onClick={onCancel}>Вернуться к заданиям</Button>
            <Button size="m" radius={12} isLoading={submitting} onClick={onConfirm}>
                <Send size={18} />Сдать и посмотреть результаты
            </Button>
        </div>
    </ModalWindow>
);
