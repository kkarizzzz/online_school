import type { JSX } from 'react';
import { cn } from '../../../../shared/lib';
import styles from './AchievementBadge.module.css';
import type { AchievementBadgeProps } from './AchievementBadge.props';

export const AchievementBadge = ({ achievement, unlocked, className, ...props }: AchievementBadgeProps): JSX.Element => {
    const Icon = achievement.icon;

    return (
        <div 
            className={cn(
                styles.badge,  
                {
                    [styles.unlocked]: unlocked,
                    [styles.locked]: !unlocked
                },
                className
            )} 
            title={!unlocked ? 'Достижение пока не получено' : undefined}
            {...props}
        >
            <div className={styles.iconWrap}>
                <Icon width={24} height={24} strokeWidth={1.5} />
            </div>
            <div>
                <h3 className={styles.title}>{achievement.title}</h3>
                <p className={styles.desc}>{achievement.description}</p>
            </div>
        </div>
    );
};