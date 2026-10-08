import { ArrowLeft, ArrowRight, Camera, FileText, Paperclip, Send } from 'lucide-react';
import { useEffect, useRef, type JSX } from 'react';
import { ANSWER_HINTS, ANSWER_PLACEHOLDERS } from '../../../../entities/exam-task';
import { cn, pluralize, useObservable } from '../../../../shared/lib';
import { Button, Markdown } from '../../../../shared/ui';
import styles from './AttemptTaskPanel.module.css';
import type { AttemptTaskPanelProps } from './AttemptTaskPanel.props';

const PHOTO_TYPES = 'image/jpeg,image/png,image/webp,image/heic,application/pdf';


/** Текущее задание: условие, поле ответа и переход по заданиям. Enter — следующее, ← → — когда фокус не в поле */
export const AttemptTaskPanel = ({ session, onSubmit }: AttemptTaskPanelProps): JSX.Element => {
    useObservable(session);
    const inputRef = useRef<HTMLInputElement & HTMLTextAreaElement>(null);
    const fileRef = useRef<HTMLInputElement>(null);
    const { current, item, isFirst, isLast } = session;
    const { task } = item;
    const detailed = task.answerType === 'detailed';
    const files = session.filesOf(current);

    const next = () => (isLast ? onSubmit() : session.goTo(current + 1));

    // Сменилось задание — фокус в поле ответа (на телефоне не открываем клавиатуру сами)
    useEffect(() => {
        if (matchMedia('(hover: hover)').matches) inputRef.current?.focus({ preventScroll: true });
    }, [current]);

    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            const target = e.target as HTMLElement;
            if (target.matches('input, textarea') || document.querySelector('[role="dialog"]')) return;
            if (e.key === 'ArrowLeft') session.goTo(session.current - 1);
            if (e.key === 'ArrowRight') session.goTo(session.current + 1);
        };
        document.addEventListener('keydown', onKey);
        return () => document.removeEventListener('keydown', onKey);
    }, [session]);

    return (
        <article className={cn('glass', styles.card)} aria-live="polite">
            <div className={styles.head}>
                <span className={styles.num}>Задание {current + 1}</span>
                <span className={styles.meta}>
                    №{task.taskNumber} ЕГЭ · {pluralize(item.maxScore, 'балл', 'балла', 'баллов')}
                </span>
            </div>

            {task.sharedText && <Markdown className={styles.shared} source={task.sharedText} />}
            <Markdown className={styles.text} source={task.condition} />

            {task.attachments.length > 0 && (
                <div className={styles.attachments}>
                    {task.attachments.map((f) => (
                        <a key={f.url} href={f.url} target="_blank" rel="noreferrer" download>
                            <Paperclip size={14} />{f.filename}
                        </a>
                    ))}
                </div>
            )}

            {detailed ? (
                <div className={styles.detailed}>
                    <span className={styles.answerLabel}>Решение</span>
                    <textarea
                        ref={inputRef}
                        placeholder={ANSWER_PLACEHOLDERS.detailed}
                        value={session.answerOf(current)}
                        readOnly={session.closed}
                        onChange={(e) => session.setAnswer(e.target.value)}
                    />
                    <div className={styles.upload}>
                        <input
                            ref={fileRef}
                            type="file"
                            accept={PHOTO_TYPES}
                            onChange={(e) => {
                                const file = e.target.files?.[0];
                                e.target.value = '';
                                if (file) void session.upload(file);
                            }}
                        />
                        <Button
                            variant="outline"
                            size="s"
                            radius={12}
                            isLoading={session.uploading}
                            disabled={session.closed}
                            onClick={() => fileRef.current?.click()}
                        >
                            <Camera size={16} />Приложить фото решения
                        </Button>
                        {files.length > 0 && (
                            <div className={styles.files}>
                                {files.map((f) => (
                                    <a key={f.url} href={f.url} target="_blank" rel="noreferrer">
                                        <FileText size={14} />{f.filename}
                                    </a>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            ) : (
                <label className={styles.answer}>
                    <span className={styles.answerLabel}>Ответ</span>
                    <input
                        ref={inputRef}
                        type="text"
                        inputMode={task.answerType === 'short' ? 'decimal' : 'text'}
                        autoComplete="off"
                        spellCheck={false}
                        placeholder={ANSWER_PLACEHOLDERS[task.answerType]}
                        value={session.answerOf(current)}
                        readOnly={session.closed}
                        onChange={(e) => session.setAnswer(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                                e.preventDefault();
                                next();
                            }
                        }}
                    />
                </label>
            )}
            <p className={styles.hint}>
                {ANSWER_HINTS[task.answerType]} Ответ сохраняется сам — можно закрыть страницу и вернуться позже.
            </p>

            <div className={styles.actions}>
                <Button variant="ghost-secondary" size="m" radius={12} disabled={isFirst} onClick={() => session.goTo(current - 1)}>
                    <ArrowLeft size={18} />Предыдущее
                </Button>
                <Button size="m" radius={12} onClick={next}>
                    {isLast ? <>К сдаче<Send size={18} /></> : <>Следующее<ArrowRight size={18} /></>}
                </Button>
            </div>
        </article>
    );
};
