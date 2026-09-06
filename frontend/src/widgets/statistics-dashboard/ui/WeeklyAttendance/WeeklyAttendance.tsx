import type { JSX } from 'react';
import { MOCK_STATS_ATTENDANCE } from '../../../../shared/constants';
import { Card, LineChart } from '../../../../shared/ui';
import styles from './WeeklyAttendance.module.css';
import type { WeeklyAttendanceProps } from './WeeklyAttendance.props';

export const WeeklyAttendance = ({ data=MOCK_STATS_ATTENDANCE, className, ...props }: WeeklyAttendanceProps): JSX.Element => {
    return (
        <Card variant="glass" className={className} {...props}>
            <div className={styles.header}>
                <h3 className={styles.title}>Посещаемость за неделю</h3>
                <span className={styles.unit}>часов в день</span>
            </div>
            
            <LineChart data={data} />
        </Card>
    );
};