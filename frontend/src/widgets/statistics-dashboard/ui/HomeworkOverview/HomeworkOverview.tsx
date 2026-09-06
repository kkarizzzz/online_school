import type { JSX } from 'react';
import { cn } from '../../../../shared/lib';
import { Card, ProgressRing } from '../../../../shared/ui';
import styles from './HomeworkOverview.module.css';
import type { HomeworkOverviewProps } from './HomeworkOverview.props';

export const HomeworkOverview = ({ className, ...props }: HomeworkOverviewProps): JSX.Element => {
    // В будущем эти данные будут приходить из пропсов или API
    const submitted = 34;
    const overdue = 5;
    const total = submitted + overdue;
    
    const pct = total > 0 ? Math.round((submitted / total) * 100) : 0;

    return (
        <Card variant="glass" className={className} {...props}>
            <h2 className={styles.title}>Домашние задания</h2>

            <div className={styles.content}>
                <ProgressRing
                    value={pct}
                    label="сдано вовремя"
                    size={200}
                    stroke={16}
                />

                <div className={styles.legend}>
                    <div className={styles.legendItem}>
                        <span className={cn(styles.legendDot, styles.colorPrimary)}/>
                        <span className={styles.legendText}>Сдано — {submitted}</span>
                    </div>
                    <div className={styles.legendItem}>
                        <span className={styles.legendDot}/>
                        <span className={styles.legendText}>Просрочено — {overdue}</span>
                    </div>
                </div>
            </div>
        </Card>
    );
};