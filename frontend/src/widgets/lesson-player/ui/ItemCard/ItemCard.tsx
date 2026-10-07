import { BookOpenCheck, Check, CircleCheck, CircleX, Eye, Info, Lightbulb, RotateCcw, X } from 'lucide-react';
import { useRef, useState, type FormEvent, type JSX } from 'react';
import { cn, OPTION_LETTERS, pluralize } from '../../../../shared/lib';
import { Button, HtmlText } from '../../../../shared/ui';
import { ChoiceItem, InputItem } from '../../model/LessonItem';
import styles from './ItemCard.module.css';
import type { ItemCardProps } from './ItemCard.props';


/** Вопрос под роликом или задача практики: варианты ответа либо ввод числа */
export const ItemCard = ({ session, stepIndex, itemIndex, onSolved, onRewatch, className, ...props }: ItemCardProps): JSX.Element => {
    const item = session.steps[stepIndex].items[itemIndex];
    const progress = session.progress(stepIndex, itemIndex);
    const isPractice = session.steps[stepIndex].kind === 'practice';
    const locked = progress.isResolved;

    const [value, setValue] = useState(progress.value);
    const inputRef = useRef<HTMLInputElement>(null);

    const answerChoice = (option: number) => {
        if (session.answerChoice(stepIndex, itemIndex, option)) onSolved(itemIndex);
    };

    const answerInput = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (session.answerInput(stepIndex, itemIndex, value)) onSolved(itemIndex);
        else inputRef.current?.focus();
    };

    const pill = progress.status === 'ok'
        ? <span className={cn(styles.pill, styles.pillOk)}><Check size={13} />Решено</span>
        : progress.status === 'shown'
            ? <span className={cn(styles.pill, styles.pillShown)}>Решение открыто</span>
            : progress.tries
                ? <span className={cn(styles.pill, styles.pillBad)}>{pluralize(progress.tries, 'ошибка', 'ошибки', 'ошибок')}</span>
                : null;

    return (
        <article
            className={cn('glass', styles.card, {
                [styles.ok]: progress.status === 'ok',
                [styles.shown]: progress.status === 'shown',
                [styles.bad]: !locked && progress.tries > 0,
            }, className)}
            data-item={itemIndex}
            {...props}
        >
            <div className={styles.head}>
                <span className={styles.num}>{isPractice ? 'Задача' : 'Вопрос'} {itemIndex + 1}</span>
                <span className={styles.kind}>{item instanceof InputItem ? 'Введите ответ' : 'Выберите ответ'}</span>
                {pill}
            </div>

            <HtmlText className={styles.question} html={item.question} />

            {item instanceof ChoiceItem && (
                <div className={styles.options} role="group" aria-label="Варианты ответа">
                    {item.options.map((option, oi) => {
                        const right = locked && oi === item.correct;
                        const wrong = progress.wrong.includes(oi);
                        return (
                            <button
                                key={oi}
                                type="button"
                                className={cn(styles.option, { [styles.right]: right, [styles.wrong]: wrong })}
                                disabled={locked || wrong}
                                onClick={() => answerChoice(oi)}
                            >
                                <span className={styles.letter}>{OPTION_LETTERS[oi]}</span>
                                <HtmlText className={styles.optionText} html={option} />
                                {right && <Check size={18} />}
                                {wrong && <X size={18} />}
                            </button>
                        );
                    })}
                </div>
            )}

            {item instanceof InputItem && (
                <form className={styles.answer} onSubmit={answerInput}>
                    <label className={cn(styles.field, { [styles.fieldRight]: progress.isSolved })}>
                        <span className={styles.srOnly}>Ваш ответ</span>
                        <input
                            ref={inputRef}
                            type="text"
                            inputMode="decimal"
                            autoComplete="off"
                            placeholder="Ответ, например 2 или 3/2"
                            value={progress.status === 'shown' ? item.answerText : value}
                            onChange={(e) => setValue(e.target.value)}
                            disabled={locked}
                        />
                    </label>
                    <Button type="submit" size="m" disabled={locked} disableJump>Проверить</Button>
                </form>
            )}

            <Feedback
                session={session}
                stepIndex={stepIndex}
                itemIndex={itemIndex}
                isPractice={isPractice}
                onRewatch={onRewatch}
            />
        </article>
    );
};


interface FeedbackProps {
    session: ItemCardProps['session'];
    stepIndex: number;
    itemIndex: number;
    isPractice: boolean;
    onRewatch?: () => void;
}

const Feedback = ({ session, stepIndex, itemIndex, isPractice, onRewatch }: FeedbackProps): JSX.Element | null => {
    const item = session.steps[stepIndex].items[itemIndex];
    const progress = session.progress(stepIndex, itemIndex);

    if (progress.status === 'ok') {
        return (
            <div className={cn(styles.fb, styles.fbOk)}>
                <CircleCheck size={18} />
                <p><b>{progress.tries === 0 ? 'Верно с первой попытки!' : 'Верно!'}</b> <HtmlText html={item.explain} /></p>
            </div>
        );
    }

    if (progress.status === 'shown') {
        return (
            <div className={cn(styles.fb, styles.fbShown)}>
                <BookOpenCheck size={18} />
                <p><b>Ответ: <HtmlText html={item.answerText} />.</b> <HtmlText html={item.explain} /></p>
            </div>
        );
    }

    const showHintButton = isPractice && !!item.hint && !progress.hint;
    const showSolutionButton = isPractice && progress.tries > 0;
    const showRewatch = !isPractice && progress.tries > 0 && !!onRewatch;

    if (!progress.error && !progress.tries && !progress.hint && !showHintButton) return null;

    return (
        <div className={styles.feedback}>
            {progress.error ? (
                <div className={cn(styles.fb, styles.fbShown)}>
                    <Info size={18} />
                    <p>{progress.error}</p>
                </div>
            ) : progress.tries > 0 && (
                <div className={cn(styles.fb, styles.fbBad)}>
                    <CircleX size={18} />
                    <p><b>Не совсем.</b> {isPractice ? 'Попробуйте ещё раз.' : 'Попробуйте ещё раз или пересмотрите ролик.'}</p>
                </div>
            )}

            {progress.hint && item.hint && (
                <div className={cn(styles.fb, styles.fbHint)}>
                    <Lightbulb size={18} />
                    <p><b>Подсказка.</b> <HtmlText html={item.hint} /></p>
                </div>
            )}

            {(showHintButton || showSolutionButton || showRewatch) && (
                <div className={styles.actions}>
                    {showRewatch && (
                        <button type="button" className={styles.chip} onClick={onRewatch}>
                            <RotateCcw size={15} />Пересмотреть ролик
                        </button>
                    )}
                    {showHintButton && (
                        <button type="button" className={styles.chip} onClick={() => session.showHint(stepIndex, itemIndex)}>
                            <Lightbulb size={15} />Подсказка
                        </button>
                    )}
                    {showSolutionButton && (
                        <button type="button" className={styles.chip} onClick={() => session.showSolution(stepIndex, itemIndex)}>
                            <Eye size={15} />Показать решение
                        </button>
                    )}
                </div>
            )}
        </div>
    );
};
