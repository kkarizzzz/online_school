import type { JSX } from 'react';
import { cn } from '../../../../shared/lib';
import { ProgressBar } from '../../../../shared/ui';
import styles from './TaskProgress.module.css';
import type { TaskProgressProps } from './TaskProgress.props';


export const TaskProgress = ({ solved, total, className, ...props }: TaskProgressProps): JSX.Element => {
    return (
        <div className={cn(styles.progressRow, className)} {...props}>
            <ProgressBar value={solved} max={total} className={styles.progressBarWidth} />

            <span className={styles.progressText}>
                {solved}/{total}
            </span>
        </div>
    );
};