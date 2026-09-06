import type { JSX } from 'react';
import { Card, ProgressRing } from '../../../../shared/ui';
import { WeeklyActivity } from '../WeeklyActivity/WeeklyActivity';
import { WidgetMetric } from '../WidgetMetric/WidgetMetric';
import styles from './StatsPanel.module.css';
import type { StatsPanelProps } from './StatsPanel.props';


export const StatsPanel = ({ title, subject="Предмет", children, className, ...props }: StatsPanelProps): JSX.Element => {
    return (
        <Card variant="glass" className={className} {...props}>
            <div>
                <h2 className={styles.headerTitle}>{title}</h2>
                <p className={styles.headerSubtitle}>{subject} &middot; ЕГЭ Профиль</p>
            </div>

            <div className={styles.progressSection}>
                <ProgressRing value={77} label='курса пройдено'/>
                <p className={styles.quote}>
                    {children}
                </p>
            </div>

            <WidgetMetric />

            <WeeklyActivity />
        </Card>
    );
};