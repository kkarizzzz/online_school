import { Flame, Target, Trophy } from 'lucide-react';
import type { JSX } from 'react';
import { useMyStats, weekTotal } from '../../../../entities/stats';
import { cn, pluralize } from '../../../../shared/lib';
import type { StatItem } from '../../model/types';
import styles from './WidgetMetric.module.css';
import type { WidgetMetricProps } from './WidgetMetric.props';


export const WidgetMetric = ({ 
    stats: given, 
    className, 
    ...props 
}: WidgetMetricProps): JSX.Element => {
    const { data } = useMyStats();
    const stats: StatItem[] = given ?? [
        { id: 'streak', icon: Flame, label: 'Серия', value: pluralize(data?.streak ?? 0, 'день', 'дня', 'дней') },
        { id: 'tasks', icon: Target, label: 'Задач за неделю', value: weekTotal(data?.week ?? [], 'answered') },
        { id: 'rating', icon: Trophy, label: 'Рейтинг', value: data?.rankPercent != null ? `Топ ${data.rankPercent}%` : '—' },
    ];
    
    return (
        <div className={cn(styles.grid, className)} {...props}>
            {stats.map((stat) => {
                const Icon = stat.icon;
                return (
                    <div key={stat.id} className={styles.item}>
                        <Icon width={16} height={16} className={styles.icon} />
                        <span className={styles.value}>{stat.value}</span>
                        <span className={styles.label}>{stat.label}</span>
                    </div>
                );
            })}
        </div>
    );
};
