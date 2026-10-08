import type { JSX } from 'react';
import { useMyStats, weekdayOf } from '../../../../entities/stats';
import { cn } from '../../../../shared/lib';
import styles from './WeeklyActivity.module.css';
import type { WeeklyActivityProps } from './WeeklyActivity.props';


/** Столбики за 7 дней: высота — доля от самого активного дня */
export const WeeklyActivity = ({ 
    data: given, 
    className, 
    ...props 
}: WeeklyActivityProps): JSX.Element => {
    const { data: stats } = useMyStats();
    const week = stats?.week ?? [];
    const top = Math.max(1, ...week.map((d) => d.seconds));
    const data = given ?? week.map((d) => ({ day: weekdayOf(d.day), value: Math.round((d.seconds / top) * 100) }));

    return (
        <div className={cn(styles.wrapper, className)} {...props}>
            <div className={styles.header}>
                <h3 className={styles.title}>Активность за неделю</h3>
                <span className={styles.unit}>ч/день</span>
            </div>
            
            <div className={styles.chart} aria-hidden="true">
                {data.map((d) => (
                    <div key={d.day} className={styles.column}>
                        <div className={styles.track}>
                            <div
                                className={styles.bar}
                                style={{
                                    height: `${d.value}%`,
                                    opacity: 0.35 + (d.value * 0.01) * 0.65,
                                }}
                            />
                        </div>
                        <span className={styles.dayLabel}>{d.day}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};