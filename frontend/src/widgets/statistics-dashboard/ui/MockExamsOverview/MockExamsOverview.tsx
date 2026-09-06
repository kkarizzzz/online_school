import type { JSX } from 'react';
import { MockExamCard } from '../../../../entities/mock-exam';
import { Badge, Card } from '../../../../shared/ui';
import styles from './MockExamsOverview.module.css';
import type { MockExamsOverviewProps } from './MockExamsOverview.props';


export const MockExamsOverview = ({ exams, className, ...props }: MockExamsOverviewProps): JSX.Element => {
    const averageScore = exams && exams.length > 0
        ? Math.round(exams.reduce((sum, e) => sum + e.value, 0) / exams.length)
        : 0;

    return (
        <Card variant="glass" className={className} {...props}>
            <div className={styles.header}>
                <h2 className={styles.title}>Пробники</h2>
                
                <Badge variant="soft" size="l">
                    <span>Средний балл</span> 
                    <span className={styles.averageScore} >{averageScore}</span>
                </Badge>
            </div>

            {exams && <div className={styles.grid}>
                {exams.map((exam) => (
                    <MockExamCard key={exam.subject} exam={exam} />
                ))}
            </div>}
        </Card>
    );
};