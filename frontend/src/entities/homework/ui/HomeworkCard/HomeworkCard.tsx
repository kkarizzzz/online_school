import { AlertTriangle, ArrowRight, CheckCircle2, Clock } from 'lucide-react';
import type { JSX } from 'react';
import { Link } from 'react-router';
import { cn } from '../../../../shared/lib';
import { Button, Card } from '../../../../shared/ui';
import { homeworkRoute } from '../../lib/routes';
import styles from './HomeworkCard.module.css';
import type { HomeworkCardProps } from './HomeworkCard.props';

export const HomeworkCard = ({ homework, className, ...props }: HomeworkCardProps): JSX.Element => {
    const status = homework.status;
    const isOverdue = status === 'overdue';
    const isDone = status === 'done';
    const isChecking = homework.attempt?.status === 'checking';
    const to = homeworkRoute(homework.id);

    const actionLabel = isOverdue
        ? 'Досдать'
        : homework.answeredCount > 0 ? 'Продолжить выполнение' : 'Приступить к выполнению';

    return (
        <Card variant='glass' className={className} {...props}>
            <div className={styles.card}>
                <div className={styles.info}>
                    <h3 className={styles.title}>{homework.title}</h3>
                    <p className={styles.topic}>{[homework.topic, homework.sizeLabel].filter(Boolean).join(' · ')}</p>

                    <div className={styles.meta}>
                        <span className={cn(styles.metaItem, {
                            [styles.metaOverdue]: isOverdue,
                            [styles.metaDone]: isDone
                        })}>
                            {isOverdue ? (
                                <AlertTriangle size={14} />
                            ) : isDone ? (
                                <CheckCircle2 size={14} />
                            ) : (
                                <Clock size={14} />
                            )}
                            {homework.deadlineLabel}
                        </span>
                        <span className={styles.metaItem}>{homework.progressLabel}</span>
                    </div>
                </div>

                {isDone ? (
                    <div className={styles.side}>
                        <span className={styles.doneBadge}>
                            <CheckCircle2 size={16} className={styles.metaDone} />
                            {isChecking ? 'На проверке' : 'Выполнено'}
                        </span>
                        <Button as={Link} to={to} variant='ghost' size='s' radius={18}>
                            Разбор<ArrowRight size={16} />
                        </Button>
                    </div>
                ) : (
                    <Button
                        as={Link}
                        to={to}
                        variant={isOverdue ? 'danger' : 'primary'}
                        radius={18}
                        size='s'
                        className={cn(styles.action, { [styles.btnOverdue]: isOverdue })}
                        arrow="right"
                    >
                        {actionLabel}
                    </Button>
                )}
            </div>
        </Card>
    );
};
