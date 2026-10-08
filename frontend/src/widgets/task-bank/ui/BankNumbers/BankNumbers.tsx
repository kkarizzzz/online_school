import { useCallback, type JSX } from 'react';
import { useSearchParams } from 'react-router';
import { useBankNumbers } from '../../../../entities/bank-task';
import { pluralize } from '../../../../shared/lib';
import { TopicsDrawer } from '../TopicsDrawer/TopicsDrawer';
import styles from './BankNumbers.module.css';

const PARTS = [
    { part: 1, title: 'Часть 1', note: 'краткий ответ · задания 1–12' },
    { part: 2, title: 'Часть 2', note: 'развёрнутый ответ · задания 13–19' },
] as const;


/**
 * Номера ЕГЭ 1–19 по частям. Клик по номеру открывает панель тем справа.
 * Открытый номер — в адресе (?n=6): так возвращает ссылка «Банк заданий» со страницы номера.
 */
export const BankNumbers = (): JSX.Element => {
    const { data: numbers, isError } = useBankNumbers();
    const [params, setParams] = useSearchParams();
    const open = numbers?.find((b) => b.n === Number(params.get('n'))) ?? null;

    const close = useCallback(() => setParams({}, { replace: true }), [setParams]);

    if (isError) return <p className={styles.empty}>Не удалось загрузить банк заданий. Обновите страницу.</p>;
    if (!numbers) return <p className={styles.empty}>Загружаем банк заданий…</p>;

    return (
        <>
            {PARTS.map(({ part, title, note }) => (
                <section key={part} className={styles.part}>
                    <h2 className={styles.partTitle}>{title}<span>{note}</span></h2>
                    <ul className={styles.numbers}>
                        {numbers.filter((b) => b.part === part).map((b) => (
                            <li key={b.n}>
                                <button
                                    type="button"
                                    className={styles.card}
                                    aria-haspopup="dialog"
                                    onClick={() => setParams({ n: String(b.n) }, { replace: true })}
                                >
                                    <span className={styles.badge}>{b.n}</span>
                                    <span className={styles.main}>
                                        <span className={styles.title}>{b.title}</span>
                                        <span className={styles.meta}>
                                            {pluralize(b.topics.length, 'тема', 'темы', 'тем')} · {pluralize(b.taskCount, 'задание', 'задания', 'заданий')}
                                            {b.solvedCount > 0 && ` · решено ${b.solvedCount}`}
                                        </span>
                                    </span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </section>
            ))}

            <TopicsDrawer key={open?.n ?? 0} number={open} onClose={close} />
        </>
    );
};
