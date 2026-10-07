import { ArrowLeft } from 'lucide-react';
import type { JSX } from 'react';
import { cn } from '../../lib';
import styles from './FeedBar.module.css';
import type { FeedBarProps } from './FeedBar.props';


/** Полоса над лентой заданий: назад, текущий режим и статистика сессии */
export const FeedBar = ({
    backLabel,
    onBack,
    modeIcon,
    modeAccent,
    modeLabel,
    modeTitle,
    stats,
    className,
    ...props
}: FeedBarProps): JSX.Element => (
    <div className={cn('glass', styles.bar, className)} {...props}>
        <button type="button" className={styles.back} onClick={onBack}>
            <ArrowLeft size={18} />{backLabel}
        </button>

        <div className={styles.mode}>
            <span className={cn(styles.modeIcon, { [styles.accent]: modeAccent })}>{modeIcon}</span>
            <span className={styles.modeText}>
                <span className={styles.modeLabel}>{modeLabel}</span>
                <span className={styles.modeTitle}>{modeTitle}</span>
            </span>
        </div>

        <div className={styles.stats}>
            {stats.map(({ icon: Icon, label, value, title, hot, bumpKey }) => (
                <span
                    key={`${label}:${bumpKey ?? 0}`}
                    className={cn(styles.stat, { [styles.hot]: hot, [styles.bump]: !!bumpKey })}
                    title={title}
                >
                    <Icon width={16} height={16} />{label} <b>{value}</b>
                </span>
            ))}
        </div>
    </div>
);
