import { useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, CalendarClock, Send } from 'lucide-react';
import { useEffect, useState, type JSX } from 'react';
import { Link } from 'react-router';
import {
    HOMEWORK_LIST_ROUTE, homeworkKeys, homeworkRepository, useSubmitHomework, type HomeworkResult,
} from '../../../../entities/homework';
import { cn, formatDayMonth, pluralize, useObservable } from '../../../../shared/lib';
import { Button, ModalWindow } from '../../../../shared/ui';
import { HomeworkAttempt } from '../../model/HomeworkAttempt';
import { ElapsedTimer } from '../ElapsedTimer/ElapsedTimer';
import { HomeworkResults } from '../HomeworkResults/HomeworkResults';
import { HomeworkTaskPanel } from '../HomeworkTaskPanel/HomeworkTaskPanel';
import styles from './HomeworkSolver.module.css';
import type { HomeworkSolverProps } from './HomeworkSolver.props';


/**
 * Выполнение ДЗ — как решение варианта-отработки, но без обратного отсчёта: вместо него срок сдачи
 * и секундомер «в работе». «Сдать» → подтверждение → результаты. Сданное ДЗ переписать нельзя.
 */
export const HomeworkSolver = ({ homework }: HomeworkSolverProps): JSX.Element => {
    const queryClient = useQueryClient();
    const { mutate: submit } = useSubmitHomework();
    // Результат держим у себя: сразу после сдачи показываем его, не дожидаясь перезагрузки списка
    const [result, setResult] = useState<HomeworkResult | null>(homework.result);
    const [justFinished, setJustFinished] = useState(false);
    const [confirmOpen, setConfirmOpen] = useState(false);
    const [attempt] = useState(() => (homework.result ? null : new HomeworkAttempt(homework, homeworkRepository)));

    // Уходим со страницы — список ДЗ должен увидеть сохранённые ответы
    useEffect(() => () => {
        queryClient.invalidateQueries({ queryKey: homeworkKeys.all });
    }, [queryClient]);

    const finish = () => {
        if (!attempt) return;
        const final = attempt.toResult();
        setConfirmOpen(false);
        setResult(final);
        setJustFinished(true);
        submit({ id: homework.id, result: final });
        window.scrollTo({ top: 0 });
    };

    const kicker = `Домашнее задание · ${homework.topic} · ${homework.sizeLabel}`;

    return (
        <div className={styles.solve}>
            <header className={cn('glass', styles.top, { [styles.topResults]: result })}>
                <Link className={styles.back} to={result ? `${HOMEWORK_LIST_ROUTE}?tab=done` : HOMEWORK_LIST_ROUTE}>
                    <ArrowLeft size={18} /><span>Домашние задания</span>
                </Link>
                <div className={styles.heading}>
                    <p className={styles.kicker}>{kicker}</p>
                    <h1 className={styles.title}>{homework.title}</h1>
                </div>

                {!result && attempt && (
                    <>
                        <div className={cn(styles.chip, { [styles.chipDanger]: homework.isOverdue })}>
                            <CalendarClock className={styles.chipIcon} size={20} />
                            <span className={styles.chipText}>
                                <b>{formatDayMonth(homework.deadline)}</b>
                                <span>{homework.isOverdue ? 'срок истёк' : 'срок · до 23:59'}</span>
                            </span>
                        </div>
                        <ElapsedTimer since={attempt.startedAt} className={styles.timer} />
                        <Button size="m" radius={12} className={styles.finish} onClick={() => setConfirmOpen(true)}>
                            <Send size={18} />Сдать
                        </Button>
                    </>
                )}
            </header>

            {result ? (
                <HomeworkResults homework={homework} result={result} justFinished={justFinished} />
            ) : attempt && (
                <>
                    <HomeworkWork attempt={attempt} onSubmit={() => setConfirmOpen(true)} />
                    <SubmitDialog
                        open={confirmOpen}
                        unanswered={attempt.unansweredCount}
                        late={homework.isOverdue}
                        onCancel={() => setConfirmOpen(false)}
                        onConfirm={finish}
                    />
                </>
            )}
        </div>
    );
};


const HomeworkWork = ({ attempt, onSubmit }: { attempt: HomeworkAttempt; onSubmit: () => void }): JSX.Element => {
    useObservable(attempt);

    return (
        <section className={styles.work}>
            <nav className={cn('glass', styles.nav)} aria-label="Задачи домашнего задания">
                <div className={styles.navHead}>
                    <span className={styles.navTitle}>Задачи</span>
                    <span className={styles.navProgress}>Отвечено {attempt.answeredCount} из {attempt.tasks.length}</span>
                </div>
                <div className={styles.navStrip}>
                    {attempt.tasks.map((_, i) => (
                        <button
                            key={i}
                            type="button"
                            className={cn(styles.navTask, { [styles.navTaskAnswered]: attempt.isAnswered(i) })}
                            aria-current={i === attempt.current ? 'step' : undefined}
                            aria-label={`Задача ${i + 1}${attempt.isAnswered(i) ? ', есть ответ' : ''}`}
                            onClick={() => attempt.goTo(i)}
                        >
                            {i + 1}
                        </button>
                    ))}
                </div>
            </nav>

            <HomeworkTaskPanel attempt={attempt} onSubmit={onSubmit} />

            <p className={styles.note}>
                Задачи собраны генератором, ответы проверяются в браузере. Позже ДЗ будет проверять преподаватель и оставлять комментарии.
            </p>
        </section>
    );
};


interface SubmitDialogProps {
    open: boolean;
    unanswered: number;
    late: boolean;
    onCancel: () => void;
    onConfirm: () => void;
}

const SubmitDialog = ({ open, unanswered, late, onCancel, onConfirm }: SubmitDialogProps): JSX.Element | null => (
    <ModalWindow isOpen={open} onClose={onCancel} title="Сдать домашнее задание?">
        <p className={styles.confirmText}>
            {unanswered
                ? `Без ответа ${pluralize(unanswered, 'задача', 'задачи', 'задач')} — они будут засчитаны как неверные.`
                : 'Ответы даны на все задачи. После сдачи изменить их будет нельзя.'}
            {late && ' Срок уже прошёл — преподаватель увидит, что ДЗ сдано после дедлайна.'}
        </p>
        <div className={styles.confirmActions}>
            <Button variant="outline" size="m" radius={12} onClick={onCancel}>Вернуться к задачам</Button>
            <Button size="m" radius={12} onClick={onConfirm}><Send size={18} />Сдать и посмотреть результаты</Button>
        </div>
    </ModalWindow>
);
