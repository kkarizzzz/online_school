import { ArrowRight, Lightbulb, TriangleAlert, X } from 'lucide-react';
import { useEffect, useRef, type JSX } from 'react';
import { Link } from 'react-router';
import { useLessonSummary, type LessonSummaryData } from '../../../../entities/curriculum';
import { lessonRoute } from '../../../../entities/lesson';
import { cn } from '../../../../shared/lib';
import { Button } from '../../../../shared/ui';
import styles from './LessonDrawer.module.css';
import type { LessonDrawerProps } from './LessonDrawer.props';


/** Выезжающая панель урока: мини-конспект и переход к прохождению */
export const LessonDrawer = ({ lesson, open, progress, onClose }: LessonDrawerProps): JSX.Element => {
    const { data: summary } = useLessonSummary(lesson);
    const closeRef = useRef<HTMLButtonElement>(null);
    const bodyRef = useRef<HTMLDivElement>(null);
    const isOpen = open && !!lesson;

    useEffect(() => {
        if (!isOpen) return;
        const lastFocus = document.activeElement as HTMLElement | null;
        closeRef.current?.focus();
        const onKey = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        document.addEventListener('keydown', onKey);
        return () => {
            document.removeEventListener('keydown', onKey);
            lastFocus?.focus();
        };
    }, [isOpen, onClose]);

    useEffect(() => {
        bodyRef.current?.scrollTo({ top: 0 });
    }, [lesson]);

    const topic = lesson?.topic;
    const status = !lesson ? '' : progress.isDone(lesson) ? 'Пройден' : progress.isNext(lesson) ? 'Следующий урок' : 'Не пройден';

    return (
        <>
            {isOpen && <div className={styles.backdrop} onClick={onClose} />}
            <aside
                className={cn(styles.drawer, { [styles.on]: isOpen })}
                role="dialog"
                aria-hidden={!isOpen}
                aria-labelledby="lesson-drawer-title"
            >
                {lesson && topic && (
                    <>
                        <div className={styles.head}>
                            <p className={styles.crumb}>Уровень {topic.level} &middot; Ветка {topic.branch + 1} &middot; {topic.title}</p>
                            <Button ref={closeRef} variant="ghost-secondary" size="icon" iconSize={40} onClick={onClose} aria-label="Закрыть">
                                <X size={22} />
                            </Button>
                        </div>

                        <div className={styles.body} ref={bodyRef}>
                            <h2 className={styles.title} id="lesson-drawer-title">{lesson.id}. {lesson.name}</h2>
                            <p className={styles.meta}>
                                {[`Урок ${lesson.index} из ${topic.lessons.length}`, `≈ ${lesson.minutes} мин`,
                                    ...topic.examTasks.map((n) => `№${n}`), status].join(' · ')}
                            </p>
                            {summary && <Conspect summary={summary} />}
                        </div>

                        <div className={styles.foot}>
                            <Button as={Link} to={lessonRoute(lesson.id)} size="m" className={styles.go} disableJump>
                                Перейти к уроку<ArrowRight size={18} />
                            </Button>
                        </div>
                    </>
                )}
            </aside>
        </>
    );
};


const Conspect = ({ summary }: { summary: LessonSummaryData }): JSX.Element => {
    const warn = summary.tip?.kind === 'warn';
    const PointsList = summary.steps ? 'ol' : 'ul';

    return (
        <div className={styles.conspect}>
            <section className={styles.block}>
                <h3 className={styles.blockTitle}>Кратко</h3>
                <p className={styles.intro}>{summary.intro}</p>
            </section>

            {!!summary.formulas?.length && (
                <section className={styles.block}>
                    <h3 className={styles.blockTitle}>Формулы и правила</h3>
                    <div className={styles.formulas}>
                        {summary.formulas.map(([label, formula]) => (
                            <div key={label + formula} className={styles.formula}>
                                <span>{label}</span>
                                <code>{formula}</code>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {!!summary.points?.length && (
                <section className={styles.block}>
                    <h3 className={styles.blockTitle}>{summary.steps ? 'Порядок действий' : 'Главное'}</h3>
                    <PointsList className={styles.points}>
                        {summary.points.map((p) => <li key={p}>{p}</li>)}
                    </PointsList>
                </section>
            )}

            {summary.tip && (
                <div className={cn(styles.tip, { [styles.tipWarn]: warn })}>
                    {warn ? <TriangleAlert size={18} /> : <Lightbulb size={18} />}
                    <p><b>{warn ? 'Частая ошибка' : 'Запомни'}.</b> {summary.tip.text}</p>
                </div>
            )}

            {summary.example && (
                <section className={cn(styles.block, styles.example)}>
                    <h3 className={styles.blockTitle}>Пример</h3>
                    <p>{summary.example.q}</p>
                    <code>{summary.example.a}</code>
                </section>
            )}
        </div>
    );
};
