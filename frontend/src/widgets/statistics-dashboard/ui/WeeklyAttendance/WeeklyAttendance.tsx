import type { JSX } from 'react';
import { toHours, useMyStats, weekdayOf } from '../../../../entities/stats';
import { Card, LineChart } from '../../../../shared/ui';
import styles from './WeeklyAttendance.module.css';
import type { WeeklyAttendanceProps } from './WeeklyAttendance.props';


/** Часы занятий за последние 7 дней: решение задач и уроки */
export const WeeklyAttendance = ({ data, className, ...props }: WeeklyAttendanceProps): JSX.Element => {
    const { data: stats } = useMyStats();
    const points = data ?? (stats?.week ?? []).map((d) => ({ day: weekdayOf(d.day), value: toHours(d.seconds) }));

    return (
        <Card variant="glass" className={className} {...props}>
            <div className={styles.header}>
                <h3 className={styles.title}>Посещаемость за неделю</h3>
                <span className={styles.unit}>часов в день</span>
            </div>

            <LineChart data={points} />
        </Card>
    );
};
