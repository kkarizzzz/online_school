import { ArrowLeft, Play, RotateCcw } from 'lucide-react';
import { useEffect, useRef, useState, type JSX } from 'react';
import { Link, useNavigate } from 'react-router';
import { levelOf, LevelMeter } from '../../../../entities/bank-task';
import { usePracticeNumbers, type Difficulty, type PracticeNumber } from '../../../../entities/practice-task';
import { cn, parseApiError, plural, pluralize } from '../../../../shared/lib';
import { Button } from '../../../../shared/ui';
import { usePersonalStorage, type PersonalSelection } from '../../model/PersonalStorage';
import { ALL_DIFFICULTIES, countTasks, describeDifficulties, PRACTICE_ROUTE } from '../../model/scope';
import styles from './PersonalSetup.module.css';


/**
 * Настройка персонального режима: сложность и номера ЕГЭ с подтемами.
 * Галочка у номера отмечает или снимает все его подтемы. Выбор сохраняется сразу.
 */
export const PersonalSetup = (): JSX.Element => {
    const numbersQuery = usePracticeNumbers();
    const storage = usePersonalStorage();
    const navigate = useNavigate();
    // Профиль ученика к этому моменту уже загружен (RequireAuth), так что хранилище — его
    const [selection, setSelection] = useState<PersonalSelection>(() => storage.read());

    const update = (next: PersonalSelection) => {
        setSelection(next);
        storage.write(next);
    };

    const toggleTopics = (ids: number[], on: boolean) => {
        const rest = selection.topicIds.filter((id) => !ids.includes(id));
        update({ ...selection, topicIds: on ? [...rest, ...ids] : rest });
    };

    const toggleLevel = (d: Difficulty) => {
        const has = selection.difficulties.includes(d);
        if (has && selection.difficulties.length === 1) return; // хотя бы одна сложность остаётся
        update({ ...selection, difficulties: has ? selection.difficulties.filter((x) => x !== d) : [...selection.difficulties, d] });
    };

    if (numbersQuery.isPending) return <p className={styles.empty}>Загружаем номера…</p>;
    if (numbersQuery.isError) {
        return (
            <div className={cn('glass', styles.error)}>
                <p><b>Не удалось загрузить номера.</b> {parseApiError(numbersQuery.error, 'Сервер нарешки недоступен.')}</p>
                <Button variant="outline" size="s" onClick={() => numbersQuery.refetch()}><RotateCcw size={16} />Повторить</Button>
            </div>
        );
    }

    const numbers = numbersQuery.data;
    const picked = selection.topicIds;
    const pickedNumbers = numbers.filter((n) => n.topics.some((t) => picked.includes(t.id))).length;
    const total = countTasks(numbers, picked, selection.difficulties).total;
    const levels = describeDifficulties(selection.difficulties);

    return (
        <section className={styles.setup}>
            <Link to={PRACTICE_ROUTE} className={styles.back}><ArrowLeft size={17} />Нарешка</Link>

            <div className={cn('glass', styles.levels)}>
                <div>
                    <h2 className={styles.levelsTitle} id="practice-levels">Сложность</h2>
                    <p className={styles.levelsHint}>Задания каких уровней будут попадаться в ленте. «Гроб» бывает только во второй части.</p>
                </div>
                <div className={styles.chips} role="group" aria-labelledby="practice-levels">
                    {ALL_DIFFICULTIES.map((d) => (
                        <button
                            key={d}
                            type="button"
                            className={styles.levelChip}
                            aria-pressed={selection.difficulties.includes(d)}
                            onClick={() => toggleLevel(d)}
                        >
                            <LevelMeter level={levelOf(d)} />
                        </button>
                    ))}
                </div>
            </div>

            <h2 className={styles.sectionTitle}>Номера и подтемы</h2>
            <div className={styles.grid}>
                {numbers.map((n) => (
                    <NumberCard key={n.number} number={n} selection={selection} onToggle={toggleTopics} />
                ))}
            </div>

            <div className={styles.bar}>
                <span className={styles.barInfo}>
                    {picked.length ? (
                        <>
                            Выбрано <b>{picked.length}</b> {plural(picked.length, 'подтема', 'подтемы', 'подтем')} из{' '}
                            <b>{pickedNumbers}</b> {plural(pickedNumbers, 'номера', 'номеров', 'номеров')}
                            {' · '}{pluralize(total, 'задание', 'задания', 'заданий')}{levels && ` · ${levels}`}
                            {!total && <> — <b>нет заданий</b> такой сложности</>}
                        </>
                    ) : 'Ничего не выбрано — отметьте номера или подтемы'}
                </span>
                {picked.length > 0 && (
                    <Button variant="ghost-secondary" size="m" onClick={() => update({ ...selection, topicIds: [] })}>Очистить</Button>
                )}
                <Button size="m" disabled={!total} onClick={() => navigate(`${PRACTICE_ROUTE}?mode=personal`)}>
                    <Play size={18} />Решать
                </Button>
            </div>
        </section>
    );
};


interface NumberCardProps {
    number: PracticeNumber;
    selection: PersonalSelection;
    onToggle: (ids: number[], on: boolean) => void;
}

const NumberCard = ({ number, selection, onToggle }: NumberCardProps): JSX.Element => {
    const ids = number.topics.map((t) => t.id);
    const count = ids.filter((id) => selection.topicIds.includes(id)).length;
    const all = count === ids.length;
    const boxRef = useRef<HTMLInputElement>(null);
    const tasks = (topicIds: number[]) => countTasks([number], topicIds, selection.difficulties).total;

    // «Частично» у чекбокса ставится только из JS
    useEffect(() => {
        if (boxRef.current) boxRef.current.indeterminate = count > 0 && !all;
    }, [count, all]);

    const meta = all ? 'Весь номер'
        : count ? `Выбрано ${count} из ${ids.length}`
        : `${pluralize(ids.length, 'подтема', 'подтемы', 'подтем')} · ${pluralize(tasks(ids), 'задание', 'задания', 'заданий')}`;

    return (
        <article className={cn('glass', styles.number, { [styles.picked]: count > 0 })}>
            <label className={styles.numberHead}>
                <input ref={boxRef} type="checkbox" className={styles.check} checked={all} onChange={() => onToggle(ids, !all)} />
                <span className={styles.badge}>{number.number}</span>
                <span className={styles.numberText}>
                    <span className={styles.numberTitle}>{number.title ?? `Задание №${number.number}`}</span>
                    <span className={styles.numberMeta}>{meta}</span>
                </span>
            </label>
            <ul className={styles.topics}>
                {number.topics.map((t) => {
                    const on = selection.topicIds.includes(t.id);
                    return (
                        <li key={t.id}>
                            <label className={cn(styles.topic, { [styles.selected]: on })}>
                                <input type="checkbox" className={styles.check} checked={on} onChange={() => onToggle([t.id], !on)} />
                                <span className={styles.topicName}>{t.name}</span>
                                <span className={styles.topicCount}>{tasks([t.id])}</span>
                            </label>
                        </li>
                    );
                })}
            </ul>
        </article>
    );
};
