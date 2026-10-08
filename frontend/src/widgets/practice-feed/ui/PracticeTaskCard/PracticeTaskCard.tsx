import { ArrowRight, Check, ChevronRight, CircleCheck, CircleX, Eye, Hourglass, Info, Shuffle, WifiOff } from 'lucide-react';
import { useEffect, useRef, useState, type FormEvent, type JSX } from 'react';
import { ANSWER_HINTS, ANSWER_PLACEHOLDERS, DIFFICULTY_LABELS } from '../../../../entities/exam-task';
import type { SubmitResult } from '../../../../entities/practice-task';
import { cn, plural, pluralize } from '../../../../shared/lib';
import { Button, Markdown } from '../../../../shared/ui';
import styles from './PracticeTaskCard.module.css';
import type { PracticeTaskCardProps } from './PracticeTaskCard.props';


/** Задание ленты: условие, ответ, проверка, решение и переход дальше */
export const PracticeTaskCard = ({ feed, task }: PracticeTaskCardProps): JSX.Element => {
    const [answer, setAnswer] = useState('');
    const [empty, setEmpty] = useState(false);
    const [showSource, setShowSource] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const nextRef = useRef<HTMLButtonElement>(null);

    const { result, wrong, revealed, submitting, error } = feed.attempt;
    const finished = feed.isFinished;

    useEffect(() => {
        inputRef.current?.focus({ preventScroll: true });
    }, []);

    useEffect(() => {
        if (finished) nextRef.current?.focus({ preventScroll: true });
        else if (wrong) inputRef.current?.select();
    }, [finished, wrong, result]);

    const submit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!answer.trim()) {
            setEmpty(true);
            inputRef.current?.focus();
            return;
        }
        feed.submit(answer);
    };

    const goNext = (load: () => Promise<void>) => {
        load();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const meta = [
        task.subtopic ? task.topic : null,
        `Часть ${task.part}`,
        DIFFICULTY_LABELS[task.difficulty],
        pluralize(task.maxScore, 'балл', 'балла', 'баллов'),
        ...task.sources,
    ].filter(Boolean);

    return (
        <article className={cn('glass', styles.task)}>
            <div className={styles.head}>
                <span className={styles.badge}>№{task.taskNumber}</span>
                <div className={styles.info}>
                    <h2 className={styles.title}>{task.subtopic ?? task.topic ?? 'Задание'}</h2>
                    <p className={styles.meta}>{meta.join(' · ')}</p>
                </div>
                <button
                    type="button"
                    className={styles.mdToggle}
                    aria-pressed={showSource}
                    title="Показать, как условие хранится в базе"
                    onClick={() => setShowSource((v) => !v)}
                >
                    MD
                </button>
            </div>

            {showSource && <pre className={styles.source}>{task.condition}</pre>}
            {task.sharedText && <Markdown className={styles.shared} source={task.sharedText} />}
            <Markdown source={task.condition} />

            <form className={styles.answer} autoComplete="off" noValidate onSubmit={submit}>
                <input
                    ref={inputRef}
                    className={cn(styles.input, {
                        [styles.inputError]: empty || (wrong && !revealed),
                        [styles.inputSuccess]: result?.isCorrect === true,
                    })}
                    value={answer}
                    onChange={(e) => {
                        setAnswer(e.target.value);
                        setEmpty(false);
                    }}
                    placeholder={ANSWER_PLACEHOLDERS[task.answerType]}
                    aria-label="Ответ"
                    inputMode="decimal"
                    readOnly={finished}
                />
                {!finished && (
                    <Button type="submit" size="m" isLoading={submitting}><Check size={20} />Проверить</Button>
                )}
            </form>
            <p className={styles.hint}>{ANSWER_HINTS[task.answerType]}</p>

            {error && (
                <Result tone="fail" icon={<WifiOff size={22} />} title="Не удалось проверить ответ" text={error} />
            )}

            {result && (
                <ResultBlock
                    result={result}
                    revealed={revealed}
                    streak={feed.streak}
                    onReveal={() => feed.reveal()}
                />
            )}

            {finished && (
                <div className={styles.next}>
                    <Button ref={nextRef} size="m" disabled={feed.loading} onClick={() => goNext(() => feed.next())}>
                        Следующее задание<ArrowRight size={20} />
                    </Button>
                    <Button
                        variant="outline-primary"
                        size="m"
                        disabled={feed.loading || !task.similarCount}
                        title={task.similarCount ? undefined : 'Похожих заданий пока нет'}
                        onClick={() => goNext(() => feed.similar())}
                    >
                        <Shuffle size={20} />Решить похожее
                    </Button>
                </div>
            )}

            {result?.solution && finished && (
                <details className={styles.solution} open={revealed}>
                    <summary><ChevronRight size={16} />Решение</summary>
                    <Markdown className={styles.solutionBody} source={result.solution} />
                </details>
            )}
        </article>
    );
};


interface ResultBlockProps {
    result: SubmitResult;
    revealed: boolean;
    streak: number;
    onReveal: () => void;
}

const ResultBlock = ({ result, revealed, streak, onReveal }: ResultBlockProps): JSX.Element => {
    if (result.isCorrect === true) {
        const score = result.score ?? result.maxScore;
        const streakText = streak >= 3 ? ` · серия ${streak} 🔥` : '';
        return (
            <Result
                tone="ok"
                icon={<CircleCheck size={22} />}
                title={`Верно! +${score} ${plural(score, 'балл', 'балла', 'баллов')}${streakText}`}
            />
        );
    }

    if (result.isCorrect === null) {
        return (
            <Result
                tone="ok"
                icon={<Hourglass size={22} />}
                title="Ответ отправлен на проверку"
                text="Развёрнутые ответы проверяет куратор по критериям — баллы появятся позже."
            />
        );
    }

    if (revealed) {
        return (
            <Result
                tone="fail"
                icon={<Info size={22} />}
                title={`Правильный ответ: ${result.correctAnswer}`}
                text="Разберите решение и закрепите тему похожей задачей."
            />
        );
    }

    return (
        <>
            <Result tone="fail" icon={<CircleX size={22} />} title="Неверно" text="Проверьте вычисления и попробуйте ещё раз." />
            <Button variant="ghost-secondary" size="s" className={styles.reveal} onClick={onReveal}>
                <Eye size={18} />Показать ответ и решение
            </Button>
        </>
    );
};


interface ResultProps {
    tone: 'ok' | 'fail';
    icon: JSX.Element;
    title: string;
    text?: string;
}

const Result = ({ tone, icon, title, text }: ResultProps): JSX.Element => (
    <div className={cn(styles.result, tone === 'ok' ? styles.ok : styles.fail)}>
        {icon}
        <div>
            <div className={styles.resultTitle}>{title}</div>
            {text && <div className={styles.resultText}>{text}</div>}
        </div>
    </div>
);
