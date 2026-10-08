import { Hourglass } from 'lucide-react';
import { useEffect, useRef, useState, type JSX } from 'react';
import { cn, formatClock } from '../../../../shared/lib';
import styles from '../AttemptSolver/AttemptSolver.module.css';

const WARN_SEC = 15 * 60;
const DANGER_SEC = 5 * 60;

interface CountdownTimerProps {
    /** Конец, мс по часам браузера */
    until: number;
    /** Время вышло — вызывается один раз */
    onExpire: () => void;
    className?: string;
}


/** Обратный отсчёт варианта: за 15 минут до конца желтеет, за 5 — краснеет */
export const CountdownTimer = ({ until, onExpire, className }: CountdownTimerProps): JSX.Element => {
    const [now, setNow] = useState(() => Date.now());
    const expired = useRef(false);
    const left = Math.max(0, (until - now) / 1000);

    useEffect(() => {
        const id = setInterval(() => setNow(Date.now()), 1000);
        return () => clearInterval(id);
    }, []);

    useEffect(() => {
        if (left > 0 || expired.current) return;
        expired.current = true;
        onExpire();
    }, [left, onExpire]);

    return (
        <div
            className={cn(styles.chip, className, {
                [styles.chipWarn]: left <= WARN_SEC && left > DANGER_SEC,
                [styles.chipDanger]: left <= DANGER_SEC,
            })}
            title="Сколько осталось до конца"
        >
            <Hourglass className={styles.chipIcon} size={20} />
            <span className={styles.chipText}>
                <b>{formatClock(left)}</b>
                <span>осталось</span>
            </span>
        </div>
    );
};
