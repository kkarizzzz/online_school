import { ArrowRight, Check, CircleCheck, CircleX, EyeOff, Hourglass, Lightbulb, Shuffle, WifiOff } from 'lucide-react';
import { useEffect, useRef, useState, type FormEvent, type JSX } from 'react';
import { ANSWER_HINTS, ANSWER_PLACEHOLDERS, DIFFICULTY_LABELS } from '../../../../entities/exam-task';
import type { SubmitResult } from '../../../../entities/practice-task';
import { cn, plural, pluralize } from '../../../../shared/lib';
import { Button, Markdown } from '../../../../shared/ui';
import styles from './PracticeTaskCard.module.css';
import type { PracticeTaskCardProps } from './PracticeTaskCard.props';


/**
 * Задание ленты: условие, ответ, проверка, решение и переход дальше.
 * Решение можно открыть в любой момент; «Похожее» появляется после ответа (верного или нет) или просмотра решения.
 */
export const PracticeTaskCard = ({ feed, task }: PracticeTaskCardProps): JSX.Element => {
    const [answer, setAnswer] = useState('');
    const [empty, setEmpty] = useState(false);
    const [showSource, setShowSource] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const nextRef = useRef<HTMLButtonElement>(null);

    const { result, wrong, solution, revealed, submitting, revealing, error } = feed.attempt;
    const accepted = feed.isAccepted;

    useEffect(() => {
        inputRef.current?.focus({ preventScroll: true });
    }, []);

    useEffect(() => {
        if (accepted) nextRef.current?.focus({ preventScroll: true });
        else if (wrong) inputRef.current?.select();
    }, [accepted, wrong, result]);

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
                        [styles.inputError]: empty || wrong,
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
                    readOnly={accepted}
                />
                {!accepted && (
                    <Button type="submit" size="m" isLoading={submitting}><Check size={20} />Проверить</Button>
                )}
            </form>
            <p className={styles.hint}>{ANSWER_HINTS[task.answerType]}</p>

            {error && <Result tone="fail" icon={<WifiOff size={22} />} title="Не удалось связаться с сервером" text={error} />}
            {result && <ResultBlock result={result} streak={feed.streak} />}

            {revealed && solution && (
                <section className={styles.solution} aria-label="Решение">
                    <p className={styles.solutionTitle}><Lightbulb size={16} />Решение</p>
                    {solution.solution
                        ? <Markdown className={styles.solutionBody} source={solution.solution} />
                        : <p className={styles.solutionEmpty}>Разбора к этому заданию пока нет.</p>}
                    <p className={styles.solutionAnswer}>Ответ: <b>{solution.correctAnswer}</b></p>
                </section>
            )}

            <div className={styles.actions}>
                <Button
                    variant="ghost-secondary"
                    size="m"
                    isLoading={revealing}
                    aria-expanded={revealed}
                    onClick={() => feed.toggleSolution()}
                >
                    {revealed ? <><EyeOff size={18} />Скрыть решение</> : <><Lightbulb size={18} />Показать решение</>}
                </Button>
                <span className={styles.spacer} />
                {feed.canTakeSimilar && (
                    <Button
                        variant="outline"
                        size="m"
                        disabled={feed.loading || !task.similarCount}
                        title={task.similarCount ? 'Ещё задание из той же подтемы' : 'Похожих заданий пока нет'}
                        onClick={() => goNext(() => feed.similar())}
                    >
                        <Shuffle size={18} />Похожее
                    </Button>
                )}
                <Button
                    ref={nextRef}
                    variant={accepted ? 'primary' : 'outline'}
                    size="m"
                    disabled={feed.loading}
                    onClick={() => goNext(() => feed.next())}
                >
                    Следующее<ArrowRight size={18} />
                </Button>
            </div>
        </article>
    );
};


const ResultBlock = ({ result, streak }: { result: SubmitResult; streak: number }): JSX.Element => {
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

    return <Result tone="fail" icon={<CircleX size={22} />} title="Неверно" text="Попробуйте ещё раз или посмотрите решение." />;
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
