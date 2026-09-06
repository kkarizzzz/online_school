import type { JSX } from 'react';
import { Card } from '../Card/Card';
import styles from './StatCard.module.css';
import type { StatCardProps } from './StatCard.props';


export const StatCard = ({ label, value, delta, icon: Icon, className, ...props }: StatCardProps): JSX.Element => {
    return (
        <Card variant="glass" className={className} {...props}>
            <div className={styles.iconWrap}>
                <Icon width={18} height={18} strokeWidth={2} />
            </div>
            
            <div className={styles.info}>
                <span className={styles.value}>{value}</span>
                <span className={styles.label}>{label}</span>
            </div>
            
            {delta && <span className={styles.delta}>{delta}</span>}
        </Card>
    );
};