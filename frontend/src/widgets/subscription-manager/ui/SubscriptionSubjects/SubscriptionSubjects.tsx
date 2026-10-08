import type { JSX } from 'react';
import { useUserProfile } from '../../../../entities/user';
import { SUBJECTS } from '../../../../shared/constants';
import { cn, pluralize } from '../../../../shared/lib';
import { Card } from '../../../../shared/ui';
import styles from './SubscriptionSubjects.module.css';
import type { SubscriptionSubjectsProps } from './SubscriptionSubjects.props';


/** Предметы, к которым у ученика есть доступ */
export const SubscriptionSubjects = ({ className, ...props }: SubscriptionSubjectsProps): JSX.Element => {
    const { data: profile } = useUserProfile();
    const pickedSubjects = (profile?.subjects ?? []).map((s) => s.subject);

    return (
        <Card variant="glass" className={className} {...props}>
            <div className={styles.header}>
                <h2 className={styles.title}>Мои предметы</h2>
                <p className={styles.subtitle}>
                    {pickedSubjects.length
                        ? `Подключено ${pluralize(pickedSubjects.length, 'предмет', 'предмета', 'предметов')}`
                        : 'Предметы подключаются вместе с тарифом'}
                </p>
            </div>

            <div className={styles.grid}>
                {SUBJECTS.map((s) => {
                    const isPicked = pickedSubjects.includes(s.id);
                    const Icon = s.icon; 
                    
                    return (
                        <div
                            key={s.id}
                            className={cn(styles.card, {
                                [styles.active]: isPicked,
                                [styles.inactive]: !isPicked
                            })}
                        >
                            <div className={styles.iconWrap}>
                                <Icon size={18} />
                            </div>
                            <span className={styles.subjectName}>{s.label}</span>
                        </div>
                    );
                })}
            </div>
        </Card>
    );
};
