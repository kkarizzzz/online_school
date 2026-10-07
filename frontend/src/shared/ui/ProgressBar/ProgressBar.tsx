import type { CSSProperties, JSX } from 'react';
import { cn } from '../../lib';
import styles from './ProgressBar.module.css';
import type { ProgressBarProps } from './ProgressBar.props';

const TONES: Record<string, string> = {
    primary: 'var(--primary)',
    done: 'var(--done)',
};

export const ProgressBar = ({ value, max=100, tone='primary', size='m', className, style, ...props }: ProgressBarProps): JSX.Element => {
    
    const pct = max > 0 ? Math.max(0, Math.min(100, Math.round((value / max) * 100))) : 0;
    const barStyle = { '--bar-color': TONES[tone] ?? tone, ...style } as CSSProperties;

    return (
        <div 
            className={cn(styles.track, styles[size], className)} 
            role="progressbar" 
            aria-valuenow={value} 
            aria-valuemax={max}
            style={barStyle}
            {...props}
        >
            <div className={styles.fill} style={{ width: `${pct}%` }} />
        </div>
    );
};
