import { BookOpenCheck, CheckCircle2, Clock, Flame } from 'lucide-react';
import type { JSX } from 'react';
import { toHours, useMyStats, weekTotal } from '../../../../entities/stats';
import { cn, plural } from '../../../../shared/lib';
import { StatCard } from '../../../../shared/ui';
import styles from './MetricsGrid.module.css';
import type { MetricsGridProps } from './MetricsGrid.props';

const delta = (n: number, unit = ''): string => (n > 0 ? `+${n.toLocaleString('ru-RU')}${unit} за неделю` : 'за неделю — пока ничего');


export const MetricsGrid = ({ className, ...props }: MetricsGridProps): JSX.Element => {
    const { data: stats } = useMyStats();
    const totals = stats?.totals;
    const week = stats?.week ?? [];

    const metrics = [
        {
            icon: Clock,
            label: 'Часов на платформе',
            value: totals ? toHours(totals.seconds).toLocaleString('ru-RU') : '—',
            delta: delta(toHours(weekTotal(week, 'seconds')), ' ч'),
        },
        {
            icon: BookOpenCheck,
            label: 'Пройдено уроков',
            value: totals?.lessonsDone.toLocaleString('ru-RU') ?? '—',
            delta: delta(weekTotal(week, 'lessonsDone')),
        },
        {
            icon: CheckCircle2,
            label: 'Решено задач',
            value: totals?.tasksSolved.toLocaleString('ru-RU') ?? '—',
            delta: delta(weekTotal(week, 'correct')),
        },
        {
            icon: Flame,
            label: 'Серия дней',
            value: stats?.streak ?? '—',
            delta: stats?.streak ? `${plural(stats.streak, 'день', 'дня', 'дней')} подряд` : 'Начните сегодня',
        },
    ];

    return (
        <div className={cn(styles.grid, className)} {...props}>
            {metrics.map((m) => (
                <StatCard key={m.label} label={m.label} value={m.value} delta={m.delta} icon={m.icon} />
            ))}
        </div>
    );
};
