import { Timer } from 'lucide-react';
import { useEffect, useState, type JSX } from 'react';
import { cn, formatClock } from '../../../../shared/lib';
import styles from '../AttemptSolver/AttemptSolver.module.css';
import type { ElapsedTimerProps } from './ElapsedTimer.props';


/** Секундомер «в работе» — тикает сам, чтобы не перерисовывать всю страницу раз в секунду */
export const ElapsedTimer = ({ since, className }: ElapsedTimerProps): JSX.Element => {
    const [now, setNow] = useState(() => Date.now());

    useEffect(() => {
        const id = setInterval(() => setNow(Date.now()), 1000);
        return () => clearInterval(id);
    }, []);

    return (
        <div className={cn(styles.chip, className)} title="Сколько времени идёт выполнение">
            <Timer className={styles.chipIcon} size={20} />
            <span className={styles.chipText}>
                <b>{formatClock((now - since) / 1000)}</b>
                <span>в работе</span>
            </span>
        </div>
    );
};
