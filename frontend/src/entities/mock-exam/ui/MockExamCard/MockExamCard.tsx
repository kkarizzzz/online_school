import type { JSX } from 'react';
import { cn } from '../../../../shared/lib';
import { Card, ProgressBar } from '../../../../shared/ui';
import styles from './MockExamCard.module.css';
import type { MockExamCardProps } from './MockExamCard.props';

export const MockExamCard = ({ exam, className, ...props }: MockExamCardProps): JSX.Element => {
    return (
        <Card hoverable className={cn(styles.card, className)} {...props}>
            <span className={styles.subjectName}>{exam.subject}</span>
            <div className={styles.scoreRow}>
                {exam.value}
                <span className={styles.maxScore}> / {exam.max}</span>
            </div>
            
            <ProgressBar value={exam.value} max={exam.max} />
        </Card>
    );
};