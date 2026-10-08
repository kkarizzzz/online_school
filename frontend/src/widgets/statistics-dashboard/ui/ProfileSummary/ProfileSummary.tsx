import { TrendingUp } from 'lucide-react';
import type { JSX } from 'react';
import { useMyStats } from '../../../../entities/stats';
import { useUser, useUserProfile } from '../../../../entities/user';
import { cn, formatLongDate } from '../../../../shared/lib';
import { Avatar, Badge, Card } from '../../../../shared/ui';
import styles from './ProfileSummary.module.css';
import type { ProfileSummaryProps } from './ProfileSummary.props';


export const ProfileSummary = ({ className, ...props }: ProfileSummaryProps): JSX.Element => {
    const { data: user } = useUser();
    const { data: profile } = useUserProfile();
    const { data: stats } = useMyStats();

    const fullName = user ? `${user.firstName} ${user.lastName || ''}`.trim() : '';
    const meta = [
        profile?.grade && `${profile.grade} класс`,
        profile?.examYear ? `ЕГЭ ${profile.examYear}` : 'ЕГЭ Профиль',
        profile && `с ${formatLongDate(profile.createdAt)}`,
    ].filter(Boolean).join(' · ');

    return (
        <Card variant="glass" className={cn(styles.card, className)} {...props}>
            <div className={styles.userInfo}>
                <Avatar 
                    firstName={user?.firstName} 
                    lastName={user?.lastName} 
                    size={56} 
                    variant='rounded'
                />
                
                <div className={styles.details}>
                    <h2 className={styles.name}>{fullName}</h2>
                    <p className={styles.meta}>{meta}</p>
                </div>
            </div>

            {stats?.rankPercent != null && (
                <Badge variant="soft" size="l">
                    <TrendingUp size={16} />
                    <span>Рейтинг: Топ {stats.rankPercent}%</span>
                </Badge>
            )}
        </Card>
    );
};