import type { JSX } from 'react';
import { useMyStats } from '../../../../entities/stats';
import { cn, percent } from '../../../../shared/lib';
import { Card, ProgressRing } from '../../../../shared/ui';
import styles from './HomeworkOverview.module.css';
import type { HomeworkOverviewProps } from './HomeworkOverview.props';


/** Доля ДЗ, сданных вовремя, среди сданных и просроченных */
export const HomeworkOverview = ({ className, ...props }: HomeworkOverviewProps): JSX.Element => {
    const { data: stats } = useMyStats();
    const hw = stats?.homework;
    const submitted = hw?.done ?? 0;
    const overdue = hw?.overdue ?? 0;
    const onTime = submitted - (hw?.late ?? 0);

    return (
        <Card variant="glass" className={className} {...props}>
            <h2 className={styles.title}>Домашние задания</h2>

            <div className={styles.content}>
                <ProgressRing
                    value={percent(onTime, submitted + overdue)}
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
                    {hw && hw.current > 0 && (
                        <div className={styles.legendItem}>
                            <span className={styles.legendDot}/>
                            <span className={styles.legendText}>Ждут выполнения — {hw.current}</span>
                        </div>
                    )}
                </div>
            </div>
        </Card>
    );
};
