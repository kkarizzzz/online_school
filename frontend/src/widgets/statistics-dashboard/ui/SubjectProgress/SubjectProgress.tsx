import type { JSX } from 'react';
import { useMyStats } from '../../../../entities/stats';
import { SUBJECTS } from '../../../../shared/constants';
import { Card, ProgressBar } from '../../../../shared/ui';
import styles from './SubjectProgress.module.css';
import type { SubjectProgressProps } from './SubjectProgress.props';

const labelOf = (subject: string): string => SUBJECTS.find((s) => s.id === subject)?.label ?? subject;


/** Решено заданий из банка по каждому предмету, где есть задания */
export const SubjectProgress = ({ className, ...props }: SubjectProgressProps): JSX.Element => {
    const { data: stats } = useMyStats();
    const subjects = stats?.subjects ?? [];

    return (
        <Card variant="glass" className={className} {...props}>
            <h2 className={styles.title}>Задачи по предметам</h2>

            <div className={styles.list}>
                {subjects.length === 0 && <p className={styles.counter}>Заданий пока нет.</p>}
                {subjects.map((s) => (
                    <div key={s.subject}>
                        <div className={styles.itemHeader}>
                            <span className={styles.subjectName}>{labelOf(s.subject)}</span>
                            <span className={styles.counter}>{s.tasksSolved} / {s.taskCount}</span>
                        </div>

                        <ProgressBar value={s.tasksSolved} max={s.taskCount} />
                    </div>
                ))}
            </div>
        </Card>
    );
};
