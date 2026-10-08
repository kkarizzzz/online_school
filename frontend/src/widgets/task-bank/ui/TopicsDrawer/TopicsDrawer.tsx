import { ArrowRight, X } from 'lucide-react';
import { useEffect, useRef, useState, type JSX } from 'react';
import { Link } from 'react-router';
import { BANK_PART_LABEL, bankNumberRoute } from '../../../../entities/bank-task';
import { cn, pluralize } from '../../../../shared/lib';
import { Button } from '../../../../shared/ui';
import { TopicChoice } from '../../model/TopicChoice';
import styles from './TopicsDrawer.module.css';
import type { TopicsDrawerProps } from './TopicsDrawer.props';

const tasksLabel = (n: number) => pluralize(n, 'задание', 'задания', 'заданий');


/**
 * Панель тем номера: темы отмечаются галочками, «Все темы» выбирает или снимает все сразу.
 * Кнопка внизу ведёт к заданиям выбранных тем. Закрыть — крестик, фон или Esc.
 */
export const TopicsDrawer = ({ number, onClose }: TopicsDrawerProps): JSX.Element => {
    const [chosen, setChosen] = useState<Set<string>>(() => (number ? TopicChoice.load(number) : new Set()));
    const closeRef = useRef<HTMLButtonElement>(null);
    const isOpen = !!number;

    useEffect(() => {
        if (!isOpen) return;
        const lastFocus = document.activeElement as HTMLElement | null;
        closeRef.current?.focus();
        document.body.style.overflow = 'hidden';
        const onKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        document.addEventListener('keydown', onKey);
        return () => {
            document.removeEventListener('keydown', onKey);
            document.body.style.overflow = '';
            lastFocus?.focus();
        };
    }, [isOpen, onClose]);

    const update = (next: Set<string>) => {
        setChosen(next);
        if (number) TopicChoice.save(number, next);
    };

    const toggle = (id: string) => {
        const next = new Set(chosen);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        update(next);
    };

    const topics = number?.topics ?? [];
    const allChosen = topics.length > 0 && chosen.size === topics.length;
    const total = topics.reduce((s, t) => s + t.tasks.length, 0);
    const count = topics.filter((t) => chosen.has(t.id)).reduce((s, t) => s + t.tasks.length, 0);
    // Все темы — без topics в адресе
    const to = number ? bankNumberRoute(number.n, allChosen ? undefined : [...chosen]) : '';

    return (
        <>
            {isOpen && <div className={styles.backdrop} onClick={onClose} />}
            <aside
                className={cn(styles.drawer, { [styles.on]: isOpen })}
                role="dialog"
                aria-modal="true"
                aria-hidden={!isOpen}
                aria-labelledby="topics-drawer-title"
            >
                {number && (
                    <>
                        <Button
                            ref={closeRef}
                            variant="ghost-secondary"
                            size="icon"
                            iconSize={40}
                            className={styles.close}
                            onClick={onClose}
                            aria-label="Закрыть"
                        >
                            <X size={22} />
                        </Button>

                        <div className={styles.body}>
                            <span className={styles.partTag}>{BANK_PART_LABEL[number.part]}</span>
                            <h2 className={styles.title} id="topics-drawer-title">
                                <span className={styles.num}>№{number.n}</span>{number.title}
                            </h2>
                            <p className={styles.sub}>Выберите темы, задания которых хотите решать.</p>

                            <label className={cn(styles.topic, styles.topicAll)}>
                                <input
                                    type="checkbox"
                                    className={styles.check}
                                    checked={allChosen}
                                    // Выбрана часть тем — галочка в промежуточном состоянии
                                    ref={(el) => {
                                        if (el) el.indeterminate = chosen.size > 0 && !allChosen;
                                    }}
                                    onChange={() => update(allChosen ? new Set() : new Set(topics.map((t) => t.id)))}
                                />
                                <span className={styles.topicMain}>
                                    <span className={styles.topicName}>Все темы</span>
                                    <span className={styles.topicMeta}>
                                        {pluralize(topics.length, 'тема', 'темы', 'тем')} · {tasksLabel(total)}
                                    </span>
                                </span>
                            </label>

                            <ul className={styles.topics}>
                                {topics.map((t) => (
                                    <li key={t.id}>
                                        <label className={styles.topic}>
                                            <input
                                                type="checkbox"
                                                className={styles.check}
                                                checked={chosen.has(t.id)}
                                                onChange={() => toggle(t.id)}
                                            />
                                            <span className={styles.topicMain}>
                                                <span className={styles.topicName}>{t.name}</span>
                                                <span className={styles.topicMeta}>{tasksLabel(t.tasks.length)}</span>
                                            </span>
                                        </label>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className={styles.foot}>
                            {count ? (
                                <Button as={Link} to={to} size="m" radius={12} className={styles.go}>
                                    К заданиям · {count}<ArrowRight size={18} />
                                </Button>
                            ) : (
                                <Button size="m" radius={12} className={styles.go} disabled>
                                    Выберите хотя бы одну тему
                                </Button>
                            )}
                        </div>
                    </>
                )}
            </aside>
        </>
    );
};
