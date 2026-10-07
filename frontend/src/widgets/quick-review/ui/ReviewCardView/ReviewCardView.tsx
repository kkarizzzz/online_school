import { ArrowRight, Check, CircleCheck, CircleHelp, CircleX, Info, RotateCcw, X } from 'lucide-react';
import { useEffect, useRef, type JSX } from 'react';
import { cn, OPTION_LETTERS } from '../../../../shared/lib';
import { Button, MathText } from '../../../../shared/ui';
import { KIND_META } from '../../lib/modeIcons';
import { DONT_KNOW } from '../../model/ReviewFeed';
import styles from './ReviewCardView.module.css';
import type { ReviewCardViewProps } from './ReviewCardView.props';


/** Карточка вопроса: варианты (клавиши 1–4), «Не знаю», пояснение и «Дальше» (Enter) */
export const ReviewCardView = ({ feed, card }: ReviewCardViewProps): JSX.Element => {
    const nextRef = useRef<HTMLButtonElement>(null);
    const { question } = card;
    const kind = KIND_META[question.kind];
    const KindIcon = kind.icon;
    const streak = feed.session?.streak ?? 0;

    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            const target = e.target as HTMLElement | null;
            if (e.ctrlKey || e.metaKey || e.altKey || target?.closest('input, textarea')) return;
            if (!card.isAnswered) {
                const position = Number(e.key) - 1;
                if (position >= 0 && position < card.order.length) feed.answer(card.order[position]);
            } else if (e.key === 'Enter') {
                e.preventDefault(); // иначе фокус на «Дальше» нажмёт её второй раз
                feed.next();
            }
        };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [feed, card]);

    useEffect(() => {
        if (card.isAnswered) nextRef.current?.focus({ preventScroll: true });
    }, [card.isAnswered]);

    const tone = !card.isAnswered ? null : card.isCorrect ? 'ok' : card.isDontKnow ? 'shown' : 'bad';
    const title = card.isCorrect
        ? `Верно!${streak >= 3 ? ` Серия ${streak} 🔥` : ''}`
        : card.isDontKnow ? 'Правильный ответ отмечен зелёным.' : 'Неверно.';

    return (
        <article className={cn('glass', styles.card, tone && styles[tone])}>
            <div className={styles.head}>
                <span className={styles.num}>Вопрос {card.number}</span>
                <span className={styles.tag}>{question.topic}</span>
                <span className={cn(styles.tag, styles[`kind-${question.kind}`])}><KindIcon size={13} />{kind.label}</span>
                {card.retry && <span className={cn(styles.tag, styles.retry)}><RotateCcw size={13} />Повтор ошибки</span>}
            </div>

            <MathText className={styles.question} text={question.q} />

            <div className={styles.options} role="group" aria-label="Варианты ответа">
                {card.order.map((option, position) => {
                    const right = card.isAnswered && option === 0;
                    const wrong = card.isAnswered && option === card.picked && option !== 0;
                    return (
                        <button
                            key={option}
                            type="button"
                            className={cn(styles.option, { [styles.right]: right, [styles.wrong]: wrong })}
                            disabled={card.isAnswered}
                            onClick={() => feed.answer(option)}
                        >
                            <span className={styles.letter}>{OPTION_LETTERS[position]}</span>
                            <MathText className={styles.optionText} text={question.options[option]} />
                            {right && <Check size={18} />}
                            {wrong && <X size={18} />}
                        </button>
                    );
                })}
            </div>

            {card.isAnswered && tone && (
                <div className={cn(styles.fb, styles[`fb-${tone}`])}>
                    {tone === 'ok' ? <CircleCheck size={18} /> : tone === 'shown' ? <Info size={18} /> : <CircleX size={18} />}
                    <div>
                        <b>{title}</b> <MathText text={question.explain} />
                        {!card.isCorrect && <span className={styles.fbNote}>Этот вопрос вернётся через пару карточек.</span>}
                    </div>
                </div>
            )}

            <div className={styles.foot}>
                {card.isAnswered ? (
                    <>
                        <span className={styles.keyHint}><kbd>Enter</kbd> — следующий вопрос</span>
                        <Button ref={nextRef} size="m" onClick={() => feed.next()}>Дальше<ArrowRight size={18} /></Button>
                    </>
                ) : (
                    <>
                        <span className={styles.keyHint}>Клавиши <kbd>1</kbd>–<kbd>{card.order.length}</kbd> выбирают ответ</span>
                        <button type="button" className={styles.chip} onClick={() => feed.answer(DONT_KNOW)}>
                            <CircleHelp size={15} />Не знаю
                        </button>
                    </>
                )}
            </div>
        </article>
    );
};
