import { Award } from 'lucide-react';
import type { JSX } from 'react';
import { AchievementBadge, ACHIEVEMENTS_DICT } from '../../../../entities/achievement';
import { Card } from '../../../../shared/ui';
import styles from './AchievementsOverview.module.css';
import type { AchievementsOverviewProps } from './AchievementsOverview.props';

export const AchievementsOverview = ({ 
    unlockedIds=[], 
    className, 
    ...props 
}: AchievementsOverviewProps): JSX.Element => {
    
    const unlockedCount = unlockedIds.length;
    const totalCount = ACHIEVEMENTS_DICT.length;

    return (
        <Card variant="glass" className={className} {...props}>
            <div className={styles.header}>
                <div className={styles.titleInfo}>
                    <h2 className={styles.title}>Достижения</h2>
                    <p className={styles.subtitle}>
                        Открыто {unlockedCount} из {totalCount} медалей
                    </p>
                </div>
                <Award size={24} className={styles.headerIcon} />
            </div>

            <div className={styles.grid}>
                {ACHIEVEMENTS_DICT.map((achievement) => {
                    const isUnlocked = unlockedIds.includes(achievement.id);
                    
                    return (
                        <AchievementBadge 
                            key={achievement.id} 
                            achievement={achievement} 
                            unlocked={isUnlocked} 
                        />
                    );
                })}
            </div>
        </Card>
    );
};