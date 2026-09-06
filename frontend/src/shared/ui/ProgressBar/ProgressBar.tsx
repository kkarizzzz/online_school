import type { JSX } from 'react';
import { cn } from '../../lib';
import styles from './ProgressBar.module.css';
import type { ProgressBarProps } from './ProgressBar.props';

export const ProgressBar = ({ value, max=100, className, ...props }: ProgressBarProps): JSX.Element => {
    
    const pct = max > 0 ? Math.max(0, Math.min(100, Math.round((value / max) * 100))) : 0;

    return (
        <div 
            className={cn(styles.track, className)} 
            role="progressbar" 
            aria-valuenow={value} 
            aria-valuemax={max}
            {...props}
        >
            <div className={styles.fill} style={{ width: `${pct}%` }} />
        </div>
    );
};