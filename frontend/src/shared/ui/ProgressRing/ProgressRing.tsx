import type { JSX } from 'react';
import { cn } from '../../../shared/lib';
import styles from './ProgressRing.module.css';
import type { ProgressRingProps } from './ProgressRing.props';


export const ProgressRing = ({ value=0, display, label, size=168, stroke=12, tone='primary', compact, className, ...props }: ProgressRingProps): JSX.Element => {
    
    const radius = (size - stroke) * 0.5;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (value * 0.01) * circumference;
    const circleSize = size * 0.5

    return (
        <div 
            className={cn(styles.wrapper, styles[tone], { [styles.compact]: compact }, className)} 
            style={{ width: size, height: size }} 
            {...props}
        >
            <svg 
                width={size} 
                height={size} 
                className={styles.svg} 
                aria-hidden="true"
            >
                <circle
                    className={styles.circleBg}
                    cx={circleSize}
                    cy={circleSize}
                    r={radius}
                    strokeWidth={stroke}
                />
                <circle
                    className={styles.circleProgress}
                    cx={circleSize}
                    cy={circleSize}
                    r={radius}
                    strokeWidth={stroke}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                />
            </svg>
            <div className={styles.content}>
                <span className={styles.percentage}>{display ?? `${value}%`}</span>
                {label && <span className={styles.label}>{label}</span>}
            </div>
        </div>
    );
};