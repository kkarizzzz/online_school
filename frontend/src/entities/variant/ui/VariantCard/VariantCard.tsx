import { CheckCircle2, Clock, Hourglass, Play, RotateCcw, Users } from 'lucide-react';
import type { JSX } from 'react';
import { Link } from 'react-router';
import { scoreLabel } from '../../../attempt';
import { LevelMeter, levelOf } from '../../../bank-task';
import { cn, formatDayMonth, formatSpentTime, pluralize } from '../../../../shared/lib';
import { Badge, Button, Card, Divider } from '../../../../shared/ui';
import { variantAttemptRoute, variantSolveRoute } from '../../lib/routes';
import type { Variant } from '../../model/types';
import styles from './VariantCard.module.css';
import type { VariantCardProps } from './VariantCard.props';

/** «Задания №3, 14» или «Как на ЕГЭ» */
const formatLabel = (v: Variant): string =>
    v.isStandard ? 'Как на ЕГЭ' : `Задания №${v.numbers.join(', ')}`;


export const VariantCard = ({ variant, className, ...props }: VariantCardProps): JSX.Element => {
    const last = variant.lastAttempt;
    const inProgress = variant.inProgressAttemptId !== null;
    const meta = [
        variant.publisher,
        formatLabel(variant),
        pluralize(variant.taskCount, 'задание', 'задания', 'заданий'),
        variant.timeLimitSec ? formatSpentTime(variant.timeLimitSec) : 'без ограничения времени',
    ].filter(Boolean).join(' · ');

    return (
        <Card variant="glass" className={cn(styles.card, { [styles.coffin]: variant.difficulty === 4 }, className)} {...props}>
            <div className={styles.header}>
                <div>
                    <h3 className={styles.title}>{variant.title}</h3>
                    <p className={styles.meta}>{meta}</p>
                </div>
                <Badge variant={variant.isStandard ? 'primary' : 'outline'} size="s" className={styles.badge}>
                    {variant.isStandard ? 'Вариант' : 'Отработка'}
                </Badge>
            </div>

            <div className={styles.facts}>
                {variant.difficulty && <LevelMeter level={levelOf(variant.difficulty)} />}
                <span title="Сколько учеников сдали вариант">
                    <Users size={13} />{variant.solvedStudents.toLocaleString('ru-RU')}
                </span>
                {variant.timeLimitSec && <span><Hourglass size={13} />на время</span>}
            </div>

            <Divider />

            <div className={styles.footer}>
                <span className={cn(styles.status, { [styles.statusDone]: last })}>
                    {last ? <CheckCircle2 size={14} /> : <Clock size={14} />}
                    {inProgress
                        ? 'Начат, не сдан'
                        : last ? `${scoreLabel(last)} · ${formatDayMonth(last.submittedAt ?? last.startedAt)}` : 'Не решён'}
                </span>

                <div className={styles.actions}>
                    {last && !inProgress && (
                        <Button as={Link} to={variantAttemptRoute(last.id)} variant="outline" size="xs" radius={16} disableJump>
                            Разбор
                        </Button>
                    )}
                    <Button
                        as={Link}
                        to={variantSolveRoute(variant.id)}
                        variant={last && !inProgress ? 'ghost' : 'primary'}
                        size="xs"
                        radius={16}
                        disableJump
                    >
                        {inProgress ? <><Play size={14} />Продолжить</> : last ? <><RotateCcw size={14} />Ещё раз</> : 'Начать'}
                    </Button>
                </div>
            </div>
        </Card>
    );
};
