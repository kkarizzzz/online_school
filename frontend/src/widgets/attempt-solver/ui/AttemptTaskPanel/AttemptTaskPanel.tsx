import { ArrowLeft, ArrowRight, Send } from 'lucide-react';
import { useEffect, useRef, type JSX } from 'react';
import { cn, useObservable } from '../../../../shared/lib';
import { Button, MathText } from '../../../../shared/ui';
import styles from './HomeworkTaskPanel.module.css';
import type { HomeworkTaskPanelProps } from './HomeworkTaskPanel.props';


/** Текущая задача: условие, поле ответа и переход по задачам. Enter — следующая, ← → — когда фокус не в поле */
export const HomeworkTaskPanel = ({ attempt, onSubmit }: HomeworkTaskPanelProps): JSX.Element => {
    useObservable(attempt);
    const inputRef = useRef<HTMLInputElement>(null);
    const { current, task, isFirst, isLast } = attempt;

    const next = () => (isLast ? onSubmit() : attempt.goTo(current + 1));

    // Сменилась задача — фокус в поле ответа (на телефоне не открываем клавиатуру сами)
    useEffect(() => {
        if (matchMedia('(hover: hover)').matches) inputRef.current?.focus();
    }, [current]);

    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            const target = e.target as HTMLElement;
            if (target.matches('input, textarea') || document.querySelector('[role="dialog"]')) return;
            if (e.key === 'ArrowLeft') attempt.goTo(attempt.current - 1);
            if (e.key === 'ArrowRight') attempt.goTo(attempt.current + 1);
        };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [attempt]);

    return (
        <article className={cn('glass', styles.card)} aria-live="polite">
            <div className={styles.head}>
                <span className={styles.num}>Задача {current + 1}</span>
                <span className={styles.meta}>№{task.number} ЕГЭ</span>
            </div>

            <MathText className={styles.text} text={task.text} />

            <label className={styles.answer}>
                <span className={styles.answerLabel}>Ответ</span>
                <input
                    ref={inputRef}
                    type="text"
                    inputMode="decimal"
                    autoComplete="off"
                    spellCheck={false}
                    placeholder="Введите число"
                    value={attempt.answerOf(current)}
                    onChange={(e) => attempt.setAnswer(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            next();
                        }
                    }}
                />
            </label>
            <p className={styles.hint}>
                Целое число или десятичная дробь, например <b>0,25</b>. Ответ сохраняется сразу — можно закрыть страницу и вернуться позже.
            </p>

            <div className={styles.actions}>
                <Button variant="ghost-secondary" size="m" radius={12} disabled={isFirst} onClick={() => attempt.goTo(current - 1)}>
                    <ArrowLeft size={18} />Предыдущая
                </Button>
                <Button size="m" radius={12} onClick={next}>
                    {isLast ? <>К сдаче<Send size={18} /></> : <>Следующая<ArrowRight size={18} /></>}
                </Button>
            </div>
        </article>
    );
};
