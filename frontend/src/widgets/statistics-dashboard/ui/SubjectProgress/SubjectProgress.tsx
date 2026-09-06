import type { JSX } from 'react';
import { MOCK_SUBJECT_TASKS } from '../../../../shared/constants';
import { Card, ProgressBar } from '../../../../shared/ui';
import styles from './SubjectProgress.module.css';
import type { SubjectProgressProps } from './SubjectProgress.props';

export const SubjectProgress = ({ className, ...props }: SubjectProgressProps): JSX.Element => {
    return (
        <Card variant="glass" className={className} {...props}>
            <h2 className={styles.title}>Задачи по предметам</h2>
            
            <div className={styles.list}>
                {MOCK_SUBJECT_TASKS.map((s) => (
                    <div key={s.subject}>
                        <div className={styles.itemHeader}>
                            <span className={styles.subjectName}>{s.subject}</span>
                            <span className={styles.counter}>{s.value} / {s.max}</span>
                        </div>

                        <ProgressBar value={s.value} max={s.max} />
                    </div>
                ))}
            </div>
        </Card>
    );
};