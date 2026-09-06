import type { JSX } from 'react';
import { MOCK_STAT_METRICS } from '../../../../shared/constants';
import { cn } from '../../../../shared/lib';
// Импортируем нашу новую карточку из shared/ui
import { StatCard } from '../../../../shared/ui';
import styles from './MetricsGrid.module.css';
import type { MetricsGridProps } from './MetricsGrid.props';

export const MetricsGrid = ({ className, ...props }: MetricsGridProps): JSX.Element => {
    return (
        <div className={cn(styles.grid, className)} {...props}>
            {MOCK_STAT_METRICS.map((m) => (
                <StatCard 
                    key={m.label}
                    label={m.label}
                    value={m.value}
                    delta={m.delta}
                    icon={m.icon}
                />
            ))}
        </div>
    );
};