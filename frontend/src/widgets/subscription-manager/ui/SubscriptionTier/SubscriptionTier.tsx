import { Crown } from 'lucide-react';
import type { JSX } from 'react';
import { Link } from 'react-router';
import { useUserProfile } from '../../../../entities/user';
import { PRICING_PAGE_TIERS } from '../../../../shared/constants';
import { cn, formatDayMonth } from '../../../../shared/lib';
import { Badge, Button, Card } from '../../../../shared/ui';
import { TierCard } from '../TierCard/TierCard';
import styles from './SubscriptionTier.module.css';
import type { SubscriptionTierProps } from './SubscriptionTier.props';

const capitalize = (s: string): string => s.charAt(0) + s.slice(1).toLowerCase();


/** Тарифы школы и срок доступа ученика. Покупка — на странице тарифов */
export const SubscriptionTier = ({ className, ...props }: SubscriptionTierProps): JSX.Element => {
    const { data: profile } = useUserProfile();
    const until = profile?.subjects
        .map((s) => s.accessUntil)
        .filter((d): d is string => d !== null)
        .sort()
        .at(-1);
    const status = !profile?.subjects.length
        ? 'Доступ не подключён'
        : until ? `Доступ до ${formatDayMonth(until)}` : 'Доступ без срока';

    return (
        <Card variant="glass" className={cn(className)} {...props}>
            <div className={styles.header}>
                <div className={styles.titleWrap}>
                    <Crown size={20} className={styles.titleIcon} />
                    <h2 className={styles.title}>Тарифы</h2>
                </div>
                
                <Badge variant="soft" size="l" className={styles.statusBadge}>{status}</Badge>
            </div>

            <div className={styles.grid}>
                {PRICING_PAGE_TIERS.map((t) => (
                    <TierCard
                        key={t.tier}
                        name={capitalize(t.name)}
                        price={`${Number(t.price).toLocaleString('ru-RU')} ${t.unit}`}
                        features={t.sub}
                        isActive={false}
                    />
                ))}
            </div>

            <Button as={Link} to="/pricing" size="s" radius={18} className={styles.actionBtn}>
                Сравнить тарифы
            </Button>
        </Card>
    );
};
